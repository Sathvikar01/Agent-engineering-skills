# v3 evaluation plan

Status: **planned, not run.** Current evidence (revision 2 and the 2.1 smoke runs) is single-sample, same-model-family and mostly revised-vs-previous. This plan is the experiment needed to claim that the skills materially change agent behavior.

## Questions

1. **Effect:** does each skill improve outcomes over no skill, and over its previous version?
2. **Activation:** do real harnesses load the right skill from its description, and leave it unloaded when it doesn't apply?

## Behavioral effect

- **Skills (6):** agent-development-workflow, agent-evals, deterministic-authority, evidence-provenance, structured-output-design and agent-failure-recovery. These carry the collection's core rules and the most consequential failure modes.
- **Configurations (3):** no skill, previous released version, current version.
- **Cases:** 6–8 held-out cases per skill, written fresh and not used during development, covering representative, adversarial and "skill should change nothing" inputs. Freeze them, with expectations, before any run.
- **Repetition:** 5 runs per case per configuration (about 720 runs). Pin model, sampling settings and harness version.
- **Blinding:** strip configuration identity, randomize IDs, keep the ID map away from graders until scoring is complete.
- **Graders:**
  - one model grader from a different model family than the executors;
  - one same-family grader, to measure grader bias;
  - human labels on a stratified 20% sample (at least 2 labelers), with agreement (Cohen's κ) reported and disagreements adjudicated.
  - Deterministic checks wherever an expectation is decidable.
- **Analysis:** per-skill paired differences (current − none, current − previous) with bootstrap 95% intervals across cases and runs; per-expectation pass rates; failure classes using the agent-evals taxonomy. Report ties and regressions as prominently as gains.
- **Pre-registered gates:** set before running. For example: current ≥ none on every skill with an interval excluding zero on at least four; no expectation regresses by more than one run in five against previous; zero critical-authority violations.

## Activation

- **Harnesses:** Claude Code and Codex at minimum, each in a clean profile containing only this collection plus a fixed set of adjacent third-party skills (for realistic collisions).
- **Queries:** the existing 380 trigger queries plus 60 new held-out ones, including multi-skill queries where loading several skills is correct.
- **Measurement:** whether the harness actually loads each skill, read from tool-use and transcript logs rather than from a metadata classifier. Score precision and recall per skill, and confusion between neighboring skills.
- **Known ambiguity:** the one proxy miss (central worker-budget reservation, which also belongs to agent-cost-and-latency) stays a scope question. Do not tune descriptions to fit a single query.

## Deliverables

Frozen case set and expectations, raw transcripts, grader outputs, human labels, an analysis notebook or script with a single rerun command, and a results report that keeps every caveat in `VALIDATION-REPORT.md` that still applies.
