# Revision 2.1 paired smoke evaluation

This folder holds the paired runs of the seven behavioral cases added in 2.1, each answered with the revised skill and with its 2.0.0 predecessor.

## Method

- **Executors:** one fresh agent per run. Each saw only its copy of `SKILL.md` and `references/`, never `evals/`, the expectations or other runs, and was told not to use installed skills.
- **Blinding:** runs were saved under random IDs. The grader scored them against `cases.json` without knowing which version produced which answer. The ID-to-version map (`id-map.json`) was kept out of the run folder until grading finished.
- **Grading:** strict. An expectation passes only when it is met explicitly, and every part of a multi-part expectation must be present. Each verdict cites a quote from the answer (`grades.json`).

## First run (`answers/`, `grades.json`)

All seven pairs, revised skills at 2.1.0: **22/24 vs 20/24**. Two problems surfaced:

1. **agent-development-workflow:** the engineer-vs-AI ownership rule lived only in step 13 (decision records), so the 2.1.0 answer did not apply it in a direct defence. It was added to step 14. A standalone re-run (`r15-wf-fix`) passed 4/4, but it was not a blinded pair.
2. **agent-evals:** expectation 2 required a TRIED → RESULT → REJECTED record for "any rejected variant". Both versions correctly held and rejected nothing, so both failed. The expectation was invalid for this input.

## Re-run (`rerun/`)

To close both loose ends, the expectation was corrected to: *"For every variant it rejects, records TRIED → RESULT → REJECTED …; if it rejects no variant, it states explicitly that none was rejected and why."* The two affected pairs were then re-run blind with fresh executors and a fresh grader, current skills (2.1.1) against 2.0.0:

| Case | Revised | 2.0.0 | 2.0.0 failure |
|---|---:|---:|---|
| agent-evals | **4/4** | 3/4 | no whole-record exact match |
| agent-development-workflow | **4/4** | 3/4 | no current fallback; no engineer-vs-AI split |

## Combined paired result

Using the re-run for those two pairs and the first run for the other five:

| Case | Skill | Revised | 2.0.0 |
|---|---|---:|---:|
| wf | agent-development-workflow | **4/4** | 3/4 |
| ev | agent-evals | **4/4** | 3/4 |
| fr | agent-failure-recovery | **4/4** | 3/4 |
| td | tool-design | **3/3** | 2/3 |
| pv | evidence-provenance | 3/3 | 3/3 |
| ob | agent-observability | 3/3 | 3/3 |
| ar | agent-architecture | 3/3 | 3/3 |
| **Total** | | **24/24** | **20/24** |

- **Improved:** four skills. Three ties: the 2.0.0 skills already met contradiction reconciliation, raw trace artifacts and module separation on these prompts, so a tie does not show added benefit.
- **Mixed versions:** five pairs ran the 2.1.0 text. 2.1.1 changes only optional-companion wording and the workflow step-14 rule, but those five were not re-run on 2.1.1.
- **Noise:** the 2.0.0 agent-evals answer failed a different expectation in each run (expectation 2, then expectation 0). Single samples move between runs.

## Limits

One sample per case and configuration: smoke evidence, not reliability. Executors and graders were the same model family, and no human labels were used. The comparison is revised skill vs previous skill, not skill vs no skill. See [the v3 evaluation plan](../V3-PLAN.md) for the experiment that would address these.
