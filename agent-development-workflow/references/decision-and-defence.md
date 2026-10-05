# Material decisions and technical defence

Use for architecture, trust, quality or operational choices, not tiny edits.

| Decision | Hypothesis | Alternatives | Why chosen | Evidence | Limitation | Fallback | Status |
|---|---|---|---|---|---|---|---|
| Bounded model extraction, deterministic payment arithmetic | Document variants need interpretation | Regex-only; autonomous finance agent | Interpretation uncertain; arithmetic specified | Actual fixture/eval result or proposed experiment | Unseen layouts | Typed review-needed result | PROPOSED/VALIDATED/REJECTED/SUPERSEDED |

Do not mark proposed experiments VALIDATED. Track important AI proposals and engineer choices/tests without per-line attribution.

For “Why this architecture?”, lead with choice/boundary, then implementation, alternatives/trade-offs, observed comparisons, limits/fallback. A substantial completion defence covers what was built, boundaries, key code locations, why choices survived, test/eval versions/counts, failure modes, fallback, risks and next improvement.

Inner-loop record: planned invariant/check → diff → actual command/output → reproduced failure/root cause when present → correction → rerun/regression result → retain/revert decision. Do not manufacture a failure to fill DEBUG; if no mismatch occurred, report checks and that observation.
