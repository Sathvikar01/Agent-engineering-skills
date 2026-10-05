# Receipt-to-reimbursement agent: wrong currency on one example

## TL;DR

- **This is a scoped bug, not a reason to redesign.** Reproduce the one failing example, find which stage produced the wrong currency, and only then fix it. No prompt rewrite and no new agent steps before we know the root cause.
- **Short answer for the reviewer: we can't call it robust yet.** 18/20 on a small, general set says nothing about currency in particular. One currency failure shows there is at least one path where the system picks a currency silently instead of proving it or flagging it.
- **What "robust" should mean here:** the model *proposes* a currency and points to the text that supports it. Trusted code *checks and normalizes* it. Anything ambiguous goes to **review instead of a guess**. A wrong currency in a reimbursement is a money error, so it is a zero-tolerance invariant. It is not something we average away.

---

## 1. What we know and what we don't

| Known | Unknown (find out before fixing) |
|---|---|
| 18/20 examples pass | What the **second** failure is, and whether it's related |
| One output has the wrong `currency` value | Which stage made the error: OCR/text, model extraction, symbol→code mapping, defaulting, FX conversion, or the gold label |
| Reviewer is asking about robustness | How many of the 20 cases test currency at all (probably few, likely mostly home currency) |

The 20-case set looks like a smoke set, not a robustness suite. So the 18/20 can't support a robustness claim in either direction.

---

## 2. Next debugging step (one inner-loop pass)

### PLAN

- **Change:** none yet. This step is diagnosis only.
- **Invariant we want:** the output `currency` is a valid ISO 4217 code supported by evidence on the receipt (or by trusted context such as the card statement). If the evidence is ambiguous, the output is `needs_review`. A guess is never allowed.
- **Success check:** the failing case is reproduced in a test, the root cause is named with evidence, and the full 20-case run shows no regressions after the fix.

### Reproduce and capture the trace for the failing case

Run the single example and save every intermediate value:

1. The raw receipt input (image/PDF) and the OCR/text layer the model actually saw
2. The prompt version, model/version and config used
3. The model's **raw** structured output, before any parsing
4. The output after parsing/normalization (symbol→code mapping, defaults)
5. Any FX conversion step: source currency, target currency, rate, rate date
6. The final output compared with the gold label

Then find the **first stage where the value goes wrong**. That stage is where the fix belongs.

### Root-cause hypotheses and the check that tells them apart

| # | Hypothesis | Check that confirms or rules it out |
|---|---|---|
| H1 | **Ambiguous symbol:** `$` was mapped to USD, but the receipt is CAD/AUD/SGD/MXN/etc. (`¥` JPY/CNY and `kr` SEK/NOK/DKK have the same problem) | Raw model output says `"$"` or `"USD"` with no code on the receipt; merchant address or country points elsewhere |
| H2 | **Silent default:** currency was missing or unparseable and code filled in the home currency | Raw output has a null/empty currency; normalizer has a `default="USD"` (or similar) path |
| H3 | **Conversion mix-up:** amount converted but the field kept the original currency, or the reverse | Amount matches the converted value but currency matches the original (or vice versa) |
| H4 | **Two currencies on one receipt** (e.g. a foreign-transaction line or a "charged in your currency" line), and the model picked the wrong one | Receipt contains two currency/amount pairs; the model's evidence points to the wrong line |
| H5 | **OCR/text issue:** symbol dropped or misread (`€` read as `C`, code cut off) | Text layer differs from the image |
| H6 | **Schema allows free text**, so something like `"US$"`, `"usd"` or `"Euro"` passed through, or failed the comparison | Output isn't a strict ISO code; schema has no enum |
| H7 | **Gold label is wrong** | A second person checks the receipt by hand. If the label is wrong, fix the label, record the change, and touch no code |

Also triage the **other failing example** in the same way. If it involves amount, locale or decimal formatting (e.g. `1.234,56`), it may be the same family of bug.

### CORRECT / REVIEW (after root cause is known)

- Fix the cause at the stage where it happens, with the smallest change that works. Examples: remove the silent default, add an ambiguity rule, or make the schema a strict enum. A broad prompt edit is not the fix.
- Add the failing case as a regression test first. Confirm it fails, then confirm it passes after the fix.
- Rerun all 20 cases plus the new currency slice (section 5). Decide **KEEP / REVISE / ROLLBACK** based on the results. Do not decide from the one case turning green.

---

## 3. What I'd paste to the AI coding assistant

This prompt is scoped so the assistant diagnoses before editing and can't "fix" the problem with a wide prompt rewrite.

```text
Context: Receipt-to-reimbursement pipeline. Eval: 18/20 pass. Case <CASE_ID> outputs
currency=<ACTUAL>, expected <EXPECTED>. Attached: receipt text layer, raw model output,
normalized output, final output, prompt/model version.

Task (diagnose first, do NOT fix yet):
1. Reproduce <CASE_ID> with the current code and config. Show the exact command and output.
2. Trace the currency value through each stage: OCR text -> model raw output -> parsing ->
   symbol/code normalization -> defaults -> FX conversion -> final output. Name the FIRST
   stage where it diverges from the expected value, and quote the code/line responsible.
3. Report which hypothesis fits, with evidence: ambiguous symbol mapping, silent default,
   conversion field mismatch, multiple currencies on the receipt, OCR error, free-text
   schema, or wrong gold label.
4. Search for any other code path that assigns a currency without evidence (defaults,
   fallbacks, locale assumptions) and list them.

Constraints:
- Do not edit the system prompt or add model calls in this step.
- Do not change gold labels; if you think the label is wrong, say so and stop.
- Do not invent results; if you couldn't run something, say so.

After I confirm the root cause, the next step will be: write a failing regression test for
<CASE_ID>, make the smallest fix at the diverging stage, rerun the full eval suite, and report
before/after per case plus any regressions.
```

---

## 4. The reviewer's question, in technical-interview format

> **Q: Is the currency handling robust?**

**Answer.** Not yet, and the current evidence can't show it either way. We pass 18/20 overall, but one case returns the wrong currency. That tells us at least one path assigns a currency without proving it. In a reimbursement flow, a wrong currency means a wrong payout. So I treat this as a correctness invariant. It is not an accuracy number we can average out.

**Where it lives / what I'm changing.** Currency is decided across a few stages: the model extracts it from the receipt, code normalizes it to a currency code, and code may convert it to the reimbursement currency. I'm reproducing the failing case and tracing the value through those stages to find where it goes wrong. My leading suspects are mapping a bare `$` to USD and a silent default to home currency. The target design is:

- **Model proposes:** `currency_evidence` (the exact text span, e.g. `"CA$"`, `"€"`, `"Total EUR"`) plus a candidate ISO code.
- **Code validates:** strict ISO 4217 enum; the evidence span must exist in the receipt text; symbol→code mapping happens in code; a symbol that maps to several currencies (`$`, `¥`, `kr`) is resolved only by corroborating context (merchant country/address, a printed code, the card-statement currency). If nothing corroborates it, the result is `needs_review`.
- **Code converts:** FX conversion and reimbursement arithmetic run in deterministic code. The output records the rate, its source and its date. The model never does that math.
- **No silent defaults:** a missing currency means review. It never means home currency.

**Why / trade-off.** Reading a messy receipt is the uncertain part, so a model does it. Mapping, conversion and the payout amount can be fully specified, so code does them. The cost is more items going to human review when receipts are ambiguous. I'd rather pay that than make a silent wrong payment. I rejected two alternatives. Regex-only extraction breaks on layout and locale variety. Asking the model to "be more careful" with currency in the prompt is guidance, not enforcement, and gives us nothing to verify.

**Evidence.** Today we have one reproduced failure (once the trace is done) and an overall 18/20. We do **not** have a currency-specific measurement yet. The 20 cases weren't built to test currency, so I'm not claiming any robustness number. After the fix I'll report currency-field accuracy, the abstain/review rate and the count of silent wrong-currency outputs from the slice below, compared before and after.

**Limitation / fallback.** Receipts with no currency marker and no corroborating context will still be ambiguous. Those go to review with the reason attached, and a person decides. New locales or formats we haven't tested remain a risk until the eval slice covers them. If the fix causes regressions elsewhere in the suite, we roll it back and keep the review route as the safe default.

---

## 5. Evals needed before anyone says "robust"

Add a **currency slice** of real or realistic receipts, labelled by someone who checked them:

- Ambiguous symbols: `$` as USD/CAD/AUD/SGD/MXN, `¥` as JPY/CNY, `kr` as SEK/NOK/DKK
- Explicit codes in various positions (`USD 12.00`, `12,00 EUR`, `CA$`)
- Locale number formats (`1.234,56`, `1 234,56`, zero-decimal currencies such as JPY)
- No currency marker at all
- Two currencies on one receipt (foreign transaction / dynamic currency conversion lines)
- OCR-degraded symbols
- Adversarial: receipt text claiming a different currency than the totals support

**Metrics and gates:**

- **Silent wrong currency: 0.** This is a hard gate, and a better average can't make up for missing it.
- Currency accuracy on cases that should resolve automatically
- Review rate on ambiguous cases. Ambiguous cases *should* go to review, and over-escalating on clear ones is a cost we track.
- No regressions on the existing 20

**One rerun command.** Use whatever the project already has. Shaped like this:
`<eval-runner> --suite receipts --slice currency --compare baseline`
Record the prompt/model/config versions with every run.

---

## 6. Decision record

| Decision | Hypothesis | Alternatives | Why chosen | Evidence | Limitation | Fallback | Status |
|---|---|---|---|---|---|---|---|
| Diagnose the single failure before changing anything | Error comes from one identifiable stage | Prompt rewrite; adding a "verifier" model call | Cheapest step that tells hypotheses apart; avoids masking the cause | Pending trace of the failing case | Doesn't cover the untested currency space | n/a | PROPOSED |
| Model proposes currency with an evidence span; code normalizes, checks and converts | Wrong currency comes from unverified assignment (guess/default) | Model-only currency; regex-only | Reading is uncertain; mapping and arithmetic can be specified | None yet; needs the currency slice | Receipts with no marker and no context | `needs_review` with reason | PROPOSED |
| Silent wrong currency treated as a zero-tolerance gate | Money errors can't be averaged away | Overall accuracy threshold only | Each failure is a direct financial error | n/a (policy) | More reviews needed | Human review | PROPOSED |

Nothing here is **VALIDATED** until the trace, the regression test and the slice eval have actually been run.

---

## Next step

Run the single-case reproduction with full trace capture, using the prompt in section 3. Name the diverging stage and root cause. Then write the failing test, apply the smallest fix, and rerun the full suite plus the new currency slice before answering the reviewer with numbers.
