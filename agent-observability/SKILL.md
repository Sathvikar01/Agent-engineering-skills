---
name: agent-observability
description: >-
  Instrument AI-agent trajectories so actions, evidence, state and quality can be reconstructed. Use when designing or reviewing traces/metrics for agent model calls, tools, approvals, retries, state, evals, cost or latency, or debugging an opaque agent run. Do not use for general service logging without an agent trajectory, full private reasoning collection, or quality scoring rules alone.
metadata:
  author: Sathvik
  collection: "Sathvik — Agent Engineering"
  version: "2.0.0"
---

# Agent Observability

Design telemetry around questions an operator must answer: what the run tried, what was authorized, what happened, what evidence supports the result, and why it stopped. Existing observability skills own logging/tracing infrastructure and alert plumbing.

## Specify the event contract

1. Choose request/run IDs and parent span/worker/task IDs that survive retries and resume. Distinguish logical operation ID from attempt ID; join distributed records with correlation IDs and state versions. Include event time and ordering/sequence where needed; clock timestamps alone do not establish causal order.
2. Emit structured events for request acceptance, model call, proposal/validation, policy decision, approval request/decision, tool attempt/result, retrieval/context assembly, checkpoint, state transition, retry/failure, evaluator outcome and terminal status. Capture inputs/outputs by safe reference or redacted bounded fields rather than indiscriminate payload logging.
3. Record actual model/prompt/schema/tool/policy/retrieval versions, authorized principal scope, token usage when available, tool/result classification, timing, normalized action digest, state versions and evidence/receipt IDs. Capture refusal, malformed output, truncated response and unknown effects distinctly.
4. Log observable decisions and short explanations when useful; do not require or store private chain-of-thought. Tool arguments, policy reasons, citations and committed state are stronger debugging evidence than a narrative of the model's thoughts.

## Connect operation to outcome

5. Measure task success/safe abstention, policy violations, unknown effects, retry exhaustion, no-progress termination, human review rate, evaluator disagreement and retrieval failures alongside p50/p95 latency and spend. Break down by release/version and meaningful task slices; avoid user/run IDs as metric labels with unbounded cardinality.
6. Attribute cost to the complete logical task including failed attempts, retries, cache charges and workers. Treat unavailable token/cost data as unavailable, not zero. Do not infer spend from output characters without labeling an estimate.
7. Link final outcome and evaluator decision to evidence, tool receipts and deterministic state versions. Preserve failed/denied attempts even if later steps succeed. Sampling ordinary debug spans can be acceptable; retain policy/approval/side-effect audit evidence at the rate needed for accountability.

## Protect and prove usefulness

8. Apply redaction before persistence, bounded payloads, tenant access, retention/deletion and secret scanning. Restricted evidence pointers are not public debug links. Trace export cannot become an exfiltration path. Separate operational telemetry from consented evaluation datasets.
9. Reconstruct a failed run from events alone: triggering request, proposal, admission, attempt, ambiguous result, retry, approval and terminal state. Verify joins and missing-event handling; inject orphan parent spans, cyclic links and missing required events, and require an incomplete/inconsistent result rather than claiming full reconstruction. Declare external trace boundaries explicitly. A replay for analysis defaults to fakes/read-only evidence and does not re-execute live effects.

Deliver an event schema/example timeline, instrumentation points, outcome/operational metrics and operator query/runbook. Verify nested workers, restart, denied action, lost response, redacted secret and evaluator disagreement. Alerts should lead to a diagnosable action, not fire on every model call.

agent-evals owns quality definitions; this skill records their results. agent-failure-recovery owns retry policy; this skill makes its decisions visible.

## Make signals actionable

Join retrieved, model-visible and used evidence IDs to decision/claim IDs and reconciled outputs; logging candidates does not prove support. Distinguish formal eval metrics (controlled fixtures), production telemetry (real traffic) and ad-hoc diagnostics (exploration).

For material signals specify baseline, threshold, observation window, denominator/minimum sample, severity, owner and response: unsupported evidence, tool failure, user overrides, safety violations, retry exhaustion, retrieval misses, eval regression and cost/latency drift. A safety breach may halt mutation capability; drift may trigger investigation/rollback to a verified version. Measure baselines or label provisional thresholds rather than inventing production numbers.
