---
name: agent-guardrails
description: >-
  Assemble and verify layered runtime guardrails for an AI system without confusing guidance with enforcement. Use when designing agent safety/quality containment, abstention gates, policy enforcement, permissions, runtime limits or approval layers, or reviewing a prompt-only guardrail claim. Do not use for security threat modeling alone, writing admission code alone, generic input validation, or making a system prompt sound safer.
metadata:
  collection: "Agent Engineering"
  version: "2.0.0"
---

# Agent Guardrails

Assign each control a concrete boundary, owner and failure mode. A system prompt alone is never a security boundary; probabilistic advice can improve behavior but cannot authorize execution.

## Build a control matrix

| Layer | Role | Failure handling |
|---|---|---|
| Probabilistic guidance/classifier | Steer or detect ambiguous content | Measure false negatives/positives; never sole protection for critical effects |
| Deterministic validation | Enforce shape, meaning and invariants | Reject current candidate; bound safe reconstruction under unchanged constraints |
| Policy enforcement | Decide allowed, denied or approval-required actions | Trusted rules; missing/error states fail closed for effects |
| Permissions | Limit caller/resource/capability scope | Least privilege; recheck at executor |
| Runtime limits | Bound time, calls, spend, concurrency and output | Stop/cancel with honest partial/failed status |
| Human approval | Supply authorized judgment for consequential choices | Exact bounded grant; silence/expiry does not approve |

1. Start with the action/outcome inventory and failure taxonomy. Select controls proportionate to impact and uncertainty; harmless read-only answers do not require every layer. Specify disallowed effects and acceptable abstention/partial behavior before adding detectors.
2. Map each risk to an enforceable layer and test. Distinguish input-content checks, model proposal validation, pre-execution admission, output grounding/privacy checks and post-execution evidence evaluation. Post-hoc blocking cannot undo an already sent email.
3. Place critical deterministic controls at every execution entry point, including retries, workers and resume. Separate model outputs from trusted state. A classifier score or second model's agreement cannot bypass permissions or hard business constraints.
4. Define fail-closed behavior for malformed proposals, missing policy, unavailable required checker, expired approval or unsupported action. Safe read-only degradation or a typed abstention can continue if policy permits; do not silently disable a required boundary during an outage.
5. Bound repair/escalation loops. State when to retry eligible failures, construct/repair supported candidates, retrieve missing evidence, use validated fallback, seek human review, deny permanently or terminate. Prefer construct → verify → admit when safe admissible solutions may exist; terminal fail-closed behavior is not a reason to skip bounded search. Calibrate uncertainty against data; do not treat model confidence as permission. Record control/version decisions and evidence with privacy-aware run IDs.

## Validate the composition

6. Test bypass paths, contradictory layer outputs, outage, stale grants, false blocking of legitimate tasks, poisoned inputs and cumulative budget exhaustion. Assert actual effects/state, not merely reassuring response text.
7. Measure violations, task success, safe abstention, false-positive/negative rates, review burden, added latency and cost. Set severity-aware acceptance thresholds; zero observed critical violations is necessary test evidence but not a universal guarantee.
8. Ablate optional probabilistic layers in a sandbox to measure benefit, while preserving mandatory deterministic permissions/policy. Remove redundant checks that add friction without coverage. Keep rollback/version compatibility and an operator path for investigation.

Deliver a risk-to-control matrix, enforcement locations, failure/escalation table, bypass/outage tests and measured release decision. agent-security owns attack-path analysis; deterministic-authority owns admission implementation; human-in-the-loop owns approval design. This skill owns how those controls compose and whether gaps remain.
