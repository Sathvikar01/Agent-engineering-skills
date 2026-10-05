# Sathvik — Agent Engineering: revision 2 validation report

Author: Sathvik. Date: 5 October 2026.

## Installation and acceptance

19 physical global skills are installed in `~/.cc-switch/skills`, exposed through 19 verified junctions each in Codex and Claude global roots. Catalogue hardlinks expose the same content. CC Switch database/settings were not edited; UI toggle registration is unverified. The old orchestration live name is removed, with its original physical directory retired into the workspace and an immutable v1 snapshot retained.

**Bounded structural/behavior/routing-proxy gates passed. The full acceptance gate is NOT completely verified:** actual automatic invocation/official description optimization, repeated held-out variance and human review remain unresolved. No production-readiness certification is claimed.

## Audit, changes and scope

Read every v1 custom SKILL.md, all 51 behavioral cases, all 340 trigger queries and four references; no custom production scripts existed. Read all 18 installed Anthropic creator files and 22 relevant third-party SKILL.md files, plus three newly visible architecture/interview command files after the inventory refresh. Their explicitly invoked general refactor/interview workflows remain complementary; no additional agent specialist was discovered. Preserve v1 files/evaluation history. Rules are motivated by the user-supplied Orchestrate observations; original reports/article were not provided and no external statistics or causality are claimed.

Third-party bodies inspected: brainstorming, writing-plans, planning-and-task-breakdown, incremental-implementation, spec-driven-development, context-engineering, source-driven-development, systematic-debugging, debugging-and-error-recovery, verification-before-completion, test-driven-development, subagent-driven-development, dispatching-parallel-agents, doubt-driven-development, documentation-and-adrs, api-and-interface-design, mcp-builder, security-and-hardening, observability-and-instrumentation, performance-optimization, research and citation-management. Later command inspection: grill-me, grill-with-docs and improve-codebase-architecture. Exact paths and original source hashes are retained in the methodology/overlap audit; the current inventory contains 514 skill metadata records.

Modified existing skills: agent-architecture, agent-cost-and-latency, agent-evals, agent-failure-recovery, agent-guardrails, agent-observability, agent-security, agent-testing, deterministic-authority, prompt-engineering, rag-engineering, structured-output-design, tool-design.

Created: agent-development-workflow and evidence-provenance. Renamed/refactored: multi-agent-orchestration → agent-orchestration. Kept unchanged: agent-state-and-memory, human-in-the-loop, tool-evals.

No model-selection-and-routing skill: architecture owns role requirements, orchestration owns route control, evals owns comparisons and cost/latency owns economics. Technical defence stays inside lifecycle completion.

Major additions:

- Simplest architecture that correctly handles uncertainty; reject both unnecessary agentification and fragile semantic heuristics.
- Complete PLAN → IMPLEMENT → RUN → DEBUG → CORRECT → REVIEW loop; actual vertical slice, decision log, human ownership and direct technical defence.
- Model fallibility and CONSTRUCT → VERIFY → ADMIT; bounded supported repair under unchanged rules, authority and task intent, then honest terminal failure when no admissible candidate exists.
- Source/normalization/ledger/decision/claim lineage; retrieved ≠ visible ≠ used support; reject invented or unrelated IDs and contradictory explanation.
- Semantic consistency beyond JSON/schema, role-specific model experiments, tool use/non-use and pre/postconditions, contract-preserving fallback and actionable telemetry.
- Baseline/variant metric-specific gates, repeatable evaluation path and component ablations; no framework/multi-agent/extra-model benefit without evidence.

## Behavioral evidence

Fresh V2 evaluation: 34 selected cases in two configurations, 68 runs over 16 modified/new skills. Independently graded expectations: **116/116** with revisions versus **111/116** baseline. 4 skills improve observed case scores, 12 tie and 0 regress. Modified skills use frozen v1; new skills use no-skill baselines. Configurations are visible to graders, not blinded.

Across preserved revision iterations, 88 graded runs are archived; the selected final comparison contains 68. Each modified skill has its original adversarial regression and new targeted case executed; each new skill has all three cases executed. Three unchanged procedures retain labeled v1 evidence. The global bundle has 71 stored cases; not every retained v1 case was rerun against v2. Expectations are withheld from executors. Fresh per-skill/configuration executors handle cases sequentially. Interrupted security runs were resumed by fresh executors within their assigned configuration, with existing artifacts disclosed; this is a continuity exception. One sample per case does not measure repeated-run variance or statistical benefit; tied cases do not demonstrate material improvement.

| Skill | V2 | Baseline | Comparison |
|---|---:|---:|---|
| agent-architecture | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| agent-cost-and-latency | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| agent-development-workflow | 10/10 | 8/10 (without_skill) | Improved smoke score |
| agent-evals | 7/7 | 6/7 (old_skill) | Improved smoke score |
| agent-failure-recovery | 7/7 | 6/7 (old_skill) | Improved smoke score |
| agent-guardrails | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| agent-observability | 7/7 | 6/7 (old_skill) | Improved smoke score |
| agent-orchestration | 8/8 | 8/8 (old_skill) | Tie; incremental benefit unproven |
| agent-security | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| agent-testing | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| deterministic-authority | 6/6 | 6/6 (old_skill) | Tie; incremental benefit unproven |
| evidence-provenance | 9/9 | 9/9 (without_skill) | Tie; incremental benefit unproven |
| prompt-engineering | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| rag-engineering | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| structured-output-design | 7/7 | 7/7 (old_skill) | Tie; incremental benefit unproven |
| tool-design | 6/6 | 6/6 (old_skill) | Tie; incremental benefit unproven |

Executable local fakes/tests are preserved with actual command logs. Graders inspect source and rerun relevant code under bundled Python; some executors also used system Python 3.11.9. Proposed design checks are labeled unexecuted. Local tests do not certify distributed storage, provider adapters, full JSON Schema support or general entailment.

## Failed evals and corrections

- agent-development-workflow case 1 without_skill: Defines baseline/multidimensional critical gates before large implementation and a repeatable run/debug/correct/review path with vertical slice. Evidence: response.md supplies held-out baselines and multidimensional release gates plus a local fixture -> calculation -> cited answer -> approval -> fake ledger slice. However it stops at First execute this locally, then replace the fake adapter and a suggested failure review with corrective action. It does not define the asserted repeatable run/debug/correct/rerun/review path or specify review decisions after rerunning a correction. Gates/slice alone cannot satisfy the whole bundled assertion.
- agent-development-workflow case 2 without_skill: Bounds timeout/alternative paths and reports no-admissible status; trace links source/decision/effect and evidence. Evidence: Bounded search and terminal statuses are verified: MAX_CANDIDATES=2; timeout one call; two invalid candidates no_valid_candidate and no effect, also independently probed. But no source/decision/effect evidence trace is implemented or saved: Decision stores only final proposal, unassociated reason strings and attempt count; FakeLedger stores request->proposal. Rejected candidate payloads, source evidence/version or used-support marker, admission event and linked execution receipt are absent. A final receipt_id and test success are insufficient evidence for the bundled trace requirement.
- agent-evals case 4 old_skill: Specifies same gold/version/configuration comparison and verifier ablation plus an obvious repeatable command/path. Evidence: response.md gives detailed common100-case manifest/version/settings/reset controls and baseline/shadow/active verifier ablation, but nowhere supplies an obvious repeatable command or named runner/spec/result path. Only response.md exists in outputs; there is no eval-plan or runnable harness. The conjunction therefore lacks required command/path evidence.
- agent-failure-recovery case 2 old_skill: Does not blindly resend a payment or promise exactly-once without provider support. Evidence: FAIL: policy text correctly prohibits blind timeout replay/exactly-once claims, and supplied test blocks status unknown. However inspected Run.dispatch only special-cases unknown and permission_blocked: committed or retained pending operations fall through to another dispatch. Independent eval-2-old_skill.log reproduces a second call for the same committed payment and a replay of pending after simulated prior dispatch/unrecorded outcome. This contradicts response pseudocode 'reuse a verified committed receipt' and 'unresolved pending payments as unknown'. These are concrete fake-state defects, not solely missing production crash tests. No real payment or actual OS crash was performed.
- agent-observability case 4 old_skill: Defines at least three signals with baseline or provisional baseline, threshold, window/denominator, severity and owner/response. Evidence: Four contracts define fields/populations/denominators/windows/actions, and response candidly leaves history unavailable, but it explicitly says thresholds must be obtained from operators and provides no provisional thresholds or named severities/owners for at least3 signals. Only immediate safety breach containment gives an implicit threshold; required conjunction is missing in response.md and signal_contracts.json.

All preserved failed assertions by exact run (including superseded iterations):

- `agent-cost-and-latency-workspace/iteration-1/eval-2-adversarial/old_skill/run-1/grading.json`: Measures end-to-end cost per success and tail latency after the change. Evidence: FAIL: response explicitly says no latency or outcome experiment executed; representative tasks/production measurements absent. Complete-task p50/p95 and all-attempt spend/verified-success denominator are specified as future matched experiment. No actual post-change end-to-end measurement supports the exact assertion; local10-test runtime is expressly not service latency. Verification log: work/v2/independent-verification/cost/eval-2-old_skill.log
- `agent-cost-and-latency-workspace/iteration-1/eval-2-adversarial/with_skill/run-1/grading.json`: Measures end-to-end cost per success and tail latency after the change. Evidence: FAIL: response explicitly labels optimization experiment unexecuted. It proposes matched cold/warm cache on/off gold runs, complete spend including failed retries/cache overhead divided by verified successes, and p50/p95 verified-completion latency, but no implementation cohort/spend-success results/tail samples after change exist. Actual31 fake checks and their runtime establish local invariants only, not this exact measurement assertion. Verification log: work/v2/independent-verification/cost/eval-2-with_skill.log
- `agent-development-workflow-workspace/iteration-1/eval-1-representative/without_skill/run-1/grading.json`: Defines baseline/multidimensional critical gates before large implementation and a repeatable run/debug/correct/review path with vertical slice. Evidence: response.md supplies held-out baselines and multidimensional release gates plus a local fixture -> calculation -> cited answer -> approval -> fake ledger slice. However it stops at First execute this locally, then replace the fake adapter and a suggested failure review with corrective action. It does not define the asserted repeatable run/debug/correct/rerun/review path or specify review decisions after rerunning a correction. Gates/slice alone cannot satisfy the whole bundled assertion.
- `agent-development-workflow-workspace/iteration-1/eval-2-adversarial/without_skill/run-1/grading.json`: Bounds timeout/alternative paths and reports no-admissible status; trace links source/decision/effect and evidence. Evidence: Bounded search and terminal statuses are verified: MAX_CANDIDATES=2; timeout one call; two invalid candidates no_valid_candidate and no effect, also independently probed. But no source/decision/effect evidence trace is implemented or saved: Decision stores only final proposal, unassociated reason strings and attempt count; FakeLedger stores request->proposal. Rejected candidate payloads, source evidence/version or used-support marker, admission event and linked execution receipt are absent. A final receipt_id and test success are insufficient evidence for the bundled trace requirement.
- `agent-evals-workspace/iteration-2/eval-4-v2-targeted/old_skill/run-1/grading.json`: Specifies same gold/version/configuration comparison and verifier ablation plus an obvious repeatable command/path. Evidence: response.md gives detailed common100-case manifest/version/settings/reset controls and baseline/shadow/active verifier ablation, but nowhere supplies an obvious repeatable command or named runner/spec/result path. Only response.md exists in outputs; there is no eval-plan or runnable harness. The conjunction therefore lacks required command/path evidence.
- `agent-failure-recovery-workspace/iteration-1/eval-2-adversarial/old_skill/run-1/grading.json`: Does not blindly resend a payment or promise exactly-once without provider support. Evidence: FAIL: policy text correctly prohibits blind timeout replay/exactly-once claims, and supplied test blocks status unknown. However inspected Run.dispatch only special-cases unknown and permission_blocked: committed or retained pending operations fall through to another dispatch. Independent eval-2-old_skill.log reproduces a second call for the same committed payment and a replay of pending after simulated prior dispatch/unrecorded outcome. This contradicts response pseudocode 'reuse a verified committed receipt' and 'unresolved pending payments as unknown'. These are concrete fake-state defects, not solely missing production crash tests. No real payment or actual OS crash was performed.
- `agent-observability-workspace/iteration-1/eval-4-v2-targeted/old_skill/run-1/grading.json`: Defines at least three signals with baseline or provisional baseline, threshold, window/denominator, severity and owner/response. Evidence: FAIL: JSON/response define seven useful measurements and denominators, null baselines and proposed common hourly/daily windows, but common.threshold_policy explicitly says numeric alert thresholds unset until baseline/coverage exists. There are no three complete provisional/qualitative threshold, severity and owner contracts. Individual JSON contracts lack all three fields; safety says confirmed breach immediate containment but cannot supply three such definitions. Response mentions severity and generic evaluator owner without assigning severity/owner per signal. Independent log records every missing field. Structural validator PASS only checks presence of other fields and does not test this assertion.
- `agent-observability-workspace/iteration-2/eval-4-v2-targeted/old_skill/run-1/grading.json`: Defines at least three signals with baseline or provisional baseline, threshold, window/denominator, severity and owner/response. Evidence: Four contracts define fields/populations/denominators/windows/actions, and response candidly leaves history unavailable, but it explicitly says thresholds must be obtained from operators and provides no provisional thresholds or named severities/owners for at least3 signals. Only immediate safety breach containment gives an implicit threshold; required conjunction is missing in response.md and signal_contracts.json.

Starter-bug failures in the lifecycle case are intentional fixtures, preserved before correction. Infrastructure command-discovery failures are retained separately from assertion failures. Any revision iterations and old grades remain in the evidence archive; tests were not relabeled to manufacture success.

The first cost/latency task required measured end-to-end economics without providing a workload. Both configurations correctly left that experiment unexecuted and failed the literal measurement assertion. Preserved those failures; revised only that eval prompt to supply a local executable 40-task fake clock/billing workload, keeping all four assertions and skill instructions unchanged. Iteration-2 measurements include failure and retry charges, independently verified successes and nearest-rank p95 terminal latency. These synthetic measurements do not establish real provider performance or a pre-change improvement. Initial baseline SQLite cleanup errors and a guardrails PowerShell StrictMode empty-pipeline Count failure remain archived beside corrected reruns.

Source review corrected architecture-table cells that still described escalation to another architecture. Both selected cases/configurations were rerun in iteration-2; iteration-1 remains archived. Independent grading also found inferred raw success counts from undefined quality percentages in eval-design output. Agent-evals now preserves metric definitions/units/denominators and was rerun in iteration-2 without changing assertions. Original unsupported claims are retained. Independent provenance probing found that the no-skill fake records a source version but does not bind its decision to that version; the revised-skill fake rejects a changed version. The original assertion did not require that binding, so the passing rubric is preserved and the uncovered gap is reported separately. Orchestration output review flags ambiguous receipt-before-dispatch phrasing: an intent can precede dispatch, but an actual receipt follows an observed effect. The skill source uses the correct ordering.

Independent security probes also reproduce a baseline fake accepting an arbitrary bounded summary under genuine D3. The revised fake checks an exact quote, which is a narrower fixture check and still does not prove general entailment. This is preserved as a semantic-support coverage limitation, not invented as a failing provenance-identity assertion.

Supplemental probes found the first revised observability fake accepting an orphan parent span as complete and the first revised testing controller admitting another effect after terminal reentry. Their bounded rubric scores are preserved. Added explicit orphan/cyclic/missing-event reconstruction faults and terminal-controller/checkpoint reentry properties, then reran both paired jobs in iteration-2 and separately reprobed those behaviors. Both original synthetic redactors also permit arbitrary credential-like text in allowlisted fields. Source and fixture refinements do not establish universal trace completeness, provider semantics or privacy enforcement.

The observability iteration-2 signal executor corrected a safety denominator and extended 14 checks to 15. Its intermediate raw 14-check log was overwritten; a correction record and final 15-check execution are retained. Independent copied-source reruns and closure probes use the saved final source; missing intermediate logs are not fabricated.

A separate refinement contract was frozen before those iteration-2 runs: metric definitions, trace closure faults and terminal reentry must pass with actual artifact/probe evidence. All three revised checks pass; their results are archived separately and are not added to original assertion denominators.

A bundled PowerShell startup threw OutOfMemoryException before a file-read command executed. A later retry with login=false succeeded; no configuration was changed. Although the shell argument requested the built-in executable, fresh process inspection identifies the root command host as bundled pwsh 7.6.5. This environment failure and actual runtime distinction are preserved separately from skill assertions.

## Trigger evidence

380 balanced queries (190 positive, 190 negative), with 35 descriptions (19 custom plus 16 adjacent existing). Independent catalogue-selection proxy: **379/380**. All skills meet the predeclared >=9/10 gate in each class. This is not automatic harness activation or the official Claude optimizer.

The one miss selected orchestration/state/guardrails for centrally reserved worker budgets rather than additionally cost-and-latency. Kept as a scope ambiguity, without relabeling or overfitting descriptions. New lifecycle, provenance and broadened orchestration pass all their proxy cases.

Official tooling preflight was repeated in a separate evidence directory on 5 October 2026: `claude -p` still reports Not logged in; untouched `scripts.run_eval` still raises WinError10038 on Windows subprocess pipes. Its generated 0/1 result is an infrastructure failure, not a measured negative activation. Official description optimization cannot run in this environment; neither authentication nor third-party code was modified. Both attempts and all 19 official-template trigger review pages are available.

## Validation commands and integrity

Runtime: bundled Python invoked with `-X utf8 -B`; locally staged PyYAML dependencies only. Governing tools are untouched.

- `python -X utf8 -B work/v2_audit.py`: official quick_validate for each staged skill plus frontmatter/name/author/scope, suite schemas, references, duplicates, snapshot and third-party hashes.
- `python -X utf8 -B work/v2_finish_evidence.py`: exact assertion contract checks, official aggregate_benchmark and generate_review.py; generated metadata corrected to actual run count and unavailable usage, with raw official output retained.
- `python -X utf8 -B work/v2_score_routes.py`: coverage/name checks and predeclared per-class proxy scoring.
- `work/v2_install_global.ps1`: snapshot equality/collision guards, scoped copy/junction migration, per-file hash verification, safe old-name retirement.
- `python -X utf8 -B work/v2_audit.py --installed`: actual installed content/frontmatter/references, all 19 junction targets and obsolete-name absence verified.
- Official package_skill creates 19 .skill archives; official packages omit evals, so the full collection ZIP retains them.

The current pre-install third-party inventory contains 5,651 files; its hashes match after installation. The initial V2 audit failed against 414 obsolete bundled-plugin paths from v1. A later continuation detected 194 paths differing from the earlier v2 snapshot (91 changed, 103 absent), including third-party design skills and one plugin configuration, plus 441 newly inventoried files. Both failed audits, prior inventories and exact differences are preserved. No task write targeted those paths; hashes alone do not establish the cause. A read-only baseline refresh precedes installation, so post-refresh integrity is verified but full-session third-party hash stability is NOT claimed. V1 custom snapshot hashes remain unchanged.

## Cross-skill adversarial review

Audited autonomy/semantic uncertainty, framework/workers benefit, proposal-to-state admission, unsupported support/semantic contradictions, premature refusal, retry/step ceilings, reconstructable runs, restart state/unknown effects, high-impact permissions, eval versus telemetry, tool choice guidance and evidence-based design defence. Worker routes are optional after fixed/single-agent routing. No mandatory dependency cycle; repeated principles remain contextual to their enforcement boundary.

## Exact unresolved risks

- Actual Codex/Claude automatic invocation and official optimizer unavailable. V1 skills appeared in the refreshed Codex catalogue, but that does not establish V2 activation. CC Switch UI registration was not performed.
- Third-party files drifted between snapshots during this continuing task. Exact changes and missing paths are recorded; full-session third-party stability is unverified despite unchanged hashes across the final installation boundary.
- Human review of official viewers, calibrated human semantic labels, repeated same-version stochastic runs and broader held-out generalization remain unverified.
- Exact inherited model/sampling identifiers and uniform token/latency usage are not supplied; omitted, not zero or character-derived tokens.
- Fresh evaluation targets modifications; retained v1 cases and unchanged-skill evidence are labeled. Smoke ties do not prove added benefit.
- Fakes, typed comparisons and design artifacts do not prove production provider idempotency, durable distributed storage, general natural-language entailment, browser/E2E coverage or full schema dialect/provider support.
- Original cost fakes also exposed strict bool/integer validation, pending-reservation return semantics and cross-tool idempotency-key scoping gaps outside their literal assertions. Recorded probes are coverage limitations; passing smoke rubrics do not certify the generated fake as a production implementation.

## Final list, tree and workflow

The collection catalogue lists all 19 skills, author, purpose, triggers/non-triggers, relationships, eval/validation status, actual files, shared terminology and the complete recommended build flow. It is included beside the skill folders in the full ZIP.

Final workflow: understand → map uncertainty → choose task-fit architecture → baseline/evals → freeze contracts → model/code boundary and authority → evidence flow → necessary tools/retrieval/state → bounded control → vertical slice → plan/implement/run/debug/correct/review → semantic and evidence reconciliation → failure tests → matched evals/ablations → retain/revise/rollback → technical defence → verification → authorized release.

```text
skills/
  AGENT-ENGINEERING-SKILLS.md
  agent-architecture/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  agent-cost-and-latency/
    evals/evals.json
    evals/trigger-evals.json
    references/cost-comparison.md
    SKILL.md
  agent-development-workflow/
    evals/evals.json
    evals/trigger-evals.json
    references/decision-and-defence.md
    SKILL.md
  agent-evals/
    evals/evals.json
    evals/trigger-evals.json
    references/scoring.md
    SKILL.md
  agent-failure-recovery/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  agent-guardrails/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  agent-observability/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  agent-orchestration/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  agent-security/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  agent-state-and-memory/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  agent-testing/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  deterministic-authority/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  evidence-provenance/
    evals/evals.json
    evals/trigger-evals.json
    references/ledger-and-reconciliation.md
    SKILL.md
  human-in-the-loop/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  prompt-engineering/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  rag-engineering/
    evals/evals.json
    evals/trigger-evals.json
    references/retrieval-scoring.md
    SKILL.md
  structured-output-design/
    evals/evals.json
    evals/trigger-evals.json
    references/proposal-contract.md
    SKILL.md
  tool-design/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
  tool-evals/
    evals/evals.json
    evals/trigger-evals.json
    SKILL.md
```
