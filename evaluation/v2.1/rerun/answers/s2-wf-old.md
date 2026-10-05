# Currency failure in the receipt-to-reimbursement agent: next step and reviewer answer

## TL;DR

- **Scope:** this is one bug, so it gets one debugging loop. It does not justify a redesign. The loop is reproduce, find the stage that goes wrong, state a root-cause hypothesis, fix that cause, rerun everything, then keep or roll back.
- **Next step:** run the failing example alone with a stage-by-stage trace, so we can see where the currency goes wrong. The suspects are OCR, the model's extraction, parsing, normalization, and conversion. **Diagnose before fixing.**
- **Reviewer's question:** honestly, **we can't call it robust yet.** We have one currency failure and no currency-specific test cases. 18/20 tells us very little about currency, because we don't know how many of the 20 receipts even use a non-default currency.

---

## 1. What we know and what we don't

| Known | Unknown (find out before touching code) |
|---|---|
| 18/20 examples pass | Which stage produced the wrong currency |
| 1 failure is a wrong `currency` field | What the wrong value was (e.g. `USD` instead of `CAD`, or `null`, or the symbol `$`) |
| The reviewer is asking about robustness | What caused the **other** failure, and whether it's the same cause |
| | How many of the 20 receipts are non-default currency or have an ambiguous symbol |
| | Whether reimbursement **amounts** depend on currency (conversion), which would make the bug affect money |

The last row sets how serious this is. If the currency is wrong and the amount gets converted (or not converted) because of it, the employee is reimbursed the wrong amount. That makes it a correctness bug with financial impact, not just a wrong label.

## 2. Hypotheses, ranked by how often I've seen them

1. **Silent default:** the prompt, schema or post-processing falls back to `USD` (or the company's home currency) when the model isn't sure.
2. **Ambiguous symbol:** `$` (USD/CAD/AUD/SGD/MXN…), `¥` (JPY/CNY), `kr` (SEK/NOK/DKK). The model picks the most common reading and ignores other clues on the receipt, such as the merchant's address, a tax label like GST/HST/VAT, or the phone number format.
3. **Two currencies on one receipt:** a foreign card slip shows both the original amount and the amount converted to the card's currency. The model takes the currency from one line and the amount from the other.
4. **Normalization overwrite:** the model got it right, but a later mapping step overwrote it (e.g. symbol-to-code lookup, locale formatting, a `.upper()` on `"us$"`).
5. **Schema too loose:** `currency: string` instead of an ISO 4217 enum, so `"$"`, `"Dollars"`, or `"usd "` gets through validation.

Each one is fixed somewhere different (prompt, deterministic resolver, schema, normalizer). That's why the stage has to be pinned down before anyone writes a fix.

## 3. The next debugging step

**Plan**
- *Change:* none yet. This step only diagnoses.
- *Expected result:* a trace showing the first stage where the currency differs from the expected value.
- *Invariant to protect:* the 18 passing cases stay passing. Every supported currency in the output is a valid ISO 4217 code with a source span backing it, or else an explicit `needs_review`.
- *Success check:* we can name the root cause and point to the input evidence that supports it.

**Steps**
1. **Reproduce in isolation.** Re-run the failing example 3–5 times with the same model, prompt version and temperature. Note whether it fails every time or only sometimes. A failure every time points at logic, prompt or schema. An intermittent one points at sampling, which says something about robustness on its own.
2. **Capture the trace at each stage:** raw OCR text → raw model output (before parsing) → parsed object → normalized object → final reimbursement record. Diff each one against the expected output.
3. **Read the evidence.** Does the receipt state the currency explicitly (an ISO code or an unambiguous symbol)? Is it ambiguous? Does it show two currencies? This tells us whether the right answer could be determined from the receipt at all. If it couldn't, the fix is to send the receipt to review, not to make the guess better.
4. **Classify the other failure.** If it's also currency or amount related, the bug is broader than one example.
5. **Count exposure.** Tag all 20 cases by currency situation (home currency, explicit foreign code, ambiguous symbol, two currencies, no marker). This shows how much currency testing 18/20 actually represents.
6. **State a hypothesis** in this form: "Stage X does Y when the input has Z." Then hand the fix over (section 4).

**Rerun command.** Use one obvious command for both the single case and the full suite. If the project doesn't have one yet, add it. Illustrative only, adapt it to your runner:

```
# single case, with trace
<runner> eval --suite receipts --case <failing_case_id> --trace --repeat 5
# full suite (regression gate)
<runner> eval --suite receipts
```

## 4. What I'd paste to the AI coding assistant

Diagnosis and the fix go in separate prompts. The first one is scoped to diagnosis only, so the assistant can't jump straight to a patch that makes this one case pass.

**Prompt 1: diagnose (paste this first)**

```text
Context: Receipt-to-reimbursement pipeline. Eval suite: 18/20 pass.
Failing case: <case_id>. Field `currency` is wrong.
  Expected: <e.g. CAD>   Actual: <e.g. USD>
Receipt evidence: <paste the relevant OCR lines: totals, currency markers,
merchant address, tax labels>

Task: DIAGNOSE ONLY. Do not modify any files yet.
1. Trace where `currency` is produced and transformed: prompt/schema
   definition, model call, parser, normalizer, conversion. List each file
   and function with line numbers.
2. Identify any default/fallback currency, symbol→code mapping, or
   locale logic, and whether ambiguous symbols ($, ¥, kr) are handled.
3. Using the trace I've attached (<paste per-stage outputs>), name the
   FIRST stage where the value diverges from expected.
4. State one root-cause hypothesis in the form
   "Stage X does Y when input has Z", plus what evidence would falsify it.
5. List which of the other 19 cases would exercise the same code path.

Constraints: do not edit expected outputs or eval fixtures; do not
propose a fix that special-cases this receipt or merchant.
```

**Prompt 2: correct (only after I've accepted the hypothesis)**

```text
Accepted root cause: <hypothesis from step 1>.

Make the smallest change that fixes the cause, not the symptom:
- `currency` must be an ISO 4217 code from an allowed enum, or the record
  must be marked `needs_review` with reason `currency_ambiguous` or
  `currency_missing`. No silent default to a home currency.
- Currency resolution order (deterministic code, not the model):
  explicit ISO code on receipt > unambiguous symbol > ambiguous symbol
  disambiguated by extracted merchant-country evidence > needs_review.
- The model extracts raw evidence (currency text as printed, its source
  line, merchant country if present). Code resolves the final value.
- If the receipt shows both an original and a converted amount, the amount
  and currency must come from the same line.
- Conversion (if any) stays deterministic, with a recorded rate source
  and rate date.

Add test cases (fixtures, not just unit mocks) for: explicit code,
unambiguous non-$ symbol, ambiguous $ with country evidence, ambiguous $
with no evidence (expect needs_review), dual-currency card slip,
comma-decimal locale, no currency marker.
Also add unit tests for the resolver and the enum validator.

Then run: <single-case command> and <full-suite command>.
Report: the diff, command output, before/after pass counts, and any
previously passing case that changed. Do not mark done if any check
was not executed.
```

**Review after it comes back:** read the diff myself. It should have no merchant-specific branches, no edited expected outputs, and no widened enum just to let the bad value through. Check the full-suite numbers next to the new currency slice. Choose **KEEP / REVISE / ROLLBACK** based on that evidence. One passing example doesn't count.

## 5. Answer to the reviewer: "Is it robust?"

*Structure: answer → where it lives → reason/trade-off → evidence → limitation/fallback.*

**Answer.**
Not yet, and I wouldn't claim it is. On our 20-example suite, one of the two failures is a wrong currency. We don't have a currency-specific test slice, so the suite can't show the handling is robust either way. Right now "robust" isn't supported by evidence.

**Where it lives and what I'm changing.**
Today the currency is <produced by the model / defaulted in the normalizer; fill in after the diagnosis>. The design I'm moving to splits the work. The **model extracts evidence**: the currency text as printed, which line it came from, and the merchant's country. **Deterministic code resolves the final value** into an ISO 4217 enum, following a fixed order of precedence. If the receipt is genuinely ambiguous, the record goes to **`needs_review`** instead of getting a default.

**Reason and trade-off.**
Reading messy receipts is the uncertain part, so that's what the model does. Mapping a symbol plus a country to a code, validating it, and converting amounts can all be specified exactly, so code does them. Code can be tested and gives the same answer every time, which matters because a wrong currency means a wrong reimbursement. The cost is that more receipts go to human review, at least at first. I'd rather slow down a reimbursement than pay out the wrong amount. I rejected two alternatives. Pure regex/symbol mapping breaks on ambiguous symbols and unusual layouts. A stronger prompt alone is still a guess with nothing enforcing it.

**Evidence I'll bring, versus what I have now.**
- *Have:* 18/20 overall. One currency failure, root cause pending.
- *Will have:* a currency slice (explicit, ambiguous-with-evidence, ambiguous-without, dual-currency, locale formats, missing), with results reported separately per slice. Repeated runs on the failing case to check stability. Full-suite regression results before and after. Pass condition for the slice: zero wrong currencies get through. A receipt flagged `needs_review` counts as a correct outcome. A confident wrong code counts as a critical failure. A better overall average can't cancel that out.

**Limitation and fallback.**
Twenty examples plus a currency slice of maybe 15–30 cases is still small. It won't cover every currency or layout. When the receipt doesn't settle it, the fallback is review, not a guess. In production I'd also track the `needs_review` rate and reviewer corrections by currency. That data only tells us something happened. The controlled eval is what lets me say "fixed."

## 6. Decision record

| Decision | Hypothesis | Alternatives | Why chosen | Evidence | Limitation | Fallback | Status |
|---|---|---|---|---|---|---|---|
| Model extracts the currency evidence; deterministic code picks the ISO 4217 value; ambiguous receipts go to `needs_review` | The failure comes from guessing or a silent default on an ambiguous or unvalidated currency | Prompt-only fix; regex symbol map; leave as is | Reading the receipt is uncertain; mapping and validation can be specified exactly; a wrong currency means a wrong payout | Pending: diagnosis trace, then currency slice plus full-suite rerun | Small eval; unseen currencies and layouts | Typed `needs_review` result | **PROPOSED** |

It moves to VALIDATED only after the rerun commands have actually been run and the currency slice passes with no confident wrong codes.

## 7. Definition of done for this bug

- [ ] Root cause named and backed by a stage-by-stage trace
- [ ] Fix addresses the cause, with no special case for this receipt
- [ ] Currency slice added. Zero confident wrong currencies; ambiguous receipts end up `needs_review`
- [ ] Full suite rerun: no previously passing case regresses, and the other failure is classified
- [ ] Results recorded with the prompt, model and config versions
- [ ] Reviewer answer updated with real numbers in place of "pending"
