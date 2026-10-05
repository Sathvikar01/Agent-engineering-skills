# Ledger and reconciliation example

Application-created records can be small typed rows:

```
E1: source=manual, span=12:18, version=4, digest=..., tenant=T1,
    observed_by=tool-call-7, run=R1, retrieved=true, visible=true
E2: source=appendix, span=1:3, version=4, tenant=T1,
    observed_by=tool-call-7, run=R1, retrieved=true, visible=false (budget)
C1: computation=approved-total, inputs=[E1], rule=totals-v2, value=100
D1: decision=WAIT, facts=[C1], used_support=[E1], missing=[approval]
claim-1: text="Approval is still required", decision=D1, support=[E1]
```

Check ID, access/freshness, visibility and lineage first; actual support next. E2 exists but cannot support this claim merely because retrieved. Unknown E9 is rejected. “Approved now” contradicts D1=WAIT even with valid E1. Source text claiming E9 cannot issue a record. Visible means supplied to this model call, not dropped during assembly.

Compare deterministic typed facts with authorized observations. For natural-language inference provide source span and calibrated support assessment; string equality is not a general entailment engine. Keep supported/unsupported/contradicted/unresolved distinct. Model-proposed support must be checked.

Retain restricted source pointers/transform mappings. Revoked or expired evidence requires rebuilding support or unsupported status. Receipts prove observed effects under adapter semantics, not universal system correctness.
