# Revision 2.1.0 paired smoke evaluation

This folder holds the paired run of the seven behavioral cases added in 2.1.0, each answered once with the 2.1.0 skill and once with its 2.0.0 predecessor.

## Method

- **Executors:** one fresh agent per run. Each saw only its copy of `SKILL.md` and `references/`, never `evals/`, the expectations or other runs, and was told not to use installed skills.
- **Blinding:** runs were saved under random IDs (`r01`–`r14`). One grader scored all 14 against `cases.json` without knowing which version produced which answer. `id-map.json` was removed from the run folder until grading finished.
- **Grading:** strict. An expectation passes only when it is met explicitly, and every part of a multi-part expectation must be present. Each verdict cites a quote from the answer (`grades.json`).

## Results

| Case | Skill | 2.1.0 | 2.0.0 |
|---|---|---:|---:|
| wf | agent-development-workflow | 3/4 → **4/4** after fix | 3/4 |
| ev | agent-evals | 3/4 | 3/4 |
| pv | evidence-provenance | 3/3 | 3/3 |
| fr | agent-failure-recovery | **4/4** | 3/4 |
| ob | agent-observability | 3/3 | 3/3 |
| td | tool-design | **3/3** | 2/3 |
| ar | agent-architecture | 3/3 | 3/3 |
| **Total** | | **22/24 → 23/24** | **20/24** |

- **Improved:** `agent-failure-recovery` (the new input-degradation section produced fixtures asserting no refund effect) and `tool-design` (the example call now sits inside the model-facing description).
- **Fixed after the run:** the first 2.1.0 workflow answer used GAP → CURRENT FALLBACK → NEXT STEP but did not separate engineer and AI contributions. That rule lived only in step 13 (decision records). It was added to step 14's answer format, and a fresh re-run (`r15-wf-fix`, graded separately with the same rubric) passed 4/4.
- **Ambiguous case:** `ev` expectation 2 asks for a TRIED → RESULT → REJECTED record for "any rejected variant". Both versions correctly chose HOLD and rejected nothing, so both failed it. The failure is kept as graded rather than relabeled. The case should be revised so the expectation can apply.
- **Ties:** five cases tied. Several new rules (contradiction reconciliation, raw trace artifacts, module separation) were already met by the 2.0.0 skills on these prompts, so a tie does not show added benefit.

## Limits

One sample per case and configuration. This is smoke evidence, not a measure of reliability. The executors and the grader were the same model family. The `r15` re-run was graded on its own, not blind against a paired answer.
