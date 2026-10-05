---
name: agent-failure-recovery
description: >-
  Design bounded retries and durable recovery for AI-agent runs and side effects. Use when handling interrupted agent execution, ambiguous tool commits, partial completion, checkpoints/resume, poison tasks or retry/timeout policy. Do not use for general bug diagnosis, ordinary synchronous exception handling, or session handoff with no runtime recovery problem.
metadata:
  collection: "Agent Engineering"
  version: "2.1.1"
---

# Agent Failure Recovery

Start by classifying what is known about the effect. A lost response is not evidence that execution failed. Recovery preserves authorized progress without duplicating irreversible work.

## Classify and budget

1. Distinguish validation/policy denial (permanent until inputs/authority legitimately change), not-found, version conflict, rate limit, transient dependency failure, cancellation, and unknown side-effect outcome. Keep unknown separate from success and failure.
2. Set per-operation and per-run retry ceilings, cumulative deadline, spend and model-call limits. Preserve remaining budgets across restarts. Use exponential backoff with jitter for eligible transient failures, honor bounded retry-after, and avoid synchronized storms. Do not retry authorization/schema failures unchanged or allow infinite model repair loops.
3. Use circuit breakers for repeated dependency failures where traffic warrants them; define open/half-open conditions and controlled probes. A tiny process may need only a deadline and retry ceiling. Do not add queues/breakers merely to appear distributed.

## Make effects recoverable

4. Give each logical operation a stable idempotency key bound to principal/action/canonical arguments. Atomically claim it, retain pending/committed/unknown status and result for a stated retry horizon, and reject conflicting payload reuse. Do not mint a new key after a timeout to force progress.
5. Checkpoint durable state and receipts at operation boundaries. Include pending effects, source/state versions and remaining budget. Define crash behavior before claim, after claim, after external commit and before local receipt persistence. Reconcile against a status API or authoritative store before replaying unknown effects.
6. When the provider offers no idempotency or reliable status query, do not claim exactly-once. Choose at-most-once dispatch with unresolved/manual review, or acknowledge possible duplicates only if the task policy permits them. Indefinite uncertainty is an escalation/terminal status, not a license to retry.
7. Resume by validating checkpoint compatibility, principal/access and current policy. Reuse completed evidence; reauthorize pending actions; recompute stale proposals against fresh state. A restart does not restore expired approval or replenish exhausted budgets.

## Handle partial work

8. Report completed, pending/unknown, failed and compensated operations separately. Roll back transactional changes where supported. For external effects, define explicit authorized compensating actions; they can fail or need their own approval and are not equivalent to erasing history. Do not attempt unauthorized reversal merely because an earlier step failed.
9. Quarantine poison tasks after a bounded number of attempts. Use dead-letter handling when a durable queue already exists; include sanitized cause, provenance, safe redrive requirements and an owner. Re-drive only after a specific cause is corrected and effects reconciled.

Deliver a failure-to-action table, budgets, checkpoint/operation ledger, retry/reconciliation pseudocode, partial-result statuses and crash/restart tests. Verify one committed effect survives a lost response and retry exactly once in an idempotent fake; test permanent denial, expired grant, exhausted budget and failed compensation.

Defect diagnosis belongs to ordinary debugging (or a debugging skill, if available); this skill owns runtime recovery semantics. agent-state-and-memory owns the state representation and tool-design owns the interface contract.

## Plan model-boundary degradation

For each boundary define primary path → eligible bounded retry → repair/alternative → supported partial result, human escalation or terminal failure. Distinguish retry (same eligible request), repair (new candidate under the same facts/contract), fallback (different implementation meeting the same acceptance gate), escalation (authorized external judgment) and terminal failure. Cover empty/malformed output, semantic contradiction, invented IDs, refusal, timeout and provider failure. Deterministic fallback is useful only for behavior it reliably specifies; regex guessing is not a semantic fallback. Construct → verify → admit within remaining budgets when valid candidates may exist. Fallback success requires evidence under the original policy; never bypass validation or resend an unknown committed effect for a reassuring result.

## Plan input-evidence degradation

Before implementation, define for each required input (file, image, audio, message history, record, retrieved document) what happens when it is missing, unreadable/corrupt (truncated, wrong encoding or type, failed decode, checksum/schema mismatch), stale or contradictory. Detect corruption with deterministic checks—size, type, decode, checksum, schema—before model interpretation; a model's description of an unreadable input is not evidence of its content. Choose an explicit action per case: request or re-fetch the input, use a validated alternate source, return a typed partial result naming the gap, escalate, or fail. Do not fill missing or corrupt evidence with plausible model output. Route contradictory inputs to the declared reconciliation rule (evidence-provenance). Test each case with a fixture and assert the typed status and absence of unsupported fields or effects.
