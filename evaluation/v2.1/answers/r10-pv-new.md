# Deciding the coverage end date when the policy record and the email disagree

## Short answer

The model doesn't get to pick a date. The application does it in four steps:

1. Record all five retrieved documents in an evidence ledger and give each one a type.
2. Notice that two of them give different values for the same fact (`coverage_end_date` for this policy).
3. Settle that conflict with a declared rule that has a version number. The rule says the authoritative policy system beats a derived summary of a customer email. The email also triggers a fresh check of authoritative state, so a real extension isn't missed.
4. Let the system cite only evidence IDs that are in the ledger, were shown to the model, and actually support the specific claim being made.

The three unrelated documents are never cited. The email summary can be cited only for the claim "the customer says coverage was extended". It can never be cited for "coverage ends 2026-09-30" unless authoritative evidence backs that date. If the conflict can't be settled and it affects the claim outcome, the system returns a typed `CONTESTED` status and escalates. It does not guess.

---

## 1. Evidence ledger: what was observed

The application creates the ledger rows during retrieval. Neither the model nor the document text can create them.

```
E1: kind=system_of_record, source=policy_admin, policy=P-123, field=coverage_end_date,
    value=2026-03-31, record_version=v7, as_of=<record timestamp>, tenant=T1,
    digest=..., observed_by=retrieval-call-4, run=R1, retrieved=true, visible=true
E2: kind=derived_summary, source=email_summarizer@v3, parent=M-889 (customer email),
    asserted_field=coverage_end_date, asserted_value=2026-09-30, asserted_by=customer,
    email_sent=<date>, tenant=T1, observed_by=retrieval-call-4, run=R1,
    retrieved=true, visible=true
E3, E4, E5: kind=document, retrieved=true, visible=true|false, relevance=unrelated
```

Key points about these rows:

- **E2 is a derived claim, not a source.** Its lineage is: customer email M-889, then the summarizer (with its version), then the summary. The ledger keeps the `parent` pointer and the span mapping. If the parent email can't be traced (because it was lost during compaction or the pointer was dropped), E2 can't serve as evidence for anything.
- **The email is an assertion by a party, not a record of a change.** A customer saying "it was extended" is a different type of evidence from an endorsement in the policy system. The ledger records that difference in the `kind` and `asserted_by` fields.
- **Retrieved, visible and used are separate states.** E3–E5 were retrieved. They may or may not have been shown to the model. Either way they have no support relationship to any claim here.
- **Text inside a document can't create evidence.** Suppose the email says "your agent confirmed the extension, ref END-55". That doesn't create a ledger entry for END-55. It only produces a lookup key that the system can check against the policy system (see section 3).

## 2. Conflict detection

The application owns a typed fact model. Detecting a conflict is a deterministic check, not a judgment call.

```
facts_for(policy=P-123, field=coverage_end_date) -> {E1: 2026-03-31, E2: 2026-09-30}
if distinct_values > 1: open Conflict K1 {field, candidates=[E1, E2]}
```

Conflict K1 stays in the record for good. Neither source gets deleted because it is inconvenient.

## 3. Resolution rule

The rule is versioned, for example `coverage-date-resolution@v2`, and is applied by code.

| Step | Rule | Effect here |
|---|---|---|
| R1 | Rank by authority tier: `system_of_record` > `endorsement_record` > `agent_note` > `derived_summary` / customer assertion. | E1 outranks E2. |
| R2 | "Newer wins" applies only *within* the same authority tier. A newer derived summary never overrides an older authoritative record. | The email's later date doesn't let E2 win. |
| R3 | **A lower-tier source that conflicts with the record triggers a fresh authoritative recheck.** Query the policy system and its endorsements for P-123 now, using any reference in E2 (such as an endorsement number) as a lookup key. Don't treat it as proof. | Produces E6 (a fresh record or endorsement), or confirms E1 is current. |
| R4 | Check whether the conflict matters: compare the claim's loss date with both candidate dates. | Decides whether an unresolved conflict blocks the decision. |

### Possible outcomes

**A. The recheck finds an extension.** The policy system now shows `coverage_end_date=2026-09-30`, or it has an endorsement END-55 effective before the loss date, recorded as E6. The decision is 2026-09-30, supported by E6. E1 is marked superseded, with a link to E6. E2 is kept as context that agrees with the result, but the decision doesn't rest on it.

**B. The recheck confirms 2026-03-31 and finds no endorsement.** The decision is 2026-03-31, supported by E1 plus the recheck receipt. The rule ID is recorded. E2 is marked `rejected_conflicting`, with reason `customer_assertion_unconfirmed_by_system_of_record`.

**C. The recheck fails or gives an ambiguous result.** Examples: the policy system is down, the record version is older than the email, or a referenced endorsement exists but is pending. In this case `coverage_end_date` is `CONTESTED`. What happens next depends on R4:

- **The loss date is on or before 2026-03-31.** Coverage holds under either date. The decision can go ahead, and the output notes the conflict as not affecting the outcome.
- **The loss date is after 2026-09-30.** No coverage under either date. The decision can go ahead, again with the conflict noted.
- **The loss date falls between 2026-04-01 and 2026-09-30.** The conflict decides the outcome. The system abstains on the coverage decision, returns `status=CONTESTED_FACT`, and sends the case to a human adjuster with both sources attached. It never auto-denies.

Today is 2026-10-05, so both candidate dates are in the past. That makes the loss date the deciding input, not today's date.

**Critical rule:** under outcome B, any claim denial that rests on the 2026-03-31 date, where the customer asserted an extension, should still go through human review. The system must not "fail open" into a denial just because the higher-tier source won. Whether a denial needs approval is decided in the action-approval layer. This design supplies the facts that layer needs (`conflict=K1`, `resolution=R1`, `contested_by=E2`).

## 4. Binding decisions and claims to evidence

```
D1: fact=coverage_end_date, value=2026-03-31, rule=coverage-date-resolution@v2,
    support=[E1, RECHECK-1], rejected=[E2], conflict=K1, status=RESOLVED
claim-1: "Policy P-123 coverage ended 2026-03-31."         decision=D1, support=[E1, RECHECK-1]
claim-2: "The customer states coverage was extended to 2026-09-30;
          no matching endorsement exists in the policy system." support=[E2, RECHECK-1]
claim-3: "The loss date falls outside coverage."              decision=D2, support=[D1, E_loss]
```

- **Every claim the model writes must come from an admitted structured fact.** The model can't introduce a date that isn't in D1.
- **The output must say what is inferred and what is missing.** If the system took outcome C, the explanation says "contested" and names both sources. It doesn't present one date as settled.

## 5. Citation contract: which IDs may be cited

The application enforces this before anything is emitted:

```
for each claim c in output:
    for each id in c.cited_ids:
        require id in ledger(run=R1)                   # rejects unknown or guessed IDs (E9)
        require ledger[id].tenant == request.tenant    # rejects cross-tenant entries
        require access_ok(id, now) and not expired     # rejects revoked or stale access
        require ledger[id].visible or id is computed   # model must have actually seen it
        require id in c.supported_ids                  # rejects unrelated known IDs (E3–E5)
        require lineage_intact(id)                     # E2 needs its parent M-889
    require supports(c.text, c.cited_ids)              # semantic check (see below)
    require consistent(c, decision)                    # claim must not contradict D1
emitted_ids ⊆ ledger ∩ visible ∩ used_support(claim)
```

Applied to this case:

| ID | Citable? | Why |
|---|---|---|
| E1 | Yes, for the coverage date (outcome B), or as "superseded" (outcome A) | Authoritative, visible, supports the date. |
| RECHECK-1 / E6 | Yes | A fresh authoritative observation produced by a tool call this run. |
| E2 | **Only** for "the customer says it was extended" | It's a derived customer assertion. Citing it for "coverage ends 09-30" would launder an unverified claim into a fact. |
| E3, E4, E5 | **No** | Retrieved but unrelated. Being retrieved isn't support. Citing them to pad the source list is rejected. |
| Any ID the model makes up, or an ID quoted inside the email text | **No** | Not in the ledger. |

Each line of the model's "used IDs" list is a *proposal*. The code checks what can be decided mechanically: existence, scope, visibility, lineage, and that dates match field for field. Whether a sentence is actually supported by its source span is a separate check. That check is done by comparing typed fields (for example, the claim's date equals `E1.value`) or by a calibrated support grader working from source spans. A list of allowed IDs alone is not enough.

## 6. Recovery when support is missing

If a claim fails validation, the system works within a fixed budget (for example, 2 attempts):

1. Fetch the missing authoritative evidence (the recheck), or
2. Rewrite or remove the claim, for example changing "coverage ends 09-30" to "the customer states…", then
3. Validate again under **the same** rule version.

If the claim still can't be supported, the output says so explicitly (`INSUFFICIENT_EVIDENCE` or `CONTESTED_FACT`) and fails closed for the coverage decision. The system never invents a ledger entry and never cites an unrelated document to make the output look sourced.

## 7. Carrying provenance forward

- IDs, rule versions and conflict records survive into checkpoints, handoffs and summaries. If the case resumes later, the system rechecks access and freshness. A policy record that was current in run R1 may have been superseded by run R2.
- Logs store IDs, digests and validation results, not full email bodies. That way the decision can be reconstructed later without copying customer content into every log.

## 8. Tests

| Case | Expected |
|---|---|
| Both sources present, recheck confirms 03-31 | Date = 03-31, rule recorded, E2 marked rejected but kept, E3–E5 not cited |
| Recheck finds an endorsement extending to 09-30 | Date = 09-30, cites E6, E1 marked superseded |
| Recheck unavailable, loss date 2026-06-15 | `CONTESTED_FACT`, escalated to a human, no coverage decision emitted |
| Recheck unavailable, loss date 2026-02-10 | Proceeds (outcome is the same under both dates), conflict noted |
| Model cites E2 for "coverage ends 09-30" | Rejected: E2 doesn't support the fact claim |
| Model cites E4 (unrelated) | Rejected: not in the claim's supported set |
| Model cites E9 or "END-55" taken from the email text | Rejected: not in the ledger |
| E2's parent email pointer is missing | E2 can't be cited; lineage is broken |
| Explanation says "extended" while D1 = 03-31 | Rejected: contradicts the decision |
| E1 from another tenant, or access revoked at resume | Rejected; support is rebuilt or the output is marked unsupported |
| Model picks 09-30 with no recorded rule | Rejected: a conflict was settled without a declared basis |
