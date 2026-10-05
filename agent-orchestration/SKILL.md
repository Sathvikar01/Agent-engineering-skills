---
name: agent-orchestration
description: >-
  Design bounded next-step control for an AI runtime, from fixed routing to adaptive tool/retrieval choice and justified workers. Use when choosing who controls the next step, implementing agent routing, handoffs, fan-out/fan-in, shared state, cancellation or aggregate budgets. Do not use for coding-subagent dispatch, ordinary parallel utilities, whole-system lifecycle planning alone, or tool contracts without a runtime control-flow question.
metadata:
  author: Sathvik
  collection: "Sathvik — Agent Engineering"
  version: "2.0.0"
---

# Agent Orchestration

First ask: “Does a model actually need control over the next step?” Second: “Could deterministic routing perform this more reliably?” Use fixed control for known conditions, bounded model choice for ambiguous/contextual observations. Then ask whether multiple agents add measured value.

## Route a single agent before adding workers

Define typed controller state, admissible next actions and deterministic transition guards. Known status/error/permission rules route in code. Ambiguous evidence gaps may justify proposals to select tools, retrieve more evidence, check contradictions, request independent verification or escalate. Validate selections against capabilities, prerequisites and remaining budgets.

Enforce max steps/model calls/tool calls/retries/time/spend, no-progress and terminal conditions across fallback/resume; repeated suggestions cannot reset the run. Prefer functions, explicit state machines or jobs; choose framework primitives only for demonstrated reliability/maintainability needs. Evaluate routing and optional workers against task-fit baselines; free-form negotiation is not a required control plane.

## Add workers only when justified

Apply the worker sections below only if the simpler controller is insufficient; one agent does not need worker handoffs or fan-in.

1. Compare deterministic workflow, one model-powered step and single-agent/tool designs using representative evals. Reject multiple agents for known rules, small shared-context tasks or role labels without measurable benefit. Parallel deterministic functions do not need agent personas.
2. Identify genuinely separable work, specialized context or independent verification. Record dependency edges, shared resources, merge semantics and expected gain. If all workers need the same full context and continually negotiate, decomposition may be wrong.
3. Choose the smallest pattern: independent fan-out/fan-in, planner with bounded workers, or a separate reviewer with a defined rubric. A reviewer can detect errors but cannot grant authority. Use deterministic scheduling for known dependencies and avoid free-form agent-to-agent chat as the control plane.

## Specify handoffs and ownership

4. Give each task a typed contract: task/run/parent IDs, objective, input evidence and scope, output schema, allowed tools, completion criteria, deadline, budgets and cancellation. Mark external content as untrusted; handoff summaries do not gain authority by being written by another agent.
5. Assign one authoritative owner per mutable resource or use explicit transactional/versioned coordination. Workers return proposals/evidence; the orchestrator validates results and deterministic policy authorizes effects. Scope each worker's identity/capabilities; do not inherit broad coordinator privileges by default.
6. Define fan-in rules for missing, failed, conflicting or duplicate results. Validate schema/provenance, choose deterministic merge rules where possible, and escalate substantive conflicts with evidence. Majority vote or reviewer agreement is not proof of truth or permission.
7. Preserve idempotency across duplicate dispatch and retries. Define checkpoint/resume and late-result behavior; a cancelled or expired task must not commit a delayed proposal. Reconcile unknown worker effects before rescheduling.

## Bound coordination and prove benefit

8. Set total and per-worker ceilings for steps, model calls, tools, spend, time, fan-out and concurrency. Reserve budgets centrally/atomically so workers cannot independently exceed the aggregate. Stop on objective completion, dependency failure, deadline, cancellation, policy denial or no progress.
9. Limit planner/reviewer rounds and specify the condition for another round. Do not allow recursive delegation or conversation loops without explicit bounded benefit. Capture parent/child traces, worker versions, handoff evidence, conflicts and final evaluator outcome.
10. Run ablations against the simpler baseline, including coordination/merge costs and failure modes. Ship multiple agents only if the measured benefit survives realistic skew, missing workers, duplicate work and contradictory outputs. Preserve a single-agent fallback only when it meets the same safety policy.

Deliver control ownership, typed controller states/guards, allowed next actions, budgets, termination/failure policy and comparison evidence. For justified workers add task graph, handoff/merge and resource authority contracts. Existing subagent/dispatching skills own agents collaborating on coding tasks; this skill designs the deployed orchestration system.

