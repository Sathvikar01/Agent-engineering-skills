---
name: agent-cost-and-latency
description: >-
  Optimize AI-system cost and latency per verified successful outcome using measured budgets. Use when profiling model/tool/retrieval spend or delays, setting agent run ceilings, choosing model routing/escalation, caching, batching or parallelism under quality constraints. Do not use for general application performance without model/agent costs, speculative model recommendations, or reducing tokens without outcome measurements.
metadata:
  collection: "Agent Engineering"
  version: "2.0.1"
---

# Agent Cost and Latency

Measure the full logical task before optimizing it. Token savings are not a win if errors, retries or incomplete results make successful outcomes more expensive.

## Establish the baseline and ceilings

1. Define verified success, safe abstention, quality/safety floors and user-facing latency target. Measure representative task slices, p50/p95 wall time, token categories, tool/retrieval time, number of steps/calls, cache behavior and all failed/retried work. Pin model/prompt/tool versions and pricing timestamp; use measured billing when available and label estimates.
2. Compute cost per successful task = total attributable spend across all attempts / verified successes. Report success rate and abstention mix alongside it; if successes=0 the metric is undefined, not zero. Include queueing, human wait time where relevant and coordination costs. Separate interactive response latency from completion latency.
3. Enforce maximum steps, model calls, tool calls, retrieved candidates/context, fan-out, deadline and spend in software. Reserve aggregate worker budgets and preserve them across resume. Stop or return a supported partial/abstained result when limits are exhausted; do not silently drop validation to hit a budget.

## Optimize the measured bottleneck

4. Route to the smallest model/workflow that satisfies the eval gate; escalate on calibrated hard-case/validation signals within explicit call/spend limits. A cheap failed call followed by a large model can cost more than direct routing. Compare routing end to end, including fallbacks.
5. Reduce context by removing irrelevant/redundant evidence and verbose tool outputs while preserving needed provenance and constraints. Improve retrieval/assembly before raising context limits. Measure recall and groundedness after reduction.
6. Cache only stable reusable work with keys covering principal/tenant, permissions, input, model/prompt/schema/tool/index versions and freshness requirements. Never reuse approvals, authoritative changing state or cross-tenant output as if current. Define expiry/invalidation and charge cache creation/read costs correctly.
7. Parallelize independent reads/model tasks only when it reduces critical-path latency within rate/concurrency/spend limits. Keep dependent actions ordered. Batch offline independent work when supported and latency tolerance permits; bound queue time and retry blast radius. Use deterministic orchestration where sufficient.
8. Reduce loops and needless calls before adding clever routing. Coalesce coherent tool operations where semantics/authority remain clear. Do not hide side effects inside a read tool to save a round trip.

## Compare and verify

9. Change one variable, run matched eval tasks under comparable load/cache conditions, repeat noisy measurements and examine tail behavior. Keep gains only if success, safety, groundedness and latency floors hold. Report cost per success, failures and p95, not only average tokens. Read [cost comparison](references/cost-comparison.md) for a worked denominator trap.

Deliver a baseline ledger, bottleneck evidence, enforced ceilings, one optimization experiment and a quality-gated retain/revert decision. Generic profiling belongs to ordinary performance work (or a performance-optimization skill, if available); this skill owns model/retrieval/trajectory economics. Do not recommend a provider/model by reputation without current measured evidence.

Evaluate model choices per role (extraction, reasoning, routing, verification, grounded generation, multimodal interpretation, embedding/reranking), then measure the assembled system. One model may satisfy several roles; an extra verifier/model needs an on/off or matched-routing ablation on the same gold set. Record role errors and whole-task quality, cost per success and latency to verified completion. Participation statistics and provider reputation do not prescribe models. agent-evals owns rigor; agent-orchestration owns route transitions.
