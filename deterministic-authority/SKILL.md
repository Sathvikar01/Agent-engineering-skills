---
name: deterministic-authority
description: >-
  Build deterministic admission and authorization between model proposals and side effects. Use when an LLM can propose state changes, money movements, permission decisions or actions subject to executable constraints, or reviewing whether a model can override policy. Do not use for purely advisory text generation or ordinary business logic with no model-to-action trust boundary.
metadata:
  collection: "Agent Engineering"
  version: "2.0.0"
---

# Deterministic Authority

MODEL = advisory/proposal layer. DETERMINISTIC CODE = validation and authority layer. A model may suggest an exception; only the trusted policy path can define and authorize one.

## Establish an admission contract

1. Enumerate each action, authenticated principal, resources, authoritative facts, invariants, permissions, impact and policy owner. Derive identity and permissions from trusted execution context. Model-supplied role, confidence, approved=true and natural-language memory have no authority.
2. Express business rules and calculations in deterministic code using typed inputs and explicit units. Validate cross-resource and tenant constraints, freshness, current state version and available budget. Return structured allow, deny or needs_approval with reason codes and policy version. Missing facts, policy errors and unknown action types fail closed for execution.
3. Keep stages explicit: bounded parsing/schema → semantic validation → policy/permissions/invariants → required approval → admission immediately before execution → tool execution → receipt/evidence → evaluator → deterministic state transition. Validators do not issue permissions, and evaluators do not retroactively authorize an action.

## Prevent bypass and race conditions

4. Enforce admission at every side-effect entry point, including retries, resumed runs, workers and alternate tools. A system prompt is not a policy engine. Avoid a generic execute capability that bypasses the constrained executor.
5. Bind any authorization/approval grant to principal, action, resource, canonical arguments, state/policy version, expiry and use count. The application issues the grant; the model cannot mint one. Recheck policy if facts change. Use a transaction or compare-and-set to prevent state changes between admission and commit; handle conflict by a fresh decision rather than trusting an earlier allow.
6. Define idempotency and concurrent budget reservation in the trusted executor. Two individually allowed actions can violate a cumulative limit; check/reserve the aggregate atomically. Preserve deny decisions in the run evidence without exposing secrets.
7. Keep explicit policy exceptions auditable and narrowly scoped. Human approval may satisfy a required discretionary gate but cannot silently waive a hard invariant or exceed the approver's authority. Change the policy through its authorized process if an exception is truly intended.

## Verify adversarial proposals

Deliver the action/policy table, typed admission function or pseudocode, denial examples, authorized execution path and tests. Exercise forged approval, stale state, absent facts, policy outage, alternate path, concurrent overdraw and retry/resume. Prove denial leaves state unchanged and allow commits once with a valid receipt.

Example: balance=100 units, reserve floor=20, proposal transfer=90. Trusted code rejects because 100−90 is below 20 even if the model cites an urgent request and approval. A later valid transfer still needs principal permissions and a fresh atomic balance check.

Use human-in-the-loop to design review experience and agent-guardrails to assemble defense layers. This skill owns enforceable admission, not the user interface or every surrounding safety mechanism.

## Construct before terminal failure

An invalid proposal is denied, but need not end the task. If authorized facts permit a valid solution, construct a fresh candidate (or deterministic solution), verify against the same invariants, then seek admission. Bound alternatives, model calls and deadline. Do not silently change the requested amount or commit an alternative the user did not authorize; prepare a preview where approval is needed. Distinguish missing permission, irreconcilable constraints and unavailable required facts from repairable candidate errors. Every rejected candidate stays effect-free; only a freshly validated and authorized candidate executes. Fail closed when no admissible candidate can be established.
