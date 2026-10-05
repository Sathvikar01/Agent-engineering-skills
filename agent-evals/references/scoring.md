# Scoring and release decisions

Use executable assertions for observable effects. For a refund task, assert actor permission, original order/tenant provenance, amount from trusted arithmetic, request-bound approval, exactly one committed fake effect under supported idempotency semantics, and a matching receipt. A fluent final answer cannot satisfy these assertions.

For final-answer semantics, use a rubric that distinguishes correct supported answer, incomplete supported answer, unsupported claim, and justified abstention. Give graders accessible source spans and expected facts; do not give variant labels or allow source text to instruct the grader. Calibrate against human-labeled examples and review disagreement. Report grader model/version and reliability separately from agent quality.

Task success = successful tasks / eligible tasks. Report safe abstention separately; exclude a task only under a predefined eligibility rule. Safety violation rate uses all applicable attempts, including failed/retried trajectories. A run with a correct answer and an unauthorized write is unsafe.

Record failure stage and severity. Use paired task results to compare variants. Repeated runs of the same task estimate stochastic variance; different tasks estimate population heterogeneity. They are not interchangeable sample sizes. Report denominators and uncertainty rather than declaring significance from a tiny mean difference.

Example release rule, to adapt before seeing scores: zero observed critical authority violations, no lost critical regression cases, task success at least the agreed baseline within the uncertainty tolerance, and p95/cost ceilings met. A 90% aggregate cannot hide an unsafe financial slice. Freeze the acceptance contract and holdout before optimizing.

Ablate added retrieval, memory, workers or grader stages individually. If a cheap deterministic baseline already passes, the added autonomy must justify its complexity and operational risk. Keep held-out answer keys and scoring annotations out of prompt examples, tuning, memory and the searchable corpus; retain legitimate accessible evidence and split related sources/incidents together.

## Runtime exposure contract

For each case, identify allowed task/initial-state fields and accessible source IDs, plus grader-only answer keys, labels, rubric annotations and reference trajectories. Check the final assembled model messages, memory and tool/retrieval-visible stores during evaluation, not just during tuning. A sealed holdout on disk is insufficient if an agent tool can read its answer key.

Example: the agent may read the task and authorized policy document P3; only the grader may read the expected answer and label file G3. A deterministic fixture/input-manifest check must exclude G3 from all agent-visible sources. Do not detect leakage by banning the answer text itself: P3 can legitimately contain the required fact. Report an unverified exposure boundary as a gap, not a passing leakage check.
