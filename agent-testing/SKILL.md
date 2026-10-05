---
name: agent-testing
description: >-
  Build a risk-based test pyramid and CI verification strategy for an AI-agent runtime. Use when implementing agent tests across deterministic admission/state, schemas, tool contracts, integration, trajectories, eval suites, adversarial behavior or restart/recovery. Do not use for ordinary test-first coding without an AI runtime, writing a gold-set scoring strategy alone, or browser automation unrelated to agent behavior.
metadata:
  author: Sathvik
  collection: "Sathvik — Agent Engineering"
  version: "2.0.0"
---

# Agent Testing

Test the system that interprets and executes model proposals. Spend model calls only where model variability matters. Existing TDD skills own red-green-refactor mechanics; agent-evals owns task population, rubrics and statistical release thresholds.

## Allocate tests by ownership and risk

| Layer | Verify | Preferred execution |
|---|---|---|
| Unit | Policies, permissions, money/units, budgets, state transitions | Pure deterministic tests; boundary/property cases |
| Schema | Required/extra fields, variants, malformed/refused output, versions | Fixtures and real validators |
| Tool contract | Inputs/results/errors, pagination, timeout, idempotency | Fakes plus adapter tests against resettable sandbox |
| Integration | Admission→executor→receipt→state, trust and tenant boundaries | Scripted model/tool responses |
| Trajectory | Allowed call dependencies, no forbidden effects, termination | Recorded/scripted traces; model runs for selection behavior |
| Eval suite | Outcome quality, grounding, abstention and stochastic variation | Versioned representative/adversarial model tasks |
| Restart/recovery | Crash windows, unknown commit, resume budgets and stale approval | Fault injection with durable fake/provider sandbox |
| E2E/browser | Actual user approval/diff, cancellation and visible outcome | Browser/E2E only when that surface exists |

## Construct evidence before implementation

1. Map each high-impact invariant to an executable deterministic test. Cover both deny and allow paths and assert persisted state/no-effect outcomes; matching an error string alone is weak evidence.
2. Stub the model at integration boundaries using valid, malformed, unsupported, adversarial and refused outputs; include empty/missing fields, valid shape with invalid meaning, invented IDs, contradictory evidence, timeout, repeated/no-progress answers and unsupported tool requests. Stub tools with realistic envelopes and uncertain commit results. Verify the production validator/executor, not a test-only implementation mirroring it.
3. Test properties across generated inputs where practical: denial never mutates state; a key/payload pair commits at most one effect under supported semantics; unknown variants fail closed; tenant A cannot read/write B; budgets never increase on resume. Reenter terminal controllers and resume terminal checkpoints: they must reuse the outcome or reject, without another dispatch/effect; new work needs a distinct logical task. A fake cannot prove a provider's idempotency guarantee—test the real adapter contract too.
4. Inject crashes before/after effect commit and before receipt persistence; race concurrent approvals/state updates; expire grants and credentials; simulate rate limits, slow tools, poisoned results and evaluator disagreement. Reconcile uncertainty before replay.
5. For stochastic model behavior, use the eval specification, pinned versions, held-out fixtures, repeated runs and meaningful thresholds. Assert permitted dependencies/effects rather than an exact transcript or chain-of-thought. Do not use an LLM grader for arithmetic, schema or permission predicates.

## Gate and report

6. Put cheap deterministic tests in the fast CI path; run integration/contract checks at relevant change boundaries, and expensive eval slices on prompt/model/tool/retrieval changes. Use a larger release suite for consequential regressions. Keep critical authority checks fail closed even if a model-eval dependency is unavailable.
7. Reset sandbox fixtures, preserve failing seeds/trajectories, and distinguish a product failure from infrastructure failure or flaky stochastic scoring. Do not silently mark skipped/unavailable tests passed. Report commands, versions, counts and uncovered risks before completion.

Deliver a risk-to-test matrix, test fixtures/fakes, runnable checks at the changed layer, CI triggers and exact verification evidence. Select browser tools only for actual user flows. Do not require a sprawling test system for an advisory single call.

Add deterministic provenance/reconciliation tests: unknown IDs and retrieved-but-unused citations cannot support claims; explanation facts must match admitted structured decisions. Include a repairable candidate reaching fresh validation/admission and an unrepairable candidate causing no effect. Execute fault fixtures against the surrounding validator/controller, not merely model promises. agent-development-workflow coordinates run/debug/correct/review; installed TDD retains implementation mechanics.
