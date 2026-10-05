---
name: agent-evals
description: >-
  Define evaluation-first quality gates for an AI agent or model-powered workflow. Use when specifying agent success before implementation, building gold task sets, comparing agent variants, or diagnosing outcome and trajectory regressions. Do not use for ordinary unit-test writing or tool-interface usability alone without an agent quality measurement question.
metadata:
  collection: "Agent Engineering"
  version: "2.1.0"
---

# Agent Evals

Before large implementation work, write a small executable or reviewable eval specification. If infrastructure is absent, a fixture table plus scoring rules is sufficient to establish the contract; label unexecuted checks honestly.

## Freeze the contract before optimizing

1. Define the task population, successful outcome, severity of mistakes, prohibited actions, latency/spend budgets and abstention behavior. Record a baseline: deterministic workflow where feasible, then the current agent. Do not compare a new agent to an invented weak baseline.
2. Build versioned gold cases from representative tasks, boundary cases, adversarial inputs and known incidents. Each case has source/provenance, expected facts or acceptable outcomes, permitted actions, initial state and reset procedure. Include success, safe refusal and partial-result cases. Assign IDs and weights by expected traffic and consequence, not convenience.
3. Split by underlying task/source/time or customer; group near duplicates. Create a runtime-input exposure manifest: task/initial state and authorized source evidence are allowed; answer keys, grader labels and scoring annotations are grader-only. Exclude grader-only material from model prompts, retrieval/tool-visible stores, memory and tuning examples during BOTH development and evaluation. Inspect the assembled model input and reachable sources; a sealed split alone does not establish this boundary. Legitimate evidence may contain the answer. Freeze the holdout before optimizing.

## Score outcomes and trajectories separately

4. Prefer executable assertions for calculations, schemas, final state, authorization, tool arguments, citation existence and budgets. A syntactically valid response is not necessarily correct; passing contract/schema checks is scaffolding, not task correctness. When the output is a record or set of fields, score each required field against gold separately (declared exact or normalized match) and report per-field accuracy alongside whole-record exact match; an aggregate score can hide one systematically wrong field. Do not require identical intermediate reasoning when several safe trajectories are acceptable.
5. Evaluate final answer correctness, completeness, groundedness and calibrated abstention. Evaluate trajectory permissions, tool selection/arguments, evidence support, redundant steps, retry behavior and termination. A good final answer cannot cancel an unauthorized action.
6. Use a model grader only for judgments that deterministic checks cannot express economically. Give it a rubric, source evidence and examples; conceal variant identity, delimit untrusted content, compare against human labels, and record disagreements. A grader's approval never grants execution authority. Do not request private chain-of-thought; evaluate observable calls, decisions and evidence.
7. Assign a failure taxonomy: task misunderstanding, context/retrieval, proposal/schema, authority, tool selection/arguments, execution/recovery, grounding, state, termination. Attribute the earliest decisive failure rather than counting downstream symptoms as independent failures.

## Compare and release

8. Pin fixtures, tool behavior, model identifier, sampling settings, prompt/tool/schema versions, environment and relevant time. Repeat stochastic tasks; report sample size, distribution and uncertainty. A seed does not guarantee provider determinism. Measure per-task paired differences; distinguish across-task variation from repeated-run variation.
9. Run ablations one change at a time: tools, context, routing, retrieval stages or workers. Report quality, safety violations, abstentions, p95 latency and cost per successful task, including failures/retries. Preserve metric definitions, units and denominators: an unspecified quality percentage need not mean binary task success and cannot establish a raw success count. Judge gains against noise and complexity.
10. Set acceptance thresholds before reviewing results. Require zero observed critical authority violations, scenario coverage for critical boundaries, agreed task-quality floor and bounded operational metrics. Zero observed violations is a test result, not proof of universal safety. Gate release on regression slices as well as the aggregate. A quality gain that breaches a critical safety, provenance or operational threshold is rejected even if the average improves.

Deliver case fixtures, scoring/rubric, split policy, runtime-input exposure manifest and leakage assertion, reproducibility manifest, failure analysis and release decision with evidence. Read [scoring guide](references/scoring.md) when constructing metrics or grader calibration.

Existing TDD and verification skills own normal code correctness and completion evidence. Agent-testing owns the runtime test pyramid; tool-evals isolates usability of the tool surface. Do not rebuild either here.

## Make comparisons rerunnable

Provide one project-appropriate command that resets fixtures, runs the selected suite and emits results: run → inspect → change → rerun → compare. Record hypothesis, changed variable, dataset/prompt/model versions, architecture, retrieval and verification settings, task/safety/tool/provenance metrics, latency, cost, failure classes and KEEP/REVISE/REJECT conclusion. Record each rejected alternative as TRIED → RESULT → REJECTED because <metric> moved from X to Y on <dataset/version>. Quality claims such as "more robust" or "more reliable" must name the run, metric and dataset that support them, otherwise report them as unmeasured. Separate formal eval results from production telemetry and exploratory diagnostics. Ablate optional verification, an extra model or routing before attributing reliability to it; unavailable measurements remain unavailable.
