# Redesigning the refund agent's trace for auditability without leaking card data

## 1. What went wrong with the current trace

A one-line summary such as `model: decided refund eligible` or `tool: order_lookup ok` answers none of the auditor's questions:

- **What did the model actually see?** That means the exact system prompt version, the conversation, the retrieved policy text, the tool results in context, and whether anything was cut off.
- **What did the tools actually return?** Was the order status really `delivered`? Was the refund window computed from the right date? Was a prior refund already on file?
- **What was proposed, what was checked, and who or what authorized it?** Did a policy check run? Did it pass, or was it skipped? Was there a human approval?
- **What was actually executed, and what did the payment system confirm?**

Summaries are also written by the system being audited. If the model or a summarizer misread a tool result, the summary repeats the same mistake. The auditor needs primary evidence, meaning the bytes that crossed each boundary, and not a narrative about them.

The goal is: **keep full-fidelity evidence of every model input/output and tool input/output, redact card data before anything is persisted, store the evidence in a restricted store, and keep only pointers and digests in the general trace.**

---

## 2. Core design: envelope events plus a restricted evidence store

Split what you keep into two tiers.

| Tier | What it holds | Where it lives | Who can read it | Sampling |
|---|---|---|---|---|
| **Trace envelope** | Structured event metadata: IDs, ordering, versions, status, timings, token counts, digests, pointers to evidence blobs, short normalized fields such as `refund_amount` and `policy_result` | Your normal tracing/APM backend | Engineers and on-call | Debug spans can be sampled. Runs with side effects cannot (see below) |
| **Evidence blobs** | Exact rendered model input (after redaction), raw model output, exact tool request and response bodies (after redaction), policy inputs and outputs, approval records | Restricted, append-only evidence store, encrypted, scoped per tenant | Auditors and a small incident-response group. Every read is logged | **100% for any run that proposes or executes a refund** |

Each envelope event refers to its blobs by a content-addressed ID (`sha256` of the redacted bytes). This gives you:

- **Integrity.** The auditor can show that the blob they are reading is the one referenced at that point in the run.
- **No payload sprawl.** Full prompts and tool bodies never land in the general log pipeline, dashboards, or trace exports. A pointer to a restricted blob is not a public debug link.
- **Deduplication.** The system prompt and policy documents are stored once and referenced by every call that used them.

---

## 3. Keeping card data out: redact at the source, before persistence

### 3.1 Principle: the model should not see card data either

Processing a refund does not require a full card number (PAN) or a CVV. The strongest design keeps them out of the model's context in the first place:

- **Tool adapters** (payments lookup, order lookup) return the payment method as a processor token plus display fields: `{"payment_method_token": "pm_7Hk...", "brand": "visa", "last4": "4242", "exp_month": null}`. They never return the PAN, CVV, or full expiry.
- **Inbound customer text** goes through the same card-data scanner before it is added to the model context. Customers do paste card numbers into chat.

When redaction happens before the model call, **the redacted record is byte-for-byte what the model saw.** You get full fidelity and safety together, and the stored digest matches the digest of the actual request payload.

### 3.2 The redaction pipeline (runs before any write to the envelope or the evidence store)

1. **Structured field rules.** These are known field paths per tool schema, such as `card.number`, `card.cvc`, `track_data`, and `billing.card_exp`. Drop sensitive authentication data entirely: CVV/CVC, track data, PINs. Do not store them in any form, encrypted or hashed. Replace the PAN with `[PAN:visa:****4242:ref=h_9c1e…]`.
2. **Free-text scanner.** Find digit runs of 13–19 digits, allowing spaces and dashes, that pass a Luhn check and match a known BIN range. Also look for CVV-like values near keywords such as "cvv", "security code", or "exp". Apply it to customer messages, model output, tool error strings, and log messages.
3. **Keyed correlation token.** `ref=h_…` is an HMAC of the PAN under a key held in KMS. It is **not** a plain hash, because the PAN space is small enough to brute-force. With it, an auditor can see that the same card appears in message 2 and in tool result 4 without ever seeing the number.
4. **Redaction manifest.** Each blob records which rules fired, how many times, at which JSON paths or character offsets, and which version of the redaction rule set ran. The auditor can then tell redaction apart from missing content.
5. **Fail closed.** If the scanner errors or times out, store the envelope with `payload_status: "withheld_redaction_failure"` and raise an alert. Never fall back to writing the raw payload.

### 3.3 When raw card data did reach the model

If a PAN got into the model context, for example from an older adapter or a scanner miss, the stored record will differ from the true model input at the redacted spans. Make that explicit and do not hide it:

- The blob carries `fidelity: "redacted_post_model"` and lists the redacted spans.
- `model_input_digest_pre_redaction` is an HMAC (not a plain hash) of the original payload. It lets you prove consistency later if needed, without storing the card number.
- This is also a security finding in its own right. Count it as a metric (section 6) and fix the adapter.

### 3.4 Other protections

- Evidence store access is limited per tenant and per role, and every read is logged. Trace export and "share this trace" features include envelopes only, never blob contents.
- Retention: keep refund-run evidence for your audit or dispute window, then delete it. The envelope can outlive the blobs and records `blob_deleted_at`.
- Run a canary scan in CI and in production over every sink (APM, log aggregator, evidence store, eval datasets) for Luhn-valid PANs and for planted test PANs.
- Keep operational evidence separate from evaluation datasets. Copying an audited run into a test set is a separate step with its own consent and redaction checks.

---

## 4. The event contract

### 4.1 Identity and ordering (on every event)

```
run_id            one customer refund conversation / task
operation_id      logical step (e.g. "issue_refund for order 8812"), stable across retries
attempt_id        one try of that operation
span_id / parent_span_id   nesting (sub-agents, tool calls under a model turn)
seq               monotonically increasing per run; causal order, not wall clock
event_time        timestamp (informational; seq is authoritative for ordering)
state_version     version of the case/order state the step read or wrote
principal         who the agent acts for + authorized scope (e.g. refund_limit=100 USD)
release           agent build id, plus versions below
```

Retries and resume after a crash keep `run_id` and `operation_id` and get a new `attempt_id`. That makes it visible that a refund was attempted twice and how the duplicate was handled.

### 4.2 Event types and what each must keep

| Event | Envelope fields (always) | Evidence blob (restricted, redacted) |
|---|---|---|
| `request.accepted` | channel, customer ref (tokenized), order ref, principal scope | Original inbound message |
| `context.assembled` | **context manifest**: an ordered list of segments with `{segment_type, source_id, source_version, token_count, blob_id}` for the system prompt, policy chunks, conversation turns, and tool results. Also `truncated: bool` and the names of dropped segments | Each segment stored once, by digest |
| `model.call` | model ID and exact version, prompt template version, output schema version, tool definitions version, sampling params, `input_digest`, input/output tokens (or `unavailable`), latency, `stop_reason` (`end_turn`, `max_tokens`, `refusal`, `tool_use`) | **Exact rendered request payload** (system, messages, tool definitions) and **raw response** |
| `model.output.parsed` | parse result: `ok`, `malformed`, `refusal`, or `truncated`. Parsed proposal digest | Raw text if parsing failed |
| `proposal` | normalized action: `{action: refund, order_id, amount, currency, reason_code}` plus `action_digest`. Evidence IDs the model cited (which tool results or policy chunks) | n/a (fully in envelope) |
| `policy.decision` | policy engine version, rules evaluated, result (`allow`/`deny`/`needs_approval`), reason codes, **input facts with their source event IDs** (e.g. `delivered_at` from tool result seq 7) | Full policy input and output |
| `approval.requested` / `approval.decided` | approver role and ID, decision, timestamp, what was shown (digest) | The approval preview exactly as shown |
| `tool.attempt` | tool name and version, `operation_id`, idempotency key, argument digest, target system | Exact request body |
| `tool.result` | status (`success`, `error`, `timeout`, `unknown_effect`), HTTP or processor code, latency, **receipt ID** (e.g. processor refund ID), result classification | **Exact response body** |
| `state.transition` | from/to state, `state_version` before and after, triggering event seq | n/a |
| `retry` / `failure` | reason, attempt count, policy that allowed the retry | Error body |
| `eval.outcome` | evaluator version, verdict, disagreement flags, linked evidence IDs | Evaluator inputs |
| `run.terminal` | terminal status (`refunded`, `denied`, `escalated`, `abandoned`, `unknown_effect`), total cost across all attempts and workers | n/a |

### 4.3 What not to keep

- **No private chain-of-thought.** Do not require or store hidden reasoning. The auditor needs the inputs, the proposal, the facts the policy engine used, the approval, and the processor receipt. That evidence is stronger than a narrative. If the model emits a short user-visible rationale as part of its structured output, keep it as an output field, labeled as model-generated.
- **No unredacted payloads in envelope fields.** Normalized fields such as amount, order ID, and reason code are fine. Free text goes in blobs, after redaction.

---

## 5. Example: reconstructing the wrong refund

Here is how the audited case would look under the new design. Assume the agent refunded an order that was outside the 30-day window.

```
seq  event               key fields
---  ------------------  -----------------------------------------------------------
1    request.accepted    run=r_51 order=8812 principal=support_agent scope{refund_limit:100USD}
2    context.assembled   segments=[sys_prompt@v14, policy_refunds@v6#chunk3, msg_1]
3    model.call          model=<id@version> tmpl=v14 stop=tool_use in_digest=a1f..
4    tool.attempt        get_order(8812)  op=op_lookup att=1
5    tool.result         success  blob=b_77  (body: delivered_at=2026-08-01, payment=[PAN:visa:****4242:ref=h_9c1e])
6    context.assembled   segments=[..., tool_result b_77]  truncated=false
7    model.call          stop=end_turn  out_blob=b_80
8    model.output.parsed ok
9    proposal            refund 8812 amount=89.00 reason=within_window  cited=[seq5, policy chunk3]
10   policy.decision     engine=v3  result=allow  facts{delivered_at: <missing>, window_days:30}
                         reason=window_check_skipped_missing_fact      <-- root cause visible
11   tool.attempt        issue_refund op=op_refund att=1 idem=k_8812_1
12   tool.result         success receipt=re_3Kx...
13   state.transition    order 8812: paid -> refunded  state_version 41 -> 42
14   run.terminal        refunded  cost=<sum of seq3,7 tokens>
```

From the events alone, the auditor can see:

- The tool **did** return `delivered_at = 2026-08-01` (blob `b_77`), so the data was correct.
- The model claimed `within_window`. The exact model input (blob for seq 7) shows whether the date was present in context and not truncated.
- The policy engine received `delivered_at: <missing>`. The fact-mapping step failed to pass the date along, and the engine **allowed by default** instead of denying. That is the real defect, and the one-line summaries hid it.
- The card shows up only as `****4242` with a correlation token.

### Operator runbook: "why was refund X approved?"

1. Look up `run.terminal` by processor receipt ID or order ID, then get the `run_id`.
2. Pull all events for the run ordered by `seq`. Check completeness: every `tool.attempt` has a `tool.result` (or an explicit `unknown_effect`), every `proposal` has a `policy.decision`, every `parent_span_id` resolves, and there are no cycles.
3. Open `policy.decision` and follow each input fact's source event ID back to the tool result blob. Check that the values match.
4. Open the `model.call` evidence for the turn that made the proposal and compare it with the context manifest. Was the relevant tool result present? Was anything truncated?
5. Compare `proposal.cited` evidence IDs with what was actually in context. A citation to something the model never saw is a finding.
6. Check approvals: was one required by the principal scope or the amount, and was it obtained?
7. If any required event is missing, the report must say **"incomplete reconstruction"** and name the gap. It must not present a complete-looking story.

### The past incident

Events that were never captured cannot be recovered. For the refund already under audit, rebuild what you can from systems of record: the order database history, the processor's refund record and request logs, and any API gateway logs of tool calls. Label the result as a partial reconstruction with the gaps listed explicitly.

---

## 6. Metrics and alerts

Envelope events feed metrics. Label by release, model version, policy version, and reason code. **Never** label by run, customer, or order ID, because that cardinality is unbounded.

| Signal | Why it matters | Suggested response |
|---|---|---|
| Policy decisions with missing input facts | The exact failure class from this incident | **Page.** Any `allow` with a missing required fact should be impossible. Fix the policy to deny on missing facts. Consider halting refund execution until it is fixed |
| Refunds executed without a matching `policy.decision` or required approval | Authorization bypass | Page and halt mutation capability |
| Redaction events: `withheld_redaction_failure`, PAN detected post-model, canary PAN found in any sink | Card data exposure | Page the security owner. Fix the adapter or scanner |
| `unknown_effect` tool results on `issue_refund` | Possible double refunds or missed refunds | Ticket. Reconcile against processor receipts |
| Model `truncated` / `malformed` / `refusal` rates | Context overflow or schema drift hides evidence from the model | Investigate when above baseline |
| Model citations that don't match the context manifest | Unsupported reasoning | Sample for review |
| Refund approval rate, escalation rate, human-override rate, by reason code | Behavior drift | Investigate on drift and compare against the previous release |
| p50/p95 latency and cost per **completed refund case**, including retries and failed attempts | Operations | Budget review. Report unavailable token data as unavailable, not zero |

Thresholds should start as **provisional** and be set from a measured baseline over a defined window with a minimum sample size. The exceptions are safety invariants such as "allow with missing fact" and "refund without policy decision", which should be zero and page on the first occurrence. Each signal needs an owner and a defined action. Do not alert on every model call.

---

## 7. Verification before you trust it

Run these as tests in a staging environment with fake payment tools. Replays for analysis must use recorded evidence and fakes and must never call the live refund API.

1. **Redacted secret:** plant a test PAN and CVV in a customer message, in a tool response, and in a tool error string. Assert that none appears in any sink, that the PAN shows as masked plus a correlation token, that the CVV is absent, and that the manifest records each redaction.
2. **Scanner failure:** force the redactor to throw. Assert that the payload is withheld, the envelope is still written, and the alert fires.
3. **Fidelity:** for a clean run, assert that the stored model input blob digest equals the digest of the payload actually sent to the model API.
4. **Lost response:** time out `issue_refund` after the processor commits. Assert `unknown_effect`, a retry with the same idempotency key, and reconciliation to a single receipt.
5. **Denied action:** policy denies, and the trace shows the proposal, the denial with reason codes, and no `tool.attempt`. The denied attempt is retained even if a later attempt succeeds.
6. **Restart mid-run:** kill the worker after the proposal. Assert that the resumed run keeps `run_id` and `operation_id` with a new `attempt_id` and that ordering by `seq` is correct.
7. **Nested workers:** if a sub-agent does the order lookup, its spans attach under the correct parent and its cost rolls up to the run.
8. **Broken traces:** inject an orphan parent span, a cyclic link, and a missing `tool.result`. Assert that the reconstruction tool reports "incomplete/inconsistent".
9. **Evaluator disagreement:** an automated evaluator flags a refund that the policy allowed. Assert that both verdicts are linked to the same evidence IDs.
10. **Replay of this incident:** re-run the audited case through the new pipeline with recorded fixtures. Check that the trace exposes the missing-fact default-allow in `policy.decision` at seq 10.

---

## 8. Rollout order

1. **Redaction first.** Move card-data stripping into the tool adapters and inbound message handling, and add the fail-closed scanner. Nothing else ships before this.
2. Stand up the restricted evidence store with access logging and retention. Then add blob capture for `model.call` and `tool.result` on refund runs at 100%.
3. Add the identity and ordering fields, `context.assembled` manifests, and `policy.decision` fact provenance.
4. Build the reconstruction query and completeness checker, then run the verification suite.
5. Add metrics and the safety-invariant alerts. Separately, fix the policy engine to **deny on missing required facts**. That is a correctness bug in its own right, beyond the observability gap.
