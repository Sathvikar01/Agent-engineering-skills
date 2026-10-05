# Receipt-to-reimbursement agent: currency failure, next debugging step, and the "is it robust?" answer

## TL;DR

- **Short answer for the reviewer: no, we can't call it robust yet.** We have one 20-example run with 18 passes. One of the two failures is a wrong currency, and we haven't tested currency handling on its own. "Robust" has to mean a named test or eval result, and we don't have one for currency yet.
- **Next step:** reproduce the failing example, capture the actual output, a trace, and the run command, and write down a root-cause hypothesis. Only then hand the AI coding assistant a specific request that contains that evidence. Don't ask it to "investigate the currency bug."
- **Fix direction (proposed, not yet validated):** the model reports the currency *evidence* it sees on the receipt (symbol, code, source text). Trusted code maps that evidence to an ISO-4217 code. When the evidence is ambiguous, code returns a typed `needs_review` result instead of guessing. Add a currency eval slice where any silently wrong currency fails the run.

---

## 1. What we know and what we don't

| | Status |
|---|---|
| 18/20 pass on the current eval set | Observed. One run, so we know nothing about variance yet |
| 1 failure: wrong `currency` field | Observed. We haven't captured the exact expected vs. actual values or the input text yet |
| 1 other failure | **Unclassified.** Don't assume it shares the currency root cause. Triage it separately (step 2e) |
| Currency handling generalizes beyond these 20 | **Unverified.** No currency slice, no ambiguous-symbol cases, no foreign-card-statement cases |

A wrong currency is a severe failure for reimbursement. 100 CAD paid out as 100 USD is a money error, not a formatting slip. The other 18 passes can't offset it. A critical-field regression fails the gate even when the average looks good.

---

## 2. Next debugging step: OBSERVATION, then HYPOTHESIS, then TRACE, then FIX

### 2a. OBSERVATION: reproduce and capture raw evidence

Run only the failing example with the same configuration as the eval run (model version, prompt version, temperature, normalizer version):

```
<eval-runner> --case <failing_case_id> --trace --out runs/currency-debug/
```

Capture these as raw artifacts, not paraphrase (redact any personal or card data):

1. The exact command and the config/version stamp.
2. **Expected vs. actual**, for example `expected.currency = "CAD"`, `actual.currency = "USD"`. Also record `amount`, `total` and any FX or `reimbursable_amount` fields, so we can see whether the error spread into downstream arithmetic.
3. **Input evidence:** the receipt text/OCR spans that contain the amount and any currency marker (symbol, code, merchant address, country, card-statement line).
4. **Trace excerpt:** the raw model output for the currency field, *before* normalization, then the value after each normalization or validation step.
5. **Rerun 3–5 times.** Does it fail every time or only sometimes? That tells us whether this is deterministic code or model variance.

### 2b. HYPOTHESIS: write one down before looking at code

Candidate root causes, ranked by how often each shows up on receipts. Fill these in from the captured evidence:

| # | Hypothesis | What would confirm it in the trace |
|---|---|---|
| H1 | **Ambiguous symbol defaulted.** The receipt shows `$` (or `¥`, `kr`, `£`). The model or the normalizer maps it to a default (USD) instead of using other evidence or abstaining | Raw model output says `"$"` or `"USD"` with no ISO code in the source text, and a lookup like `{"$": "USD"}` exists |
| H2 | **Wrong amount line chosen.** On a foreign-card or hotel receipt showing "EUR 84.00 / USD 91.20", the currency came from a different line than the amount | Currency and amount cite different source spans |
| H3 | **Normalizer overwrote a correct extraction.** The model said "CAD", but a downstream locale or default step replaced it | Raw output is correct, post-normalization value is wrong |
| H4 | **Schema allows free text.** `currency` is a plain string, so "C$" or "Canadian dollars" doesn't parse and falls back to a default | Validation log shows coercion or a fallback |
| H5 | **The gold label is wrong.** | The source receipt clearly supports the "actual" value |

**Committed hypothesis (example, to replace with whatever the evidence shows):** *"H1: the source shows only `$`. The merchant address is in Canada. Our normalizer maps `$` to USD without using other evidence and without abstaining."*

### 2c. TRACE: confirm or reject

- Follow the field through each stage: source span, then raw model output, then the normalizer, then the validator, then the final output. The stage where the value first goes wrong is where the bug is.
- If H1 is confirmed, grep the eval set and fixtures for other `$`-only receipts. The 18 passes may be passing by luck (every `$` receipt happened to be USD).
- If the trace rejects the hypothesis, go back to 2b with the next one. Don't start changing code on a rejected hypothesis.

### 2d. FIX: write a failing test first, then the smallest coherent change

1. Add the failing example and 2–3 nearby variants as **deterministic unit tests on the normalizer**, plus an eval case. Watch them fail.
2. Make the smallest change to the cause. Don't make a broad prompt rewrite.
3. **REVIEW:** rerun the full 20 and the new currency cases. Check the diff for unintended behavior. Decide **KEEP / REVISE / ROLLBACK**. Any regression on the 18 currently passing cases means REVISE.

### 2e. The other failure

Reproduce and classify it the same way (observation, then hypothesis). Record it as its own failure class. It doesn't block the currency fix, but it does block any claim about overall quality.

---

## 3. What I'll paste to the AI coding assistant

I'll send this only *after* 2a–2c, so it contains evidence and a hypothesis, not a request to "investigate." Bracketed values get replaced with the real captured artifacts.

```text
Context: receipt-to-reimbursement agent. Pipeline: OCR text -> LLM extraction (JSON) ->
<normalizer function/file> -> <validator> -> reimbursement output.

Failing case: <case_id>
Command: <eval-runner> --case <case_id> --trace
Config: model=<model+version>, prompt=<prompt version>, normalizer=<commit>

Expected vs actual (only currency differs):
  expected: {"amount": 42.50, "currency": "CAD", ...}
  actual:   {"amount": 42.50, "currency": "USD", ...}

Source evidence (redacted OCR excerpt):
  "TOTAL  $42.50" ... "123 Queen St W, Toronto ON"   (no ISO code anywhere on the receipt)

Trace excerpt:
  raw_model_output.currency = "$"
  after <normalizer>: "USD"      <- first wrong value
  validator: passed (currency is any 3-letter string)

Reproducibility: fails 5/5 reruns -> deterministic, not sampling variance.

My hypothesis: <normalizer> maps "$" -> "USD" unconditionally and never abstains on
ambiguous symbols. The validator only checks the shape (3 letters), not whether the
source supports the code.

Please:
1. Point to the exact code that maps the symbol to a currency code and confirm or reject my
   hypothesis using that code. If you reject it, say what the trace implies instead.
2. Write failing unit tests FIRST for the normalizer:
   - "$" + Canadian address, no code      -> needs_review (or CAD only if we define that rule explicitly)
   - "CAD 42.50"                           -> CAD
   - "$42.50" with explicit "USD" on receipt -> USD
   - "EUR 84.00 / USD 91.20" card line      -> currency matches the amount line chosen
3. Propose the smallest diff that makes them pass:
   - ambiguous symbols must not default silently; return a typed needs_review result
   - output currency must be a valid ISO-4217 code
   - do not change other fields, the eval scoring or gold labels
4. List any other code paths that set or override currency.

Constraints: no prompt-only fix as the sole control; no relaxing assertions; show the diff
and the test output.
```

After the reply, I check its claims against the code and the test run. I'm the one who decides whether to keep the diff, and I record what it proposed versus what I accepted or changed (section 5).

---

## 4. Answer to the reviewer: "Is the currency handling robust?"

Technical-interview format: answer, then implementation, then reason/trade-off, then evidence, then limitation/fallback.

### Today, before the fix

> **Answer:** It isn't demonstrated, and one case shows it isn't correct yet. I wouldn't call it robust.
>
> **Implementation:** Currently the model extracts `currency` as part of the JSON output and `<normalizer>` coerces it to a code. [Confirm the exact location from the trace. Don't state it from memory.]
>
> **Reason / trade-off:** Putting currency inside the model's output was the simplest first version. The cost is that the model or the default mapping can guess on an ambiguous symbol, and nothing downstream checks the guess against the source.
>
> **Evidence:** One eval run, 18/20 pass, on 20 examples. Case `<id>` returned USD where CAD was expected. We have no currency-specific slice, so the 18 passes don't tell us how ambiguous symbols are handled.
>
> **Limitation:**
> - **GAP:** Ambiguous symbols (`$`, `¥`, `kr`) can be silently mapped to a default currency.
> - **CURRENT FALLBACK:** None in code. Only a human reviewing the payout would catch it.
> - **NEXT STEP:** Reproduce and trace (section 2), add a failing test, and move the currency decision into deterministic code that abstains on ambiguity. Then add a currency eval slice.

### After the fix (what I'd be able to say, if the checks pass)

Every number here is a placeholder until the run happens.

> **Answer:** Currency is extracted as evidence, decided by code, and abstains when it's ambiguous. Robustness is shown by the currency slice results below, not claimed in general.
>
> **Implementation:** The model returns `{currency_evidence: {raw_symbol, raw_code, source_span_id}}`. `<normalize_currency()>` maps an explicit ISO code or an unambiguous symbol to ISO-4217. An ambiguous symbol with no disambiguating evidence returns `needs_review` with a reason. The validator rejects any currency whose `source_span_id` doesn't exist in the input. FX and reimbursement arithmetic are deterministic and run only on a validated currency.
>
> **Reason / trade-off:** Reading the receipt is the uncertain part, so the model handles it. Mapping a symbol to a code and computing money are specifiable rules, so code handles them. The cost is more review-queue items on `$`-only receipts. We chose that over silent wrong payouts.
>
> **Evidence:** `<test file>` has N normalizer tests passing. The currency eval slice (M cases: ambiguous symbols, explicit codes, dual-currency card lines, missing currency, symbol after the amount, comma decimals) scores X/M correct, Y routed to review, **0 silently wrong**. The original 20 rerun at Z/20 with no regressions. Command: `<rerun command>`.
>
> **Engineer vs. AI:** [Fill in truthfully. Example shape:] *"The AI assistant drafted the normalizer refactor and two of the tests. I wrote the failing reproduction, chose abstention over a locale-based default, rejected its suggestion to infer currency from the merchant country alone, and added the dual-currency case."*
>
> **Limitation:**
> - **GAP:** Unseen layouts and currencies outside the slice; review volume on `$`-only receipts.
> - **CURRENT FALLBACK:** `needs_review`, so a human confirms before payout.
> - **NEXT STEP:** Monitor the review rate and the rate of reviewers overriding the currency. Use the overrides as new eval cases.

---

## 5. Decision record and what to keep

| Decision | Hypothesis | Alternatives | Why chosen | Evidence | Limitation | Fallback | Status |
|---|---|---|---|---|---|---|---|
| Model extracts currency evidence, code decides the ISO code, abstain on ambiguity | Symbol-to-code mapping is specifiable; the ambiguity needs abstention, not a guess | (a) Prompt tweak telling the model "be careful with $"; (b) infer from merchant country; (c) keep the default USD mapping | (a) is guidance, not enforcement; (b) is wrong for travelers and foreign cards; (c) is the bug | Proposed: failing test + currency slice. **Not yet run** | More review items | Typed `needs_review` | **PROPOSED** |

Keep these artifacts for the development record: the reproduction command and output, the trace excerpt, the exact prompt sent to the AI assistant, its reply, the diff, the failing-then-passing test output, and the rerun of the 20 plus the slice. Keep them raw, not summarized.

## 6. Done criteria for this step

- [ ] Failure reproduced, and the root cause confirmed by the trace (not just assumed)
- [ ] Failing test was written before the fix, and passes after
- [ ] Original 20 rerun: no regressions; the second failure classified separately
- [ ] Currency slice exists, with **0 silently wrong currencies** as a hard gate
- [ ] Reviewer answer updated with the actual numbers. Anything not run is reported as unverified
