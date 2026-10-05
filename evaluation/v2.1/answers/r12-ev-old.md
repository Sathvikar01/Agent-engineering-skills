# Invoice Extraction: Variant A vs Variant B — Comparison and Release Decision

## TL;DR

**Decision: HOLD (REVISE).** Don't ship B yet, and don't reject it either.

The evidence so far is one number per variant: 91% vs 89% "average field match" on the 200-document **dev** set. That number can't support a ship decision, and it says nothing about robustness, for four reasons:

1. **The gap may be noise.** We have no paired per-document comparison, no uncertainty estimate and no repeated runs.
2. **It's the dev set.** If either variant was tuned against these 200 documents, the score is biased upward. B is usually the variant that got tuned more.
3. **"Average field match" isn't the quantity we care about.** It treats a wrong vendor spelling the same as a wrong total. It also doesn't tell us how many invoices came out fully correct.
4. **"More robust" is a claim about slices and stability.** A pooled average can't show either one.

B may well be better. The rest of this note sets out what we need to show that, and the acceptance contract to agree on **before** we look at the new numbers.

---

## 1. What the current numbers do and don't say

| Claim | Supported by "91% vs 89% avg field match"? | Why |
|---|---|---|
| B extracts more fields correctly on these 200 docs, in one run | Weakly | Single run, no interval, unknown match rules |
| B is better on production traffic | No | Dev set, possibly tuned on, representativeness unknown |
| B produces more fully correct invoices | No | A field average can't be converted into a document success count |
| B is better on the fields that cost money (total, tax, currency) | No | Unweighted average over 5 fields |
| B is "more robust" | No | Robustness means performance on hard slices plus run-to-run stability. Neither was measured |
| B is safe to ship | No | We have no gates for hallucinated values, schema failures, latency or cost |

### The denominator problem

5 fields × 200 docs = **1,000 field slots**. Two points is about **20 field slots**. That's about 20 fields across 200 documents. The aggregate also doesn't tell us:

- Is it 20 documents each gaining one field, or 4 documents gaining all five?
- How do missing fields score? (For example, a receipt with no tax line: is a correct `null` a match? Is a hallucinated `0.00` a match?)
- How do near-misses score? (`2026-03-04` vs `04/03/2026`, `USD` vs `$`, `1,234.50` vs `1234.5`, `ACME Corp` vs `Acme Corporation Ltd.`)
- Did the two variants fail on the same documents or on different ones?

### Is +2 points distinguishable from noise?

The right test is **paired**: score each document under A and under B, then look at the distribution of the 200 per-document differences. As an illustration only, not a computed result: if per-document differences had a standard deviation of about 15 points, the standard error of the mean difference would be about 15/√200 ≈ 1.1 points. A 95% interval would be roughly 2 ± 2.1, which **includes zero**. We don't know the real spread, so we can't currently tell.

Two things make this worse:

- **Fields within a document are correlated.** A bad OCR pass sinks all five fields. So the effective sample size is closer to 200 documents than 1,000 fields. Don't run a test as if the 1,000 field slots were independent.
- **LLM extraction is stochastic**, even at temperature 0 with a seed, because provider-side nondeterminism is real. Run-to-run variation is a separate quantity from document-to-document variation. We need repeated runs to measure it, and they **don't** add to the sample size of 200.

---

## 2. Freeze the contract first

Agree on this before rerunning anything, so the decision can't be fitted to the results.

### 2.1 Task population and outcome

- **Population:** the invoice mix we actually receive in production, by source channel (PDF-native, scanned, phone photo, email body), language, currency, vendor tier, page count and document type (invoice, credit note, receipt, pro-forma).
- **Field-level correctness:** a normalized match per field (rules in 2.3).
- **Document-level success (primary metric):** all five fields correct, or correctly abstained where the field is genuinely absent or illegible.
- **Abstention:** a `null` or "low-confidence" flag on a genuinely missing or illegible field is **correct**. A fabricated value is a **critical error**. A `null` when the value is clearly present is a **miss**, which is less severe than a fabrication.

### 2.2 Severity by field

Weight errors by downstream cost, not equally:

| Field | Error severity | Rationale |
|---|---|---|
| total | Critical | Wrong payment amount |
| currency | Critical | Silently multiplies the total error (for example, JPY read as USD) |
| tax | High | Tax reporting and reclaim errors, compliance exposure |
| vendor | High | Wrong payee or vendor match. Can route payment to the wrong party |
| date | Medium | Affects period, due date and duplicate detection |

Any **fabricated** total, tax or currency (a value that appears nowhere in the document and isn't a valid derivation) is a critical error, whatever the aggregate score.

### 2.3 Executable scoring rules, not judgment

Each field should get a deterministic assertion:

- **total / tax:** parse to a decimal in the document currency. Exact match after normalization, with a tolerance of 0.00 or at most one minor unit, agreed in advance. Handle locale formats (`1.234,50`).
- **currency:** ISO 4217 code. Symbol ambiguity (`$`) is resolved by gold labelling, not by fuzzy matching.
- **date:** ISO 8601 after parsing. Pin a policy for ambiguous `03/04` (vendor locale) and record which date field counts as "the date" (issue date, not due date).
- **vendor:** match against a canonical vendor ID or alias table where one exists. Otherwise use normalized string match plus a small human-adjudicated alias list. Use a model grader only for leftover cases deterministic rules can't express. If we do use one, blind it to variant identity, calibrate it against human labels and report its agreement rate separately.
- **Schema validity:** a failed parse or a missing key scores as a failure on every affected field, not as an excluded document.
- **Consistency checks** (assertions, not scoring): `0 ≤ tax ≤ total`, currency is a valid code, date falls within a plausible window. Violations are recorded by type.

### 2.4 Acceptance thresholds (set now, before results)

Proposed gates. Adjust the numbers with finance and ops, then freeze them:

1. **Zero observed fabricated values** in total, tax or currency on the holdout. (Zero observed is a test result, not a guarantee.)
2. **Document-level success:** B ≥ A, with the paired 95% interval for B − A excluding any loss larger than an agreed tolerance (for example, −1 pt). To claim B is *better*, the interval must sit above 0.
3. **Per-field floors:** no statistically meaningful regression on **total** or **currency**, even if other fields improve.
4. **Slice gates:** no regression beyond tolerance on any critical slice (2.5), even if the aggregate improves.
5. **Known-incident cases:** every past production failure in the regression set still passes.
6. **Stability:** run-to-run disagreement rate per field (the same doc yielding different values across runs) no higher than A's.
7. **Operational:** schema-failure rate, p95 latency and cost per *successfully extracted* document (including retries) within the agreed budget.

A gain in the average that breaches gate 1, 3, 4 or 5 is **rejected**.

### 2.5 Slices that define "robust"

Robustness is a claim about the hard cases, so report each of these separately:

- Scanned or photographed documents vs native PDFs
- Multi-page invoices, with the total on the last page
- Non-USD and multi-currency documents, especially symbol-ambiguous ones (`$` for CAD/AUD/USD, `kr`)
- Locale number and date formats (EU decimal comma, DD/MM)
- Invoices with no tax line, tax-exempt or reverse-charge documents
- Credit notes and negative totals
- Documents showing several totals (subtotal, total due, balance after deposit)
- Unseen vendors vs vendors that also appear in the tuning data
- Adversarial or odd inputs: rotated pages, handwritten amendments, text in the document that tells the model to report a different total

---

## 3. Data split and leakage

The 200 documents are the **dev** set. We should assume they were looked at while building B, through prompt edits, few-shot examples or error-driven fixes. A release decision needs a **frozen holdout**:

- **Size:** aim for several hundred documents, enough for slice-level counts to mean something. Plan the slices first, then size the set.
- **Split by vendor and by time,** not by random document. Templates from the same vendor are near-duplicates. If vendor X is in dev, its other invoices shouldn't decide the holdout. Include a later time window to catch template drift.
- **Weighting:** weight cases by production traffic share *and* consequence. High-value invoices count for more than their frequency alone suggests.
- **Gold labels:** double-annotate a sample, measure annotator agreement and adjudicate disagreements. Record provenance (source, annotator, date) per case.

### Runtime-input exposure manifest

For each case:

| Agent-visible | Grader-only |
|---|---|
| Document file / OCR text, page images | Gold field values |
| Vendor master data, if production has it | Slice labels, severity weights |
| Prompt, schema, few-shot examples from the **training** pool only | Annotator notes, adjudication records |

**Leakage assertion (executable):** before each eval run, check the assembled prompt, the few-shot pool, any retrieval or vendor-lookup store and any agent memory against the holdout case IDs and gold-label files. Fail the run if any grader-only artifact can be reached. Don't detect leakage by searching for the answer *values*, because the invoice itself legitimately contains the total. Check by **artifact identity**: gold files, label stores and holdout few-shot entries.

If we can't verify this boundary for B (for example, if its few-shot examples came from the dev pool, which overlaps the vendors in the proposed holdout), report it as an **open gap**, not a pass.

---

## 4. Reproducibility manifest

Pin and record these for both variants:

- Model identifier and version, sampling settings (temperature, top_p, max tokens, seed if used)
- Prompt version, output schema version, few-shot set version
- OCR or PDF-parsing engine and version (often the real source of differences)
- Pre- and post-processing code version (normalizers, retry logic, validators)
- Dataset version and holdout hash
- Number of repeated runs per document (suggest 3–5), plus run date and time

**Ablate one change at a time.** Do the A → B differences include a prompt change, a model change, an OCR change *and* a post-processor? Then measure each separately. If B's gain comes entirely from a deterministic normalizer (for example, date formatting), we can ship that normalizer behind A at lower risk. Don't credit the gain to the variant as a whole.

---

## 5. Failure analysis

Classify each miss by its **earliest decisive cause**. If OCR dropped the last page, the total, tax and currency errors that follow count as one failure, not three.

| Class | Examples in extraction |
|---|---|
| Input / OCR | Unreadable scan, page dropped, rotation |
| Task misunderstanding | Picked subtotal or balance due instead of total. Picked due date instead of issue date |
| Grounding / fabrication | Value not present in document. Tax invented for a tax-exempt invoice |
| Normalization / schema | Correct value, wrong format. Malformed JSON. Wrong currency code mapping |
| Abstention error | `null` for a clearly present value, or a value where the field is genuinely absent |
| Stability | Different values for the same doc across runs |
| Injection / adversarial | Followed text inside the document that altered the output |

Present it as a **paired confusion table** per field:

|  | B correct | B wrong |
|---|---|---|
| **A correct** | both | **B regressions**: inspect every one |
| **A wrong** | **B fixes** | both fail |

A +2-point net gain might be, say, 60 fixes and 40 regressions. If those 40 regressions sit in totals on scanned invoices, B fails the release gate even though its average went up. Review every regression in total, currency and tax by hand.

---

## 6. Report template for the rerun

| Metric | A | B | Paired B − A (95% CI) | Gate | Pass? |
|---|---|---|---|---|---|
| Document-level success (holdout, n=…) | | | | ≥ A − tol | |
| Field match: total / currency / tax / vendor / date | | | | no critical regression | |
| Fabricated critical values (count / n) | | | | 0 | |
| Correct abstention / wrong abstention | | | | report | |
| Schema failure rate | | | | ≤ budget | |
| Run-to-run disagreement rate | | | | ≤ A | |
| Worst slice delta (name the slice) | | | | ≥ −tol | |
| Known-incident cases passing | | | | all | |
| p95 latency | | | | ≤ budget | |
| Cost per successful document (incl. retries) | | | | ≤ budget | |

Keep the field-average metric as a secondary diagnostic. Keep its definition and denominator exactly as before, so the 89/91 history stays comparable.

### One rerunnable command

Every comparison should come from a single command that resets fixtures, pins versions, runs both variants N times on the frozen holdout, runs the leakage assertion and writes the table above, for example `eval run --suite invoice-holdout-v1 --variants A,B --repeats 5`. The loop is: run → inspect regressions → change one variable → rerun → compare. Log each experiment with its hypothesis, the changed variable, versions, metrics and a KEEP / REVISE / REJECT verdict. Keep formal eval results separate from production telemetry and ad-hoc spot checks.

---

## 7. Release decision

**Current status: REVISE (hold B).** The evidence doesn't meet any gate. It doesn't count against B either.

**Path to a ship decision:**

1. Freeze the acceptance contract in section 2.4 with finance and ops. Do this now, before new results.
2. Build a vendor- and time-split holdout with slice labels and adjudicated gold. Run the leakage assertion.
3. Run A and B on the holdout with 3–5 repeats each and pinned versions. Produce the paired table and confusion breakdown.
4. Review every B regression on total, currency and tax by hand.
5. Ablate B's component changes to find where the gain actually comes from.

**Then:**

- **SHIP B** if every gate passes. Preferably start in shadow mode (B runs alongside A and disagreements are logged), then canary with human review of disagreements on high-value invoices.
- **SHIP the component** if the gain comes from one isolated, low-risk change such as a normalizer.
- **REJECT B** if it fabricates critical values, regresses totals or currency, or fails a critical slice, whatever its average.

To the teammate: B could well be the better variant. "More robust" is a testable claim, and this plan tests it on the cases where robustness matters, under rules we fix before seeing the answer.
