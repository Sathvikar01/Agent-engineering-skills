# Redesigning the Refund Agent's Trace for Auditability

## The problem

A one-line summary can only show what the summarizer thought mattered. An auditor asking "why was this refund approved?" usually needs exactly the detail a summary drops:

- the order-lookup tool said `status: "delivered"`, but the summary said "order found"
- the refund policy tool result was cut off during context assembly, so the model never saw the 30-day clause
- the model proposed `amount: 149.00` against an order total of `14.90`
- a retry ran the refund tool a second time

So the redesign keeps **two layers**:

1. **A structured event stream**, small and always on. It holds IDs, versions, decisions, digests and outcomes, and you use it to find and join things.
2. **Raw evidence artifacts**: the exact assembled model input, the raw model output, and the raw tool requests and responses. These are redacted *before they are written*, stored under restricted access, and linked to events by ID.

Card data is handled in both layers by a redaction step that runs before persistence, plus a manifest saying what was redacted. The auditor gets "exactly what the model saw, except at these marked spans, which held a card number with token X."

---

## 1. Identity and ordering

Every record carries these fields:

| Field | Purpose |
|---|---|
| `run_id` | One per customer refund case. Survives retries and resume. |
| `operation_id` | One logical step, e.g. "issue refund for order 8812". Stays the same across retries. |
| `attempt_id` | One per physical try of that step. This is how you see the duplicate refund. |
| `span_id` / `parent_span_id` | Nesting of model calls, tools and any sub-workers. |
| `seq` | Monotonic sequence number within the run. This is the causal order; wall-clock timestamps alone don't establish it. |
| `ts` | Event time, for humans and latency. |
| `state_version` | Version of the case/refund record before and after any state change. |
| `correlation_id` | Passed to the payment and refund provider as an idempotency key, so their records can be joined to ours. |

## 2. Events to emit

Each event is a structured record. Large payloads appear only as an `artifact_ref`.

| Event | Key fields |
|---|---|
| `request.accepted` | channel, customer pseudonym, tenant, `authorized_scope` (e.g. `refund:max=200 USD`), case ID |
| `context.assembled` | `artifact_ref` to the exact model input; list of included items with `{source_event_id, evidence_id, tokens, truncated: bool}`; **dropped/truncated items listed explicitly**; prompt/template version; retrieval index version |
| `model.call` | model ID and version, sampling params, prompt version, tool-schema version, token usage (or `unavailable`), latency, `finish_reason` (stop / length / refusal / tool_use / content_filter) |
| `model.output` | `artifact_ref` to the raw response; parsed tool calls; parse status (`ok` / `malformed` / `truncated` / `refusal`), each kept as a separate status |
| `proposal.validated` | the proposed action (e.g. `refund {order_id, amount, currency, reason_code}`), schema validation result, **normalized action digest** |
| `policy.decision` | policy version, rule IDs evaluated, result (`allow` / `deny` / `needs_approval`), inputs the rule actually used (order total, days since delivery, prior refunds), short reason |
| `approval.requested` / `approval.decided` | approver principal, what they were shown (artifact_ref), decision, timestamp. Anyone overriding the policy result is recorded as such. |
| `tool.attempt` | tool name and version, `operation_id`, `attempt_id`, `artifact_ref` to the redacted raw request, args digest, idempotency key |
| `tool.result` | `artifact_ref` to the redacted raw response, HTTP/status code, classification (`success` / `business_error` / `transport_error` / **`unknown_effect`** e.g. a timeout after send), provider receipt ID, latency |
| `state.transition` | entity, `from_version` → `to_version`, fields changed, triggering event ID |
| `retry` / `failure` | cause, attempt number, whether retry policy allowed it |
| `evaluator.outcome` | (if you run online checks) evaluator version, verdict, evidence IDs it relied on |
| `run.terminal` | final status (`refunded` / `denied` / `escalated` / `abandoned` / `incomplete`), refund receipt ID, decision-to-evidence links |

**What we deliberately don't store:** the model's private chain-of-thought. The auditor's question is "what did it see and what did it do", and that is answered by the assembled input, the raw output (including any visible rationale the model produced), the tool arguments, the policy decision and the committed state. A reasoning narrative is weaker evidence than those, and it adds another place for card data to land.

## 3. The raw evidence artifacts

This is where most of the change is.

### What gets captured verbatim (after redaction)

- **Model input**: the fully assembled message array exactly as sent. That means system prompt, conversation, tool definitions, tool results *as inserted into context*, and any retrieved policy text. Store the rendered request body, not the template plus variables. Templates drift, and re-rendering later is not proof of what was sent.
- **Model output**: the raw response body, including stop reason and every tool-call block.
- **Tool request/response**: the raw payload sent to and returned by each tool, before any agent-side summarization or truncation.

The model-visible copy of a tool result and the raw tool response are stored **separately**. If context assembly truncated or reformatted the order record, the auditor can diff "what the tool returned" against "what the model saw". Wrong decisions often come from that gap.

### Artifact envelope

```json
{
  "artifact_id": "art_7f3c...",
  "event_id": "evt_0142",
  "run_id": "run_9a1...",
  "kind": "model_input",
  "content_sha256": "<hash of the redacted bytes as stored>",
  "redaction": {
    "policy_version": "pci-redact-v3",
    "applied_before_persist": true,
    "spans": [
      {"path": "messages[3].content", "offset": 212, "length": 19,
       "type": "PAN", "replacement": "[PAN tok_4f9a last4=4242]"},
      {"path": "messages[3].content", "offset": 260, "length": 3,
       "type": "CVV", "replacement": "[CVV removed]"}
    ]
  },
  "truncated": false,
  "size_bytes": 18234,
  "classification": "restricted-customer",
  "retention_until": "2027-10-05"
}
```

The redaction manifest is what makes the artifact auditable. The auditor knows the text is exact apart from the listed spans, and knows what kind of value was in each one.

## 4. Keeping card data out

### Prefer card data never reaching the model

The most robust fix is upstream. Tools that touch payment data return a **vault token plus last4/brand/expiry month**, never the full number. The refund tool takes `payment_method_token`, not a card number. If the model never sees a PAN, then "exactly what the model saw" contains no PAN, and the redactor becomes a backstop instead of the main control.

### Redaction pipeline (runs in-process, before anything is written or exported)

1. **Structured fields**: known paths (`card.number`, `cvv`, `track_data`, `billing.full_address` as needed) are replaced by schema-driven rules.
2. **Free text**: customers paste card numbers into chat. Scan with a PAN detector (13–19 digit runs, separator-tolerant, **Luhn-checked** to cut false positives) plus CVV/expiry context patterns.
3. **Replacement** keeps audit meaning without the secret:
   - PAN → `[PAN tok_<vault token or keyed HMAC> last4=4242]`. Use a keyed HMAC or vault token, **not a plain hash**. PANs have low entropy and a bare SHA-256 can be brute-forced. The same card gets the same token across the run, so the auditor can see "the card the customer mentioned is the card refunded to".
   - CVV/PIN/full track data → removed outright. These must never be stored, even tokenized.
4. **Fail closed.** If the redactor errors or times out, persist the event with `artifact_ref: null, artifact_status: "redaction_failed"` and alert. Never fall back to writing the raw payload.
5. **Secret scanning after write** as a second check over the artifact store, with alerts on any hit. Treat a hit as an incident, not just a log line.

The same pipeline covers the event stream. Short "reason" strings and tool args in events go through it too, because a model-written reason like "refunding card 4111…" is a leak path.

## 5. Access, retention and export

- **Two stores.** Operational telemetry (events, metrics) is broadly readable by on-call staff. Evidence artifacts go in a restricted store with per-tenant isolation, role-based access (auditor, incident lead) and **read-access logging**.
- An `artifact_ref` in a trace UI is a pointer that requires authorization. It must not be a public or shareable debug link.
- Retention is set per artifact class to match your audit/regulatory needs (policy/approval/refund evidence kept longer than ordinary debug artifacts). Support deletion requests by `run_id` and customer pseudonym.
- **No sampling for money.** Ordinary debug spans can be sampled, but every run that reaches `policy.decision` for a refund keeps 100% of its events and artifacts.
- Exports (to a vendor tracing tool, eval datasets, tickets) go through the same redactor and never include raw artifacts by default. Production traces only become eval data through a separate, consented path.

## 6. Example timeline: what the auditor would see for the bad refund

```
seq  event                 summary                                         artifact
001  request.accepted      case C-5531, scope refund:max=200 USD           -
002  context.assembled     prompt v14, 6 items, 1 TRUNCATED                 art_input_1
                           (order_lookup result cut at 2k tokens)
003  model.call            model X v2025-xx, finish=tool_use, 3.1k in tok    -
004  model.output          tool_call order_lookup(order=8812)                art_out_1
005  tool.attempt          order_lookup a1                                   art_treq_1
006  tool.result           success, status=delivered, total=14.90,           art_tres_1
                           delivered 47 days ago
007  context.assembled     order result inserted; policy doc v7 DROPPED      art_input_2
                           (budget)   <-- model never saw 30-day rule
008  model.output          proposes refund amount=149.00 reason=damaged      art_out_2
009  proposal.validated    schema ok, digest d41f..                          -
010  policy.decision       policy v3: rule R2 (amount<=order_total) NOT      -
                           EVALUATED (rule missing in v3) -> allow
011  tool.attempt          refund a1, idem=run9a1-op4                        art_treq_2
012  tool.result           unknown_effect (timeout)                          art_tres_2
013  retry                 attempt 2, same idempotency key                   -
014  tool.result           success, receipt R-7781                           art_tres_3
015  state.transition      refund v0 -> v1 (149.00 refunded)                 -
016  run.terminal          refunded, receipt R-7781                          -
```

The auditor can open `art_input_2` and see exactly what the model was given. They can diff it against `art_tres_1` to see the truncation, and look at `policy.decision` to see that the deterministic check that should have blocked the refund didn't exist or didn't run. That separates three failures a summary would have merged: a context-budget bug, a model error, and a policy gap.

## 7. Operator queries and runbook

Typical queries the schema has to support:

- **"Show everything for case C-5531"**: all events by `run_id` ordered by `seq`, with artifact pointers.
- **"What did the model see before it proposed the refund?"**: the last `context.assembled` with `seq` < the `proposal.validated` event, then open its artifact.
- **"Did any tool result get truncated or dropped from context?"**: `context.assembled` where `truncated_items` or `dropped_items` is not empty.
- **"Refunds where proposed amount > order total"**: join `proposal.validated` to the order-lookup `tool.result` by `run_id`.
- **"Refund tool executed more than once per operation"**: `tool.attempt` grouped by `operation_id` where the count of successful results is > 1.
- **"Policy allows that a human or rule later overturned"**: `policy.decision=allow` joined to a later reversal or chargeback.

**Audit runbook:**

1. Pull the run by case ID and check the completeness verdict (section 8). If it says incomplete, report which events are missing before drawing conclusions.
2. Walk `proposal` → `policy.decision` → `approval` → `tool.attempt/result` → `state.transition`.
3. For the decision step, open the model-input artifact and the raw tool responses, and compare model-visible against tool-returned.
4. Note the prompt, model, policy and tool versions, then check whether other runs on the same versions show the same pattern.
5. Access is logged. Don't copy artifact content into tickets; reference artifact IDs.

## 8. Proving it works

Before trusting it, test that a failed run can be **reconstructed from events alone**, and that gaps are reported as gaps:

- **Redacted secret**: feed a chat message and a tool response containing a Luhn-valid test PAN and a CVV. Assert that neither appears in any event, artifact or export, that the token and last4 do appear, and that the manifest lists both spans.
- **Redactor failure**: force the redactor to throw. Assert no raw payload is written and `redaction_failed` is recorded and alerted.
- **Lost response**: simulate a refund tool timeout after the provider commits. Assert `unknown_effect` is recorded, the retry reuses the idempotency key, and the provider receipt joins via `correlation_id`.
- **Denied action**: the policy denies a refund. Assert the denied proposal and its artifacts are kept even though the run then escalates successfully.
- **Restart/resume**: kill the worker mid-run. Assert `run_id` and `operation_id` survive and the `attempt_id`s differ.
- **Nested workers**: if a sub-agent does the order lookup, assert parent/child spans join.
- **Evaluator disagreement**: an online evaluator flags a refund the policy allowed. Assert both verdicts are linked to the same evidence IDs.
- **Broken traces**: inject orphan parent spans, cyclic links and a missing `policy.decision`. The reconstruction tool must return `incomplete` or `inconsistent` and name the gap, not render a clean-looking timeline.
- **Replay** for analysis uses the stored artifacts with fake or read-only tools. It must never re-run the live refund call.

## 9. Metrics and alerts

Track these by model, prompt and policy version and by refund slice (reason code, amount band, channel). Don't use user or run IDs as metric labels.

- refund approval rate; human-review rate; policy denials; approvals later reversed or charged back
- proposals where amount > order total or outside the policy window (should be zero after policy fixes)
- context truncation/drop rate on decision steps
- `unknown_effect` tool results; duplicate-execution count; retry exhaustion
- malformed/truncated/refusal model outputs
- redaction-failure count and post-write secret-scan hits
- p50/p95 latency and cost per *completed case*, including failed attempts and retries. Show unavailable token data as unavailable, not zero.

Alerts should lead to an action someone can take:

- **any** secret-scan hit or redaction failure → page, and halt artifact export
- duplicate refund execution for one `operation_id` → page, and consider disabling the refund tool
- policy-allow on an amount above order total → page
- truncation on decision steps or approval-reversal rate rising above baseline → ticket for investigation

Start thresholds as provisional and set them from a measured baseline over the first few weeks, rather than guessing production numbers.

## 10. About the refund that has already happened

The current traces can't show what the model saw for that run, and this redesign can't recover it. Collect whatever authoritative records do exist for that run: the refund provider's receipt and request log, the order system's state history, and any gateway/proxy request logs that kept full bodies (handle these as restricted, since they may contain unredacted card data). Then report the reconstruction as **partial**, with the model-input step explicitly marked unknown, rather than filling the gap with a guess from the summary.

## Rollout order

1. Tokenize card data at the tool boundary, so the model never needs a PAN.
2. Add the redaction pipeline (fail-closed) and the restricted artifact store with access logging.
3. Emit `context.assembled`, `model.output`, `tool.attempt/result` with artifact refs, plus `policy.decision`, for refund runs at 100%.
4. Add operation/attempt IDs and idempotency-key correlation with the refund provider.
5. Run the verification cases in section 8, then turn on the metrics and alerts.
