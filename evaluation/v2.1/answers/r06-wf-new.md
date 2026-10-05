# Receipt-to-reimbursement agent: debugging the currency failure

## TL;DR

- **Short answer for the reviewer:** we can't call it robust yet. 18/20 tells us how it did on 20 examples. It doesn't tell us how it handles currency. We have one currency case that fails, and I don't know how many of the 20 examples test currency at all. Until a currency test set passes, robustness is **unverified**.
- **Next step:** reproduce the one failing example, capture what the agent actually produced next to what we expected, write down a guess at the cause *before* changing anything, then trace where the `currency` value came from. Only then hand the AI coding assistant a specific request with that evidence pasted in.
- **Where the fix should probably go:** the model should *propose* the currency and quote the receipt text it saw. Trusted code should then *check* that proposal (valid ISO 4217 code, ambiguous symbols, a second clue such as merchant country). If the check can't settle it, the receipt goes to human review instead of getting a guessed currency.

I haven't seen your code, traces or eval files. Anything in `<angle brackets>` below is a placeholder for a real artifact you need to fill in. I haven't invented any results.

---

## 1. The next debugging step

### Step 0: Stop treating 18/20 as one number

Before touching the currency bug, sort **both** failures into types. "Wrong currency" is one. The second failure is unknown so far. If both turn out to have the same cause (for example, the model fills in a default when it isn't sure), that changes the fix.

| Example | Field(s) wrong | Failure type | Severity |
|---|---|---|---|
| `<id_A>` | `currency` | wrong value, no warning raised | **Critical**: a wrong amount gets paid |
| `<id_B>` | `<to classify>` | `<to classify>` | `<to classify>` |

Note on severity: a silently wrong currency in a payment flow is a critical regression. A higher average score can't make up for it.

### Step 1: OBSERVATION (reproduce and capture raw evidence)

Re-run just the failing example, using the same model version, prompt version and settings as the eval run. Save the raw items themselves, not a description of them:

1. The exact command you ran and what it printed. Example only, adjust to your project: `<eval-runner> --case <id_A> --trace`
2. The receipt input: image, OCR text, or both. Note especially the exact characters near the total (`$`, `€`, `kr`, `R$`, `¥`, `CAD`, a currency code on its own, or nothing).
3. The raw model output **before** any post-processing.
4. The final output record.
5. The expected record from the gold set.
6. A field-by-field diff, for example:
   ```
   field      expected   actual
   currency   CAD        USD
   amount     42.50      42.50
   ```
7. Run it about 5 times. Does it fail every time or only sometimes? That tells you whether to look at prompts and code (fails every time) or at how certain the model is (fails sometimes).

### Step 2: HYPOTHESIS (written down before investigating or delegating)

These are the likely causes, ranked by how often they show up in receipt pipelines. Pick the one your evidence points to and write it down before you trace:

| # | Hypothesis | Evidence that would confirm it |
|---|---|---|
| H1 | **Ambiguous symbol defaulted.** The receipt shows `$`, and the model or the normalizer turns `$` into `USD`. | OCR text shows `$` and no currency code. The raw model output already says `USD`, or a `symbol → code` map does. |
| H2 | **Code fills in a default when currency is missing.** The model returned null or nothing, and code filled in the employee's home or company currency. | Raw model output has no currency. The final record has it anyway. A `default`/`fallback` sits in the normalizer or schema. |
| H3 | **Original currency mixed up with reimbursement currency.** The receipt is in a foreign currency (or shows both, like a card slip), and the agent wrote the *payout* currency into the *receipt* field, or the other way round. | The receipt shows two currencies. The schema has one ambiguous `currency` field, or two fields with similar names. |
| H4 | **Schema or prompt doesn't constrain the value.** Free text such as `"US Dollars"` or `"€"` gets coerced the wrong way. | The raw output isn't an ISO code. The coercion step maps it wrongly. |
| H5 | **The gold label is wrong.** | A person rereads the receipt and agrees with the agent. |

**My leading guess, until evidence says otherwise: H1 or H2.** Both are silent defaults, and they're the most common way this field breaks. H5 is cheap to rule out, so check it first.

### Step 3: TRACE (confirm or reject)

Follow the `currency` value through each stage and record its value at every one:

```
receipt text/image → OCR → model raw output → schema parse → normalizer/defaults → (FX conversion) → final record
```

You've found the cause at the first stage where the value goes wrong. If the raw model output is already wrong, the problem is in the prompt, schema or model (H1/H4). If the raw output is correct or null and the final record is wrong, the problem is in code (H2/H3).

### Step 4: FIX, then REVIEW

- Fix the stage the trace points to, with the smallest change that fixes the cause. Don't add a special case for this one receipt.
- Re-run **all 20** cases plus the new currency test set (section 3). Check that nothing that passed before now fails.
- Read the diff, then decide whether to **KEEP / REVISE / ROLLBACK**. One passing example doesn't count as a fix.

---

## 2. What I'd paste to the AI coding assistant

I'd paste the evidence and my guess at the cause, not "investigate the currency bug". I'd fill in the template only **after** Steps 1 to 3:

````text
Context: receipt-to-reimbursement agent. Eval: 18/20 pass. Case <id_A> fails on the
`currency` field only. Every other field matches.

Reproduction (deterministic: <k>/5 runs fail):
  $ <exact command>
  <pasted output / failing assertion, secrets redacted>

Receipt text near total (from OCR):
  "<exact OCR excerpt, e.g. 'TOTAL $42.50  GST 2.02'>"

Value of `currency` at each stage:
  model raw output:   <value>
  after schema parse: <value>
  after normalizer:   <value>   <- first wrong value appears here
  final record:       <value>
  expected (gold):    <value>

Hypothesis: <e.g. H2: normalize_receipt() fills a missing currency with
employee.home_currency instead of returning "unknown">.
Supporting evidence: <file:function:line or trace excerpt>.

Request:
1. Confirm or refute the hypothesis by pointing to the exact code path. Do not
   change code yet if it's refuted. Tell me what the evidence shows instead.
2. If confirmed, propose the smallest diff that:
   - stops silently defaulting/guessing currency,
   - returns a typed `needs_review` status with reason `currency_ambiguous`
     when the receipt doesn't settle the currency,
   - keeps the output schema's field names unchanged (<list exact fields>).
3. Add unit tests for: ambiguous "$", missing symbol, two-currency receipt,
   non-ISO model output ("US Dollars"), and this case <id_A>.
4. Don't change the gold labels, the prompt for other fields, or FX conversion
   logic unless the trace shows they're involved.

Constraints: model output is untrusted. Currency must be a valid ISO 4217 code or
an explicit unknown. Never infer it from the employee's profile.
````

Why it's written this way: it hands over real evidence and a guess that can be proven wrong. It caps how much the assistant can change. It forbids "fixes" that would mask the problem, like editing gold labels or quietly adding a default. I'd keep the prompt, the reply and the diff as raw records in the debugging log.

---

## 3. The reviewer's question: "Is the currency handling robust?"

Answered the way I'd answer in a technical interview: **answer → where it lives → reasoning and trade-off → evidence → limitation and fallback.**

**Answer.**
Not shown yet, so I won't claim it. The evidence we have is 18/20 overall, with one confirmed currency failure. I don't know how many of the 20 cases actually test currency, so the pass rate tells us almost nothing about currency specifically. I'd say "unverified, and we have one counterexample", not "robust".

**Where it lives (current state, to fill in from code).**
The currency value currently comes from `<model extraction step / prompt file>` and passes through `<normalizer function>` on the way to the `currency` field in `<output schema>`. The trace in section 1 shows which of these produced the wrong value: `<stage>`.

**Reasoning and trade-off (target design).**
Recognizing a currency on a receipt is genuinely ambiguous. `$` is used for at least USD, CAD, AUD, SGD, MXN and others. `¥` can mean JPY or CNY, and `kr` can mean SEK, NOK, DKK or ISK. That's why the model should read the receipt. But whether a value is *allowed* and *acceptable* is something code can decide exactly, so the model shouldn't decide it. Split the work:

- **The model proposes** `currency_code`, plus `currency_evidence` (the exact text it saw on the receipt) and `currency_basis` (`explicit_code`, `unambiguous_symbol`, `ambiguous_symbol_plus_context`, or `not_found`).
- **Code checks the proposal:**
  - It must be a valid ISO 4217 code.
  - The quoted evidence must actually appear in the OCR text.
  - If the evidence is an ambiguous symbol, the code is accepted only when an independent clue agrees: merchant country or address, a tax label (GST/HST/VAT), a phone prefix, or the card statement.
  - Otherwise the result is `needs_review: currency_ambiguous`.
- **FX conversion stays fully in code.** It uses a named rate source and the transaction date. The model never does the arithmetic.
- **No silent defaults.** The employee's home currency is never used to fill in the receipt's currency.

The trade-off: more receipts go to human review, and in exchange none get paid in the wrong currency without anyone noticing. For reimbursements that's the right trade, because a wrong currency means a wrong payment.

Alternatives I rejected:
- Regex or symbol lookup only: can't resolve `$` or `kr`.
- Always trusting the model: that's the failure we have now.
- Always defaulting to home currency: wrong for exactly the travel receipts where currency matters most.

**Evidence (what would make "robust" a claim we can back up).**
Replace the word with named checks. None of these have been run yet, so all of them are **unverified**:

| Check | Pass condition |
|---|---|
| Currency test set: explicit ISO code; unambiguous symbol (€, £); ambiguous `$` with country clue; ambiguous `$` with no clue; `¥` JPY vs CNY; `kr` variants; no symbol at all; two currencies on one receipt (foreign total plus card-slip home amount); decimal-comma formats (`1.234,50`); OCR noise near the symbol | **0 silently wrong currencies.** Ambiguous cases end up as `needs_review`. Unambiguous cases are correct. |
| Unit tests on the checking code (bad ISO code, quoted evidence not in OCR text, ambiguous symbol without a second clue) | Deterministic pass |
| Injected faults: model returns null, `"US Dollars"`, an invented code (`"USX"`), or contradicts the receipt | Typed rejection or review, never payment |
| Matched re-run of the original 20 cases | No previously passing case regresses |

Rerun command (suggested, adapt to the project): `<eval-runner> --suite receipts --slice currency`, with the original 20 cases always run alongside it.

The bar is that **the count of silently wrong currencies is zero.** That's an invariant that must always hold, not a percentage target.

**Limitation and fallback.**

| GAP | CURRENT FALLBACK | NEXT STEP |
|---|---|---|
| The root cause of `<id_A>` isn't confirmed yet | Treat the currency field as untrusted. Flag foreign or ambiguous receipts for manual check | Run Steps 1 to 3 |
| No currency test set exists, so robustness can't be measured | None. The claim stays unverified | Build the test set above (aim for roughly 30–50 cases, including the hard ones) |
| Ambiguous `$` with no clue on the receipt can't be resolved | Proposed: `needs_review: currency_ambiguous` | Measure how often this happens. If review volume gets too high, ask the employee to confirm the currency at submission |
| Unclear how the model behaves on layouts it hasn't seen | Checking code plus human review | Watch how often production receipts go to `needs_review`. Treat that as telemetry, not as a controlled eval |

---

## 4. Decision record

| Decision | Hypothesis | Alternatives | Why chosen | Evidence | Limitation | Fallback | Status |
|---|---|---|---|---|---|---|---|
| Model proposes currency with quoted evidence; code checks it; ambiguous cases go to human review | Symbols on receipts are ambiguous, and whether a value is allowed can be checked exactly | Symbol lookup only; trust the model; default to home currency | Lets the model handle the ambiguity without ever paying a wrong amount silently | Not yet: needs the currency test set plus a re-run of the 20 cases | More receipts to review; unseen layouts | `needs_review: currency_ambiguous` | **PROPOSED** |
| Root cause of `<id_A>` | H1/H2 (silent default) | H3, H4, H5 | Most common way this field breaks | Not yet: needs the trace | — | — | **PROPOSED** |

**Done means:** the trace confirms the cause, the fix diff has been reviewed, the currency test set shows zero silent wrong currencies, none of the original 20 regress, and the second failure (`<id_B>`) has been classified. Until then, the honest status is "candidate fix, not verified".
