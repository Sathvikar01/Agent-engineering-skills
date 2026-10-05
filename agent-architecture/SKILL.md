---
name: agent-architecture
description: >-
  Choose the simplest AI-system architecture that correctly handles the task’s uncertainty. Use when designing or reviewing runtime autonomy, deciding whether a product needs an agent, or placing reasoning, tools, state and authority boundaries. Do not use for ordinary application architecture or executing a coding plan without an AI runtime design decision.
metadata:
  collection: "Agent Engineering"
  version: "2.1.1"
---

# Agent Architecture

Start with the user outcome, not an agent framework. Produce a decision record before a large implementation; adapt its detail to the system's risk.

## Select the architecture

1. Express success as observable outcomes, disallowed actions, and representative acceptance cases. Establish an existing-system or deterministic baseline before choosing autonomy.
2. Map important components: deterministic? model needed? why? failure consequence? validation? Put models where interpretation is genuinely uncertain and code where correctness can be specified. Choose among these hypotheses by task fit; they are not a universal ranking:

| Class | Choose when | Validation/comparison check |
|---|---|---|
| Deterministic software | Rules, inputs and transitions are known | Assert known rules and edge cases; confirm no material semantic interpretation is being guessed |
| Deterministic workflow / model-assisted pipeline | Step order is known; bounded interpretation may use a model | Verify extracted meaning and downstream rules on ambiguous cases |
| Single agent | Next steps depend on observations; no external capability is needed | Verify adaptive choices and termination against a fixed-control baseline |
| Agent with tools | Adaptive reasoning must use bounded external capabilities | Verify contextual tool choices, contracts and admission against fixed routing |
| Multi-agent system | Independent work, specialization, isolation or review creates measured benefit | Net gain exceeds coordination/merge cost; multiple responsibilities alone are insufficient |
| Hybrid design | Components need different control modes, such as a fixed extraction path and bounded adaptive retrieval | Validate each boundary and compare the composition; hybrid does not imply multiple agents |

3. Justify autonomy with evidence that next-step choice depends on ambiguous observations; compare simpler plausible alternatives in evals. Do not require brittle regex to fail before using a model for semantic interpretation. A marketing label, unknown future requirements, or a framework's availability is insufficient. Unknown requirements call for a bounded experiment, not a speculative swarm.

## Specify the boundaries

4. Map one representative run: intent → success/evals → context/state → model proposal → deterministic validation → policy authorization → approval if required → tool execution → evidence → evaluation → deterministic state update.
5. Assign owners for reasoning (interpretation/planning), execution (side effects), trust (untrusted inputs), and authority (permissions/business rules). The model may propose actions but cannot promote its prose into trusted state. Show where each input becomes validated data. Keep routing/control, safety/validation/authority and I/O adapters in separate modules with narrow interfaces so each boundary can be tested and audited; a single monolithic agent module hides them.
6. Define context sources and budgets; persisted state, memory and source of truth; coherent tool contracts; least-privilege identities; approval gates; and evidence provenance. Use application-owned state for money, permissions and workflow status.
7. Define terminal statuses and hard ceilings for time, steps, model/tool calls and spend. Include cancellation, no-progress detection, policy denial, unavailable evidence and partial completion. Completion requires outcome verification, not the agent's declaration.
8. Design checkpoints at durable boundaries, ambiguous-side-effect reconciliation, and resume authorization. Capture run IDs, versions, transitions, costs and evaluator outcomes so a failed trajectory is reconstructable.

## Deliver and verify

Deliver the classification and rationale, boundary/ownership table, one happy and one denied/failed trajectory, budgets and termination rules, recovery path, and eval release gate. Name unresolved assumptions and the experiment that resolves each.

Verify with a task requiring no model, a fuzzy but fixed workflow, an adaptive tool task, and an authority violation. Do not add a loop to a fixed pipeline. Do not add workers to a single context merely to label them specialist agents.

Requirements and implementation planning may use any available brainstorming, spec or planning skill. This skill owns the deployed system's autonomy decision. Use agent-evals for scoring, deterministic-authority for admission logic, and agent-orchestration for next-step control and justified workers; none is a mandatory dependency.

## Reject misleading architecture evidence

Check agentification (fixed rules given adaptive loops), deterministic overcorrection (semantic ambiguity forced into fragile rules), framework cargo culting (no needed framework capability) and multi-agent theater (roles without measurable benefit). Ordinary functions, state machines and queues are valid orchestration implementations. Adopt a framework only for demonstrated resumability, tracing, concurrency or maintainability needs.

Reject validation theater (shape without meaning), evaluation theater (tests unable to reject a bad variant), fallback theater (unreliable output relabeled success) and evidence theater (citations unrelated to the decision). Define the counterexample and acceptance check that rejects each applicable failure. Identify model roles—interpretation, extraction, classification, routing, reasoning, verification or explanation—and evaluate choices per role; one model may fill several roles.
