---
name: human-in-the-loop
description: >-
  Place proportional human review and approval gates in an AI system's execution path. Use when designing approval/escalation for agent actions with financial, external, destructive or permission impact, preview-before-commit flows, or uncertainty that warrants human judgment. Do not use for requesting routine coding confirmation, imposing approval on harmless reads, or deterministic authorization logic alone.
metadata:
  collection: "Agent Engineering"
  version: "1.0.1"
---

# Human in the Loop

Use humans where a consequential decision needs their authority or judgment. Repeated approvals for harmless actions train users to click through; removing every approval also hides consequential choices.

## Decide whether to gate

1. For each action, record impact, reversibility, affected people/resources, uncertainty, existing user authorization and applicable policy. Do not ask again if a valid scoped authorization already covers the action. A preference remembered by the model is not authorization.
2. Let deterministic policy decide which actions can proceed, must be denied, or require approval. Favor automatic execution for authorized low-impact reversible work. Gate meaningful financial commitments, external communications, destructive operations and permission changes when the user/policy has not already authorized their specific scope. A sandbox draft or preview can normally be prepared first.
3. Escalate insufficient evidence, policy exceptions, novel high-impact actions or uncertainty beyond a calibrated threshold. Use objective missing evidence or measured uncertainty, not a model's unsupported confidence score. Hard invariant violations are denied; they are not solved by an approve button.

## Prepare a concrete decision

4. Complete authorized reversible preparation before asking. Present exact proposed action, targets/recipients, amount or scope, useful diff/preview, material risks, evidence and available alternatives. Keep the request understandable and proportional; do not dump a trajectory for the approver to reconstruct.
5. Identify an approver with the necessary authority. Bind approval to principal, canonical arguments/action digest, resources, relevant state/policy version, expiry and use count. Store application-issued approval and decision evidence outside model prose. Reject self-approval by the acting model.
6. Keep pending, approved, denied, expired and cancelled states explicit. A timeout or silence is not approval. While pending, continue independent authorized work without executing the gated action. Offer cancellation and safe draft retention.
7. Recheck policy and binding before commit. Changed recipients, amounts, material diff, state or expired approval require a fresh decision. Prevent time-of-check/time-of-use substitution. Apply idempotency so retries do not duplicate approved effects.

## Control friction and verify

8. Batch related decisions only when users can understand and authorize the bounded group; allow item-level rejection. Define explicit standing grants with limits/expiry if appropriate, rather than assuming previous approvals authorize future actions. Measure approval frequency, abandonment, review time, erroneous approvals and escalation outcomes.

Deliver an action-to-gate table, one exact preview, approval state/binding contract, timeout/changed-action behavior and tests. Verify denied/expired grants prevent effects, changed payload invalidates approval, and harmless authorized reads proceed without repeated prompts.

deterministic-authority owns enforcement; this skill owns when and how a human decision enters that path. Ordinary development review and confirmation are out of scope; do not add a ritual approval step to every coding task.
