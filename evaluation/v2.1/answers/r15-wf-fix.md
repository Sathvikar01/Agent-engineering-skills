# Currency field failure: next debugging step and reviewer answer

## TL;DR

- **Next step:** reproduce the one failing currency case in isolation and record the raw evidence: the input, the raw model output, the normalized output, the expected value and the diff. Then work out which pipeline stage first produced the wrong value. Write a root-cause hypothesis **before** asking the AI coding assistant anything, and paste that evidence and hypothesis into the request. Don't just ask it to "investigate the currency bug".
- **Reviewer's question ("is it robust?"):** the honest answer today is **no, not shown yet**. 18/20 overall says almost nothing about currency handling in particular. We have one known currency failure, an unexplained second failure, and no currency-specific test slice. Until we have one, "robust" is an unverified claim.

---

## 1. What we actually know (observation, not interpretation)

| Fact | What it does and does not tell us |
|---|---|
| 18/20 examples pass | That's a whole-output pass rate. It doesn't measure currency accuracy. |
| 1 failure has a wrong `currency` field | One reproduced mismatch. We don't know the root cause yet. |
| 1 other failure | Cause unknown. **Check whether it's related** before assuming the currency bug is isolated. |
| Unknown: how many of the 20 have non-default, ambiguous or multiple currencies | If only 2 of 20 are foreign-currency receipts, currency accuracy could really be 1/2. Count this before quoting any number. |

Why this matters: a wrong currency on a reimbursement is a **money error**, not a formatting nit. ¥5,000 paid as $5,000 is a real loss. So the bar is "never silently wrong". Getting it right "most of the time" isn't enough.

---

## 2. Debugging plan: OBSERVATION, then HYPOTHESIS, then TRACE, then FIX

### Step 1: Reproduce and capture raw evidence (no fixing yet)

Re-run **only** the failing example through the same entry point the eval uses, with the same model, prompt version and config. Something like:

```
<eval-runner> --case <failing_case_id> --trace --repeat 3
```

Capture and save these as raw artifacts, with secrets and PII redacted, not as a summary:

1. Input: the receipt image reference and the OCR or text the model actually received.
2. The **raw model response**, before any parsing or normalization.
3. The parsed or normalized record that the post-processing code produced.
4. The final output and the expected (gold) output, plus the assertion diff.
5. Whether all 3 repeats fail the same way. This separates a deterministic bug from model nondeterminism.

### Step 2: Find the first stage that goes wrong

Walk the currency value through each stage and note the first one where it diverges from expected:

```
receipt text -> model extraction (raw currency string/symbol)
            -> normalization (symbol/text -> ISO 4217 code)
            -> defaulting (missing -> employee/company home currency?)
            -> conversion (transaction -> reimbursement currency?)
            -> output serialization (which field is written where?)
```

### Step 3: Write the hypothesis down before going further

Here are the candidate root causes, ranked by how often they cause this kind of bug. Commit to the leading one in writing, then let the trace confirm or reject it.

| # | Hypothesis | Signature in the trace |
|---|---|---|
| **H1 (leading)** | The currency was **inferred or defaulted, not extracted**. Either an ambiguous symbol (`$`, `¥`, `kr`) or a missing currency got silently mapped to a default such as USD or the home currency. | The raw model output shows `$` or nothing, and the normalizer or default logic produced the wrong ISO code. |
| H2 | The model took the currency from the **wrong line**. For example, it read a card-conversion line ("Total charged USD 41.20") when the field means the transaction currency, or the reverse. | The raw model output already has the wrong value, and the receipt contains two currencies. |
| H3 | **Contract ambiguity.** The schema doesn't say whether `currency` means transaction currency or reimbursement currency, so the gold label and the model disagree about what the field means. | The model output is defensible under one reading, and the spec doesn't settle it. |
| H4 | **Field mapping bug** in post-processing, such as writing `currency` from a different key or a stale default. | Raw model output is correct and the final output is wrong. |
| H5 | **The gold label is wrong.** | Reading the receipt by hand matches the model's output. |

Check H5 and H3 first, because they're cheap. If the gold label is wrong or the contract is ambiguous, changing the prompt or code would be "fixing" the wrong thing.

### Step 4: Build a small currency slice *before* fixing

One failing example can't tell us whether a fix generalizes. Add roughly 10–15 targeted cases and record the **baseline** result on them with the current code:

- An explicit ISO code (`EUR 23.50`)
- An ambiguous `$` where country or address disambiguates it (CAD, AUD, USD)
- An ambiguous `$` with **no** disambiguating evidence. Expected: review-needed, not a guess.
- `¥` (JPY vs CNY), `kr` (SEK/NOK/DKK)
- Two currencies on one receipt (local total plus card-converted total)
- No currency anywhere. Expected: review-needed.
- A locale number format (`1.234,50 €`)
- An adversarial or contradictory case, such as an address in one country and a code from another

This also gives the reviewer a named piece of evidence, which is what "robust" should be replaced with (see section 4).

### Step 5: Fix the cause, then verify

The fix depends on what the trace confirms, but for H1 or H2 the likely shape is:

- **Schema:** the model returns `currency_raw` (the verbatim text span), `currency_evidence` (where it appears on the receipt) and `currency_source` ∈ {`explicit_code`, `symbol`, `inferred_from_location`, `absent`}. It doesn't return just a bare `currency`.
- **Deterministic validator** (trusted code, not the model): look the code up in ISO 4217. An ambiguous symbol is accepted only if location evidence resolves it. If it's `absent` or still ambiguous, the record becomes **review-needed**. There's **no silent default** for a money field.
- **Contract:** state explicitly which currency the field means. If both are needed, use two fields: `transaction_currency` and `reimbursement_currency`.

Write the failing test first (the reproduced case plus the slice). Apply the smallest diff, then rerun **all 20 plus the slice**. Decide KEEP / REVISE / ROLLBACK on these rules:

- The failing case passes, or correctly comes back as review-needed.
- None of the 18 passing cases regress. A gain on currency can't buy back a regression elsewhere.
- No case gets a wrong currency silently. Review-needed is acceptable; a confident wrong answer is not.

---

## 3. What I'll paste to the AI coding assistant

This is a template. The bracketed parts get **replaced with the real captured artifacts** from Step 1, not paraphrased. The point is to hand over evidence and a falsifiable hypothesis, not "please investigate".

````text
Context: receipt-to-reimbursement pipeline. Eval: 18/20 pass. Case <case_id>
fails on the `currency` field. I am NOT asking for a general refactor.

Reproduce:
  <exact command, e.g. eval-runner --case <case_id> --trace --repeat 3>
Result: fails 3/3 (deterministic) | <or: fails N/3>

Expected vs actual (assertion output, verbatim):
  <paste diff, e.g. expected currency="CAD", got currency="USD">

Relevant input excerpt (OCR text the model received, redacted):
  <paste the lines containing amounts/currency symbols/address/country>

Raw model response (before parsing):
  <paste>

Normalized record (after post-processing):
  <paste>

Code path for currency (files/functions):
  <extraction prompt/schema location>
  <normalizer function>
  <default/fallback logic>

My hypothesis: the raw model output contains "$" with no ISO code, and
<normalizer/default function> maps "$" to USD by default instead of using
the receipt's location evidence or returning review-needed.
Evidence for it: <the trace line showing "$" in raw output and "USD" after normalization>.

Please:
1. Confirm or reject the hypothesis, citing the specific line(s) in the
   trace/code. If rejected, say which stage first produces the wrong value.
2. Propose the smallest diff that fixes the root cause.
3. Constraints: no silent default currency; ambiguous or absent currency
   must yield a review-needed result; validate against ISO 4217 in code,
   not in the prompt; do not edit gold labels; do not change other fields.
4. Write a failing test for this case plus these slice cases first:
   <list from Step 4>.
5. List any other code paths that could default or overwrite currency.
````

I review whatever the assistant returns: the diff, the test results and anything unintended. Only then do I decide KEEP, REVISE or ROLLBACK. I also keep the actual prompt, the response, the diff and the before/after eval output as the development record.

---

## 4. Answer to the reviewer: "Is it robust?" (interview format)

The structure: **answer, where it lives, reason and trade-off, evidence, limitation (GAP → CURRENT FALLBACK → NEXT STEP), who did what.**

### As I'd answer it *today*, before the fix

> **Answer.** Not shown to be robust yet, and I wouldn't use that word for currency handling right now. What we can say is that it passes 18 of 20 end-to-end examples, and one of the two failures is a wrong currency.
>
> **Where it lives.** Currency is currently decided in `<extraction prompt/schema>` and post-processed in `<normalizer function>`, with a fallback in `<default logic>`. *(Fill in the real locations. I won't claim locations I haven't checked.)*
>
> **Reason and trade-off.** Reading the currency off a messy receipt is an interpretation problem, so a model handles it. Turning that into a valid ISO 4217 code, and deciding what happens when it's ambiguous, should be deterministic code, because it's a money field. I suspect the current version blurs that boundary and lets an ambiguous or missing currency fall through to a default.
>
> **Evidence.** One reproduced failure, case `<case_id>`, with the trace showing `<raw value>` becoming `<wrong value>` at `<stage>`. There's no currency-specific test slice yet. I also don't yet know how many of the 20 examples contain non-default currencies, so I can't quote a currency accuracy number.
>
> **Limitation.**
> - **GAP:** ambiguous symbols (`$`, `¥`, `kr`), receipts with two currencies, and missing currency are untested.
> - **CURRENT FALLBACK:** none that's verified. The risk is a silent wrong currency on a reimbursement.
> - **NEXT STEP:** reproduce and trace the failing case, add a 10–15 case currency slice with a recorded baseline, and add a deterministic ISO 4217 validator that returns review-needed instead of defaulting. Then rerun all 20 plus the slice and check for regressions.
>
> **Who did what.** *(State this truthfully, e.g.)* "The AI assistant generated the original extraction prompt and normalizer. I reproduced the failure, wrote the hypothesis, and am choosing the no-silent-default policy and the test slice."

### What the answer should look like *after* the fix (only if the evidence supports it)

> "Currency is extracted by the model as a verbatim span with a source tag, in `<file>`. It's then validated in code against ISO 4217 in `<function>`. Ambiguous or absent currencies return review-needed rather than a default. Evidence: the currency slice went from `<baseline X/N>` to `<Y/N>`, the original 20 are `<result>` with no regressions, and there were zero silent wrong currencies in either run (`<command / run id>`). Limitation: unseen receipt layouts and rare currencies outside the slice. The fallback is the review-needed path; the next step is adding production-sampled receipts to the slice. The AI drafted the validator; I chose the review-needed policy, wrote the failing tests, and rejected its first version, which defaulted to the home currency."

Every number in angle brackets comes from an executed run. I won't fill them with estimates, and anything that hasn't been run stays labelled **unverified**.

---

## 5. Decision record entry

| Decision | Hypothesis | Alternatives | Why chosen | Evidence | Limitation | Fallback | Status |
|---|---|---|---|---|---|---|---|
| Model extracts the currency span with evidence; code validates ISO 4217 and fails closed to review-needed | Wrong currency comes from silent inference or defaulting of ambiguous or missing values (H1) | Prompt tweak only; regex symbol map with a default; model outputs the final ISO code unvalidated | The money field needs a deterministic rule and no silent guesses; the prompt alone can't enforce that | Pending: trace of `<case_id>`, slice baseline vs variant | Unseen layouts, rare currencies | Review-needed result routed to a human | **PROPOSED** (stays this way until the trace confirms H1 and the reruns pass) |
