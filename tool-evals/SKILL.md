---
name: tool-evals
description: >-
  Measure whether an LLM agent can discover, select, compose and recover with a tool surface. Use when testing model-facing tool usability, argument accuracy, response interpretation, multi-step tool chains, unnecessary calls or tool failure handling. Do not use for backend API contract tests alone, MCP server scaffolding, or whole-agent answer-quality benchmarking without a tool-use question.
metadata:
  collection: "Agent Engineering"
  version: "1.0.0"
---

# Tool Evals

Evaluate the model/tool interaction, not merely whether the endpoint returns 200. Keep server contract tests deterministic and separate; use agent-evals for end-to-end outcome scoring.

## Build realistic cases

1. Freeze the tool catalogue, descriptions, schemas, model/prompt version, permissions, fixtures and initial state. Include similar tool names and plausible distractors. Compare the current surface with a baseline under the same task distribution.
2. Write cases covering discovery, choosing the correct capability, filling types/units/IDs, interpreting empty/partial results, chaining dependent calls, and deciding that no tool is needed. Include ambiguous user intents and insufficient evidence; correct abstention can be success.
3. Include a realistic multi-step case: search → select a supported identifier → read current version → propose a permitted change → satisfy authority/approval → commit → verify observed state. Assert data dependency and forbidden effects rather than one exact safe call sequence.
4. Add pagination, stale version, authorization denial, malformed result, rate-limit, unknown side-effect outcome, cancellation and budget exhaustion. Keep side-effect tests in resettable sandboxes or fakes; an eval is not authorization to touch live accounts.

## Capture and score observable behavior

5. Record visible tool catalogue/discovery evidence, calls with normalized arguments, principal, response classification, timestamps, policy decisions, and final state. Preserve rejected calls in the trajectory. Do not score a correct final sentence as successful mutation unless committed evidence agrees.
6. Score each dimension independently: discovery recall; selection correctness; argument correctness; response interpretation; chain dependencies; unnecessary calls; failure recovery; termination; final state and forbidden effects. Define denominators and severity. Safe redundant calls cost efficiency; unauthorized writes fail the safety gate regardless of other scores.
7. Use deterministic assertions for schema validation, identifier provenance, call dependencies, permissions, retry ceilings, duplicate effects and state. Grade genuinely ambiguous semantic choices against a rubric and source evidence. A trace mentioning a tool name is not evidence that it selected it correctly.
8. Repeat stochastic cases, report per-slice variation and false selections, and inspect earliest failures. Separate model misuse from server bugs and catalogue/discovery omission. Do not punish valid alternative tool sequences simply because they differ from a sample transcript.

## Refine one cause at a time

9. Change one description, schema, result shape or granularity choice; rerun matched cases and held-out tasks. Retain changes only when benefit outweighs added complexity and latency. Test removal of distractor tools before adding routing machinery.

Deliver task fixtures, allowable/forbidden effects, dependency assertions, traces, dimension scores and a contract improvement justified by failures. Existing MCP XML QA evals are useful for read-only answers; add safety, ambiguity and recovery cases without replacing that tooling.
