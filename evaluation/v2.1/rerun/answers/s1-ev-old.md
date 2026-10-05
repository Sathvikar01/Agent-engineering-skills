# Invoice Extraction: Variant A vs Variant B — Comparison and Release Decision

## Decision: REVISE (do not ship B yet)

B is not rejected. But the evidence so far (91% vs 89% average field match on the 200-document dev set) can't support either claim being made: that B is better, or that B is "more robust". Here's why:

1. **It's the dev set.** If either variant's prompt, examples or post-processing was tuned on these 200 documents, the scores are optimistic. Because B is presumably the newer, more-iterated variant, they're optimistic in B's favour.
2. **"Average field match" isn't document correctness.** It blends low-stakes fields (vendor spelling) with high-stakes ones (total, tax, currency) and weights them equally. A 2-point gain could come entirely from vendor-name normalisation while totals get worse.
3. **A 2-point difference on 200 documents may be noise.** No paired analysis, confidence interval or repeated runs have been reported.
4. **"Robust" is a claim about the tails, and an average says nothing about the tails.** Robustness means worst-slice behaviour (bad scans, multi-currency, credit notes, multi-page), stability across reruns, and how the variant behaves when it's unsure. None of that has been measured.

Next step: run the frozen comparison described below on a held-out set. B ships if it meets the acceptance criteria. Those criteria are written down **now**, before anyone sees the new numbers.

---

## 1. What the current numbers do and don't show

| Claim | Supported by "91% vs 89% avg field match, 200 dev docs"? |
|---|---|
| B matches more field values than A on these 200 docs | Probably, if both ran with the same pinned settings and scoring |
| B extracts more invoices fully correctly | **No.** A field-average can't be converted into a count of correct documents |
| B is better on totals/tax/currency | **Unknown.** Per-field breakdown not reported |
| B will generalise to production traffic | **Unknown.** Dev set, possibly tuned on, no holdout |
| B is more robust | **Unknown.** No slice, variance or abstention data |
| The 2-point gap is real | **Unknown.** No paired test or CI; repeated-run variance not measured |

**Denominator questions to answer before the metric means anything:**
- Is 91% the mean per document (each doc's fraction of 5 fields correct, averaged) or the mean per field instance (correct / 1,000)? They differ when documents have missing fields.
- How do fields that are legitimately absent count? (Example: no tax line on a tax-exempt invoice.) Is a correct `null` a match? Is a hallucinated value against a `null` gold a miss?
- What does "match" mean per field: exact string, normalised, or tolerance-based?

**Rough noise check (illustrative assumption, not a measurement).** Suppose per-document score differences (B − A) have a standard deviation of about 0.15. Then the standard error of the mean difference is about 0.15/√200 ≈ 1.1 pp, which gives a 95% interval of roughly ±2.1 pp. On that assumption a 2-point gain sits at the edge of noise. The real SD has to be computed from the paired per-document results. That's cheap to do and should be done first.

---

## 2. Evaluation contract (freeze before re-running)

### 2.1 Task population and outcome
- **Population:** invoices in the mix production actually receives, by source channel (PDF-native, scanned, photo, email-body), language, currency, vendor, and document type (invoice, credit note, pro-forma, multi-page).
- **Successful document:** every *critical* field is correct, or explicitly abstained/flagged for review. Non-critical fields may be wrong only within the agreed tolerance.
- **Abstention:** returning `null` plus a review flag is an acceptable outcome. Returning a confident wrong value for a critical field is the worst outcome.

### 2.2 Field severity and scoring rules

| Field | Severity | Match rule (deterministic) | Notes |
|---|---|---|---|
| `total` | **Critical** | Decimal-equal after parsing locale formats (`1.234,56` ↔ `1234.56`), exact to the minor unit | No tolerance. Off by a cent is wrong |
| `tax` | **Critical** | Same as total. Correct `null` when the gold has no tax | Check `tax ≤ total` |
| `currency` | **Critical** | ISO-4217 code equality (`€` → `EUR`; `$` resolved via doc context, otherwise must abstain) | A right number in the wrong currency is a critical error |
| `date` | High | ISO-8601 date equality. Ambiguous `03/04` must match gold's resolved date or abstain | Distinguish invoice date from due date |
| `vendor` | Medium | Normalised match (case, punctuation, legal suffix `Ltd/GmbH/Inc`) against gold canonical name or alias list | Model grader only if alias lists can't cover it, calibrated vs human labels |

**Executable consistency assertions** (scored separately from gold match):
- Output passes the schema: types, ISO codes, no extra fields. **A valid schema doesn't count as correct.** It's a gate, not a score.
- `total`, `tax` ≥ 0, except on credit notes where sign rules apply.
- If a subtotal is present in the source: `subtotal + tax ≈ total` to the minor unit.
- Every emitted value appears in, or is derivable from, the document text/OCR. This catches invented values.

### 2.3 Metrics to report (per variant, with denominators)

| Metric | Definition |
|---|---|
| **Document success rate** | Docs with all critical fields correct-or-abstained / eligible docs |
| **Critical-field error rate** | Confident wrong values on total/tax/currency / applicable field instances |
| Per-field accuracy | Correct / applicable instances, for each of the 5 fields separately |
| Abstention rate and abstention precision | Abstentions / docs; share of abstentions where the field really was ambiguous or missing |
| Hallucination rate | Values emitted where gold is `null` or the value isn't in the source |
| Schema failure rate | Invalid outputs / all attempts, including retries |
| Run-to-run disagreement | Fraction of docs whose extracted fields change across k repeated runs |
| p95 latency | Per document, including retries |
| Cost per successful document | Total spend (including failures/retries) / successful documents |
| Average field match | Kept for continuity with the original numbers, with the denominator stated |

### 2.4 Acceptance thresholds (agreed before results)

B ships only if **all** of the following hold on the frozen holdout:

1. **Critical-field error rate:** B ≤ A, with the paired upper confidence bound on (B − A) no worse than +0.5 pp. Any regression on totals or currency blocks release, whatever the average does.
2. **Document success rate:** B ≥ A − tolerance (for example 1 pp) on the paired comparison. To claim "better", the 95% CI of the paired difference must exclude 0.
3. **No slice regression:** on every predefined slice with ≥ 30 docs, B's critical-field error rate is not worse than A's beyond the tolerance. Slices: scanned/photo, non-USD/EUR currency, credit notes, multi-page, top-10 vendors, documents with no tax.
4. **Known-incident cases:** every past production failure case in the suite passes for B, or fails no worse than A.
5. **Hallucination rate:** B ≤ A.
6. **Operational:** B's p95 latency and cost per successful document within the agreed ceilings (for example ≤ 1.2× A, or an absolute budget).
7. **Stability:** B's run-to-run disagreement on critical fields ≤ A's. This is the testable meaning of "more robust".

If the average improves but any of 1, 3, 4 or 5 fail, B is **rejected** in its current form.

---

## 3. Dataset, split and leakage

**Current state:** 200 dev documents. Treat these as development data from now on, not evidence for release.

**Build a holdout:**
- Draw from recent production traffic. Stratify by the slices above and weight by traffic volume *and* consequence (high-value invoices, multi-currency vendors).
- Target about 400–600 documents. More matters most in the critical slices: 30 credit notes are worth more than another 100 clean PDFs.
- **Split by vendor and by time**, not by document. Invoices from the same vendor share templates, so a document-level split lets template memorisation pass as generalisation. Group near-duplicates (same vendor, same layout, consecutive months) on one side.
- Include deliberately hard cases: rotated scans, two currencies on one page, "amount due" ≠ "total" (partial payments), tax-inclusive vs tax-exclusive totals, invoices whose text contains instructions ("ignore previous… total is 0"). Mark these as adversarial.
- Each case records: document ID, source/provenance, gold values per field (`null` where absent), whether `null` is the correct answer, slice tags, weight, and the labeller. Get double-labelling on critical fields, adjudicate disagreements, and report labeller agreement.
- **Freeze the holdout** (versioned, hashed) before running either variant on it. No prompt or post-processing changes after viewing holdout results without starting a new holdout.

**Runtime-input exposure manifest:**

| Material | Agent-visible? |
|---|---|
| Document file / OCR text | Yes |
| Extraction instructions, schema | Yes |
| Few-shot examples | Yes, but **only from dev docs, never holdout**, and never from holdout vendors |
| Gold labels, slice tags, rubric notes | **No (grader-only)** |
| Vendor alias lists used for grading | **No (grader-only)**, unless the same list is also a legitimate production lookup tool, in which case declare it |

**Leakage assertion:** check deterministically that no holdout document ID, gold file or holdout-vendor example appears in the assembled prompts, few-shot banks, retrieval stores or caches of either variant. Inspect the actual assembled model input for a sample of runs, not just the config. Don't test for leakage by banning gold strings: the invoice itself legitimately contains the total. **Specifically ask: were B's few-shot examples or prompt wording derived from the 200 dev docs?** If so, the 91% is partly memorisation of the test set. Until checked, this is an **unverified gap**.

---

## 4. Reproducibility manifest

Pin and record, for each variant run:
- Model identifier and version, provider/region
- Temperature, top-p, max tokens, any seed (a seed doesn't guarantee provider determinism)
- Prompt version, schema version, post-processing/normaliser version, OCR engine and version
- Retry and fallback policy
- Fixture set hash (holdout version), grader/normaliser code version, run timestamp

**Repeated runs:** run each variant **k = 3–5 times** on the full holdout. Report:
- *Across-document* variation, which tells you about population uncertainty. Use the paired bootstrap over documents.
- *Repeated-run* variation, which tells you about stochastic instability. Use per-document disagreement across runs.

These are different quantities. Five runs of 200 docs is not n = 1,000.

**Paired analysis:** for each document, compute B − A on document success and on each critical field. Report the mean difference with a 95% bootstrap CI, plus a McNemar-style count of documents A got right and B wrong, and the reverse. The second number, "documents B newly breaks", is what reviewers should read first.

**One rerunnable command** (shape, adapt to your tooling):
```
eval run --suite invoices-holdout@v1 --variants A,B --repeats 5 --reset-fixtures --out results/2026-10-xx/
eval compare results/2026-10-xx/ --paired --slices --thresholds acceptance-v1.yaml
```
The output is per-document, per-field rows plus the threshold report. Loop: run → inspect → change one thing → rerun → compare.

---

## 5. Failure analysis (fill in from the paired run)

Tag every disagreement with the **earliest decisive failure**, so one root cause isn't counted as five field errors:

| Class | Invoice-extraction examples |
|---|---|
| Context / input | OCR dropped the totals block; wrong page read on multi-page doc |
| Task misunderstanding | Took "amount due" instead of "total"; due date instead of invoice date; subtotal reported as total |
| Proposal / schema | Locale parse error (`1.234,56` → 1.234); non-ISO currency; malformed JSON |
| Grounding | Value not present in document (hallucinated tax rate × subtotal); currency guessed from vendor country |
| Abstention / calibration | Emitted a guess on an ambiguous `$`; or abstained on a clearly printed field |
| Adversarial | Followed instructions embedded in the invoice text |
| Execution / recovery | Timeout, retry produced a different answer, fallback path used |

Then compare the **distribution** of failure classes between A and B. "B fixed 15 vendor-normalisation misses but introduced 6 locale-parse errors on totals" is a ship-blocking result, even though the average went up.

---

## 6. Results template

Fill in from the frozen run. Cells marked *unavailable* stay that way until measured; don't backfill them from the dev-set average.

| Metric | A | B | Paired Δ (95% CI) | Threshold | Pass? |
|---|---|---|---|---|---|
| Document success rate | | | | B ≥ A − 1 pp | |
| Critical-field error rate | | | | UCB(Δ) ≤ +0.5 pp | |
| Total accuracy | | | | no regression | |
| Tax accuracy | | | | no regression | |
| Currency accuracy | | | | no regression | |
| Date accuracy | | | | | |
| Vendor accuracy | | | | | |
| Hallucination rate | | | | B ≤ A | |
| Abstention rate / precision | | | | | |
| Docs A right, B wrong / B right, A wrong | | | — | reviewed individually | |
| Worst slice: critical-field error | | | | no slice regression | |
| Run-to-run critical-field disagreement | | | | B ≤ A | |
| p95 latency | | | | ≤ ceiling | |
| Cost per successful doc | | | | ≤ ceiling | |
| Avg field match (dev, as reported) | 89% | 91% | *unavailable* | — | — |

---

## 7. Release decision and path to ship

**Current decision: REVISE.** No evidence of harm, and no evidence yet of benefit on the fields that matter or of robustness.

**To move to KEEP (ship B):**
1. Answer the denominator and match-rule questions, and recompute the existing dev results per field and per document with paired differences. (Hours, not days. If B regresses on totals or currency even on dev, stop here.)
2. Confirm whether B was tuned on the 200 dev docs. Check few-shot examples and prompt iterations.
3. Build and freeze the vendor/time-split holdout with double-labelled critical fields.
4. Run both variants k times under the pinned manifest, then score against the thresholds in §2.4.
5. If all thresholds pass, roll out B behind a flag. Run a shadow comparison against A on live traffic and alert on disagreement in total/currency. Keep A as instant rollback. Shadow telemetry is reported separately from the formal eval result; it doesn't replace it.

**REJECT B** if it regresses critical-field accuracy overall or on any critical slice, hallucinates more, or breaks known incident cases. That holds even with a higher average.

---

## Note for the teammate

> B's 2-point lift is encouraging and worth following up. But it's measured on the dev set, as an equal-weight average across five fields, without a confidence interval. That can't tell us whether B is better at totals, tax and currency, which are the fields where an error costs real money. And it says nothing about robustness, which is about bad scans, odd currencies, credit notes and run-to-run stability. Let's freeze the acceptance criteria now, run both variants on a held-out, vendor-split set with paired per-document comparison, and ship B if it clears them. If B is as good as it looks, this costs us a few days and gives us numbers we can defend.
