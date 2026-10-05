# Invoice Extraction: Variant A vs Variant B — Comparison and Release Decision

## TL;DR

**Decision: HOLD. Do not ship B yet.** We have one number per variant (89% vs 91% "average field match") from a single run on a 200-document dev set. That isn't enough to back a release, and it gives no support at all for "B is more robust." Before deciding we need per-field accuracy, whole-record exact match, a paired per-document comparison with uncertainty, repeated runs, regression slices, and a run on a frozen holdout with acceptance thresholds agreed **before** anyone looks at the results. B may well turn out better. We just haven't shown it.

---

## 1. What the current evidence does and doesn't support

| Claim | Evidence we have | Status |
|---|---|---|
| B scores higher than A on the dev set | 91% vs 89% average field match, one run each, same 200 docs | **Observed**, but the metric isn't fully defined and we have no uncertainty estimate |
| B extracts invoices more correctly | Needs per-field and whole-record correctness, paired | **Unmeasured** |
| B is "more robust" | No slice results, no repeated runs, no perturbed or adversarial inputs | **Unmeasured.** Treat it as a hypothesis, not a finding |
| B is safe to ship | No thresholds, no holdout, no severity weighting, no latency or cost numbers | **Unmeasured** |

### Why 91 vs 89 isn't enough by itself

1. **The metric is ambiguous.** "Average field match" could mean the mean of five per-field accuracies, the mean per-document fraction of matching fields, or the pooled share of 1,000 field slots (200 × 5). These can differ, and none of them is a document success rate. A 2-point gain in average field match doesn't tell us how many more invoices B gets *fully* right. That could be anywhere from zero to about 20.
2. **An average can hide one systematically wrong field.** Suppose B improves vendor-name normalization by 15 points but regresses `total` by 5. Its average goes up while the invoices that actually matter get worse. Five equally weighted fields also ignore consequence: a wrong `currency` or `total` costs far more than a vendor-name spelling variant.
3. **The gap may be inside the noise.** 2pp of 1,000 field slots is about 20 field-level differences. Those slots cluster within documents (one bad OCR page can break three fields at once), so the effective sample size is well below 1,000. One run per variant also mixes the real variant effect with run-to-run sampling variance. We need paired per-document differences and a confidence interval before calling this a gain.
4. **The dev set may be optimistic for B.** If B's prompt, few-shot examples, or normalization rules were iterated against these 200 documents, B has been fit to them, and its dev score will overstate production performance. The deciding comparison has to run on a frozen holdout that neither variant was tuned on.
5. **Leakage hasn't been ruled out.** If any few-shot example, retrieval store, or memory available to either variant contains dev-set documents or their gold labels, the scores are contaminated.

---

## 2. Freeze the eval contract before rerunning

### 2.1 Task population and success definition

- **Population:** invoices as they arrive in production. Record the mix: digital PDF vs scanned vs photo, single vs multi-page, languages, currencies, vendor long tail, credit notes, pro-forma invoices, and documents that aren't invoices at all.
- **Per-field success:** the extracted value equals gold after declared normalization:

| Field | Match rule | Severity if wrong |
|---|---|---|
| `vendor` | Normalized match: case-folded, legal suffix stripped (Inc/Ltd/GmbH), whitespace collapsed, or matched against the vendor master ID | Medium |
| `date` | Exact ISO-8601 after parsing. The invoice date must not be confused with the due date or delivery date. Ambiguous formats (03/04) are resolved by locale rules | Medium–High |
| `currency` | Exact ISO-4217 code | **Critical.** It silently changes the meaning of `total` and `tax` |
| `total` | Exact decimal to minor units, and must be the gross amount payable | **Critical** |
| `tax` | Exact decimal to minor units. 0 is valid only if the document shows zero tax. Null means "not present" | High |

- **Whole-record success:** all five fields correct. Report this next to per-field accuracy.
- **Abstention:** when a field isn't present or isn't legible, the correct output is `null` plus a reason, not a guess. Score this explicitly: correct null, wrong null (missed extraction), and hallucinated value (a value emitted where gold is null). A hallucinated `total` is worse than a null `total`, because a null goes to human review.
- **Cross-field consistency checks (executable):** `tax ≤ total`; the currency symbol or code appears in the source; the extracted total appears somewhere in the document text (a grounding check); the date falls in a plausible range.
- **Prohibited behavior:** if the agent writes to an ERP or AP system, any write the authorization policy doesn't allow is a critical violation, whatever the field accuracy. If it only emits fields, this doesn't apply, but record that explicitly.
- **Budgets:** p95 latency and cost per successfully extracted invoice, retries and failures included.

### 2.2 Gold cases

Build a versioned case set. Each case has: an ID, the source document (with provenance: vendor, source channel, received date), gold values per field (null where absent), labeler and review status, and a weight based on traffic share and consequence.

Include on purpose:
- Representative cases sampled to match production mix.
- Boundary cases: multi-currency documents, totals with and without tax, discount lines, credit notes (negative totals), multi-page invoices with the total on the last page, handwritten corrections, low-quality scans, and non-English invoices.
- Abstention cases: a missing tax line, an unreadable total, a document that isn't an invoice.
- Adversarial cases: a "Total" label next to a subtotal, several dates, a remit-to address that differs from the vendor, text in the invoice that reads like instructions to the model.
- Known incidents: every production extraction error that's been reported so far.

### 2.3 Splits and leakage control

- **Split by vendor (and by time where possible), not by document**, so near-duplicate invoices from the same vendor template don't end up on both sides of the split.
- Keep the existing 200 documents as the **dev** split. Freeze a separate **holdout** (I'd suggest at least 400–500 documents, stratified by slice) that nobody tunes against.
- **Runtime-input exposure manifest:**

| Material | Visible to agent at runtime? |
|---|---|
| Document image/PDF and OCR text | Yes |
| Vendor master list (if used in production) | Yes |
| Few-shot examples | Yes, but only from a training pool disjoint from both dev and holdout |
| Gold labels, labeler notes, scoring annotations | **No, grader only** |
| Holdout documents | **No.** Not in prompts, retrieval, memory, or tuning |

- **Leakage assertion:** before each run, dump the assembled model input for a sample of cases. Check programmatically that no gold value from a grader-only file appears in few-shot blocks or retrieved context unless it comes from the document itself. Also confirm that no dev or holdout document hash appears in the few-shot pool. A sealed split doesn't prove this on its own, so check the actual inputs.

---

## 3. How to score the comparison

### 3.1 Metrics to report for each variant

1. **Per-field accuracy** for each of the five fields, with 95% CIs.
2. **Whole-record exact match** (all five fields correct).
3. **Severity-weighted error rate** (currency and total weighted highest).
4. **Abstention quality:** hallucinated-value rate, missed-extraction rate, and correct-null rate per field.
5. **Schema and consistency pass rate.** This is scaffolding only: a schema-valid output can still be wrong.
6. **Operational:** p95 latency, cost per correctly extracted record, and retry/error rate.

Keep the denominators explicit: per-field accuracy is over 200 (or N) documents, and the pooled figure is over 5N field slots. Don't turn one into the other.

### 3.2 Paired comparison

Both variants run on the same documents, so compare them **per document**:

- Per field, build the 2×2 table of A-correct/B-correct. The informative counts are the discordant pairs: "A right, B wrong" and "A wrong, B right." Use McNemar's test or a paired bootstrap on those counts.
- For the aggregate, bootstrap over **documents**, not field slots, to respect the within-document clustering. Report the CI of the B − A difference.
- **Repeat each variant several times (e.g. 5 runs)** at production sampling settings. Report the mean and spread per document. Separate across-document variation (some invoices are hard) from run-to-run variation (the model is stochastic). A seed doesn't guarantee provider determinism. If a document flips between right and wrong across B's runs, that's evidence *against* robustness.

### 3.3 Turning "robust" into something measurable

If the claim is that B is more robust, define it up front and test it:

- **Slice robustness:** B's per-field accuracy is no worse than A's on any slice (scanned, multi-page, non-English, multi-currency, credit notes, long-tail vendors), not just on the aggregate.
- **Run-to-run stability:** the share of documents with identical outputs across repeated runs.
- **Perturbation robustness:** accuracy under controlled degradations such as rotation, lower DPI, JPEG compression, and page reorder.
- **Adversarial robustness:** behavior on decoy totals and on injected instruction text.

Until these are measured, write "B robustness: unmeasured" in the decision record.

### 3.4 Failure attribution

For every case where a variant is wrong, assign the **earliest decisive** failure class:

| Class | Invoice example |
|---|---|
| Context / OCR | Total on page 3 was never read; low-quality scan garbled digits |
| Task misunderstanding | Took the subtotal as the total; took the due date as the invoice date |
| Grounding / hallucination | Emitted a tax amount that appears nowhere in the document |
| Normalization / schema | Correct value, wrong format ("1.234,56" parsed as 1.23456; "$" mapped to USD on a CAD invoice) |
| Abstention | Guessed instead of returning null, or returned null when the value was clearly present |
| Execution / recovery | Timeout, retry produced a different answer, malformed output |

Counting the downstream symptoms separately would double-count. A misread page that breaks total and tax is one failure, not two.

### 3.5 Model grader

Mostly unnecessary here. Every field can be checked deterministically after normalization. The only exception might be vendor-name equivalence when no vendor master exists. If a grader is used there, blind it to variant identity, give it a rubric and examples, calibrate it against human labels on a sample, and log any disagreements.

---

## 4. Acceptance thresholds (agree these before rerunning)

These are proposals for the team to ratify **before** the holdout run. Once results are in, the thresholds don't move.

B ships only if **all** of these hold on the frozen holdout:

1. **No critical-field regression:** for `currency` and `total`, the lower bound of the 95% CI on (B − A) per-field accuracy is ≥ −0.5pp (non-inferiority). B can't trade money-field accuracy for gains elsewhere.
2. **No high-field regression:** for `tax` and `date`, the point estimate of B − A is ≥ 0 and the CI lower bound is ≥ −1pp.
3. **Real improvement:** whole-record exact match B − A > 0, with the CI excluding 0, **or** a severity-weighted error reduction whose CI excludes 0.
4. **Hallucinated-value rate** on `total` and `tax` is no higher than A's.
5. **Slice gates:** no predefined slice shows a per-field regression of more than 3pp on `currency`, `total`, or `tax`, given at least 30 documents in the slice. Smaller slices get flagged for review rather than auto-passed.
6. **Stability:** B's run-to-run disagreement rate is ≤ A's.
7. **Operational bounds:** B's p95 latency ≤ 1.2× A's and cost per correct record ≤ 1.2× A's. Adjust both to the business budget.
8. **Authority (if the agent writes downstream):** zero observed unauthorized writes. Zero observed is a test result for this case set, not a guarantee.

If B improves the average but fails any of 1, 2, 4, 5, or 8, it's **rejected**, whatever the aggregate says.

---

## 5. Reproducibility manifest (record this with every run)

- Dataset name, version, and split hash (dev and holdout separately)
- Model identifier (exact version string), temperature/top-p, max tokens
- Prompt version, few-shot pool version, output schema version, and normalization-rules version for each variant
- OCR/parsing engine and version
- Tool or vendor-master snapshot, if used
- Run timestamp and environment
- Number of repeats per document
- **What actually differs between A and B.** If B changes more than one thing (for example a new prompt *and* new few-shots *and* a new normalizer), the 2pp can't be attributed to any one of them. Run ablations one change at a time so we know which change matters and whether the extra complexity is worth it.

### One rerunnable command

The team should have a single entry point along these lines:

```
eval run --suite invoice-extraction --split holdout --variants A,B --repeats 5 \
         --reset-fixtures --out results/<date>-A-vs-B.json
```

It should reset fixtures, run both variants, score per field and per record, compute the paired CIs and slice tables, and write a report. The workflow is run → inspect → change → rerun → compare.

---

## 6. Release decision record

```
Hypothesis:        Variant B extracts invoice fields more accurately and more robustly than A.
Changed variable:  <list exactly what differs between A and B>
Dataset:           invoice-dev v<?> (200 docs) — holdout not yet built
Evidence so far:   Avg field match 91% (B) vs 89% (A); single run each; metric definition
                   unspecified; no per-field, whole-record, paired, CI, slice or repeat data.
Robustness claim:  UNMEASURED — no run, metric or dataset supports it.
Safety/authority:  Not evaluated (confirm whether the agent writes downstream).
Latency/cost:      Not reported.
Leakage check:     Not performed.
Conclusion:        REVISE — hold release pending holdout evaluation against thresholds in §4.
```

### Next steps, in order

1. Pin down what "average field match" means, then recompute **per-field accuracy and whole-record exact match** for A and B on the existing dev run outputs. This is cheap and may settle the question quickly, e.g. if B regressed on `total`.
2. List exactly what differs between A and B, and check whether B was tuned on the dev set.
3. Run the leakage assertion on the assembled inputs for both variants.
4. Ratify the thresholds in §4.
5. Build and freeze the vendor-split holdout, with slices and abstention and adversarial cases.
6. Run both variants on the holdout with 5 repeats each. Produce paired CIs, slice tables, failure attribution, and latency and cost.
7. Make the go/no-go call against the thresholds. If B passes, ship behind a shadow or canary that compares B's outputs to A's on live traffic. Keep production telemetry separate from the formal eval result, and keep A as the rollback.

### What to tell the teammate

B might be better, and the dev result is encouraging enough to justify a proper evaluation. Right now, though, "more robust" has nothing behind it: we haven't measured robustness at all, and a 2-point average on a set B may have been tuned on can hide a regression on the fields that cost money. Step 1 takes an afternoon with the outputs we already have, so let's start there.
