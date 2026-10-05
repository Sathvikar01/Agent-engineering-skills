---
name: agent-development-workflow
description: >-
  Coordinate the complete engineering lifecycle for substantial AI-agent or model-assisted workflow builds. Use when building, productionizing or substantially redesigning an agent, adding major tools/state/RAG/orchestration, or evaluating and hardening a whole agent system. Do not use for one bug, tiny prompt/schema/API changes, ordinary app work, simple deterministic utilities, conceptual agent explanations, or a narrow task owned by one specialist.
metadata:
  author: Sathvik
  collection: "Sathvik — Agent Engineering"
  version: "2.1.0"
---

# Agent Development Workflow

Models handle uncertainty; trusted code handles specifiable correctness and authority; evidence decides what survives. Coordinate specialists at relevant boundaries without copying their procedures or loading the whole collection.

## Understand and establish the contract

1. Before coding, identify goal, required behavior, inputs/outputs, system boundary, environment, constraints, safety requirements and success criteria. Inspect an existing implementation/evidence before proposing a rewrite.
2. Map important components: deterministic? model needed? why? failure consequence? validation? Avoid needless autonomy and brittle heuristics for semantic ambiguity. Use agent-architecture to choose the simplest architecture that correctly handles uncertainty; model-assisted pipeline, single tool/RAG agent and hybrid are hypotheses, not ranked defaults.
3. Use agent-evals before large implementation: baseline, representative/hard/adversarial cases, failure taxonomy, task/safety/tool/provenance/latency/cost metrics, slice thresholds and invariants. Provide one obvious project-appropriate rerun command. Average gains cannot cancel critical regressions.
4. Freeze externally visible interfaces early: run command and arguments, input/output/state/tool/model schemas and exact output fields, error semantics, stop conditions, budgets and permissions. Define behavior for missing, corrupt and contradictory inputs before implementation (agent-failure-recovery, evidence-provenance). Use structured-output-design and tool-design at those interfaces; agent-state-and-memory for persistence. Version actual contracts/assumptions rather than speculative infrastructure.

## Draw boundaries and prove a vertical slice

5. Classify decisions as deterministic, model-assisted, proposal-plus-validation or human-gated. Use deterministic-authority for permissions/calculations/state transitions and human-in-the-loop for warranted review. Model output is fallible; define what happens when it is wrong.
6. Use evidence-provenance for source → retrieval → normalization → ledger → decision → claim → reconciliation. Retrieved evidence differs from used support. Validate shape, semantics, fact/explanation consistency and cited IDs before promoting output/state.
7. Design necessary tools/retrieval/state with tool-design, rag-engineering and agent-state-and-memory. Use agent-orchestration to decide whether a model controls next steps; bound actions, calls, retries, time, cost and termination. Multiple roles/models/workers or a framework require measured benefit.
8. Build one complete safe path: input → evidence → model/logic → proposed tool action → validation → authority → effect/receipt → output → trace. Walk one real request through it and show how each exact final output field was produced from which input/evidence. Security, recovery and observability start here before real effects. Use agent-security, agent-guardrails, agent-failure-recovery and agent-observability at actual risk boundaries.

## Execute the inner loop for each material change

9. PLAN: change, reason, expected behavior, invariant and success check. IMPLEMENT: smallest coherent diff. RUN: execute relevant unit/integration/eval/CLI/browser/runtime checks. DEBUG: OBSERVATION → HYPOTHESIS → TRACE → FIX. Reproduce the mismatch and capture the actual failing command, error, assertion or trace excerpt; state a root-cause hypothesis before investigating or delegating to an AI tool, and paste that evidence into the request rather than asking it to "investigate"; then trace to confirm or reject the hypothesis; use installed systematic-debugging. CORRECT: fix the cause. REVIEW: inspect diff, results, regressions, complexity and unintended behavior; choose KEEP, REVISE or ROLLBACK. Repeat as needed; generation or one successful example is insufficient.
10. Construct → verify → admit when safe valid candidates may exist. Bound repair/alternative search under unchanged facts, policy and approval; fail closed when none can be established. Do not fabricate evidence or quietly change the requested operation.
11. Use agent-testing for deterministic semantic/authority/provenance checks, contracts, trajectories, failure injection and restart tests. Simulate malformed/empty/refused/timed-out/contradictory outputs, invented IDs, repeated answers and unsupported tools. Verify predictable degradation and no forbidden effects.
12. Run matched baseline/variant evals and inspect critical metrics; ablate uncertain extra verification, models, routing or retrieval. Record versions/configuration, quality/safety/latency/cost and failure classes. Use agent-cost-and-latency for cost per verified success and completion latency. Keep, revise or roll back from evidence; unexecuted checks remain unverified.

## Review, defend and complete

13. For material decisions record DECISION, HYPOTHESIS, ALTERNATIVES, WHY CHOSEN, EVIDENCE, LIMITATION, FALLBACK and PROPOSED/VALIDATED/REJECTED/SUPERSEDED status. Preserve important AI proposals and engineer selections/modifications/test outcomes, without labeling every line; state plainly what the engineer chose, tested, changed, rejected or fixed versus what was delegated to AI. Keep the development record as raw artifacts—actual prompts, tool responses, diffs, failing assertions and trace excerpts, with secrets redacted—not narrated summaries. Human engineers retain responsibility. Read [decision and defence templates](references/decision-and-defence.md) for substantial systems.
14. Answer technical questions directly: answer → implementation location/detail → reason/trade-off → evidence → limitation/fallback. Anchor each architectural claim to a concrete file/function or artifact. Replace qualities such as "robust", "reliable" or "trustworthy" with the named run, test, failure or log that shows them; otherwise state the claim as unverified. State limitations as GAP → CURRENT FALLBACK → NEXT STEP. At completion explain boundaries, rejected alternatives, quantified tests/evals where available, failure paths, unresolved risks and next step. Do not invent measurements or conflate telemetry with controlled evals.
15. Use installed verification-before-completion for the final evidence check. Ship through the authorized release path after required gates; record unavailable checks and gaps. A generated first implementation is a candidate, not completion.

Expected artifacts: uncertainty/ownership map, architecture decision, eval baseline/rerun command, contracts/invariants, executed vertical slice, evidence/trace, tested failure policy, comparison/ablation decision and concise defence. Scale to consequence. Existing brainstorming/planning/TDD/debugging retain mechanics; this skill owns lifecycle coordination.
