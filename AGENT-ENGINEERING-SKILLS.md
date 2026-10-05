# Sathvik — Agent Engineering

Author: **Sathvik**. Collection revision: **2.0.0**. Nineteen global, framework-agnostic skills. Three unchanged skill implementations retain version 1.0.0; modified/new implementations use 2.0.0.

Models handle uncertainty. Deterministic software handles authority wherever correctness can be specified. Evidence decides whether changes survive. The engineering loop continues beyond generation. Choose the simplest architecture that correctly handles uncertainty; avoid both agentification and brittle deterministic overcorrection.

## Recommended Full Agent Build Flow

UNDERSTAND → MAP UNCERTAINTY → CLASSIFY ARCHITECTURE → BASELINE + EVALS → FREEZE CONTRACTS + INVARIANTS → MODEL/DETERMINISTIC BOUNDARY → AUTHORITY → EVIDENCE FLOW → TOOLS/RETRIEVAL/STATE → BOUNDED ORCHESTRATION → SMALLEST VERTICAL SLICE.

For each material change: **PLAN → IMPLEMENT → RUN → DEBUG → CORRECT → REVIEW**. Reconcile syntax/schema/semantics and evidence; test failures; run matched evals; compare baseline; ablate uncertain complexity; KEEP / REVISE / ROLLBACK. Security, recovery and observability begin in the first slice. Finish with technical defence, verification-before-completion and the authorized release path.

When safe candidates may exist: CONSTRUCT → VERIFY → ADMIT. Bound reconstruction and never weaken constraints, invent support or silently change the authorized task. No admissible candidate or missing required authority ends in honest failure/unsupported status.

## Terminology

| Term | Meaning |
|---|---|
| Agent | Runtime component adaptively choosing actions from observations inside explicit boundaries. |
| Workflow | Software-controlled sequence/graph with known transitions; may include model-powered steps. |
| Tool | Bounded observation/action capability with strict contracts and explicit side effects. |
| State | Typed application-owned facts/status changed through deterministic validated transitions. |
| Memory | Scoped recall with provenance/lifecycle; not authorization or proof of current critical facts. |
| Authority | Trusted right and mechanism to admit actions or commit transitions. |
| Policy | Versioned permissions, invariants and approval rules enforced by trusted software. |
| Guardrail | Boundary control; distinguish probabilistic guidance from deterministic enforcement. |
| Approval | Application-recorded authorized human decision bound to exact action/scope and validity. |
| Evaluation | Observed outputs/effects/trajectories compared with predeclared criteria. |
| Trajectory | Observable proposals/decisions/calls/results/transitions; not private reasoning. |
| Run | Logical task identity with cumulative budgets across attempts/resume. |
| Checkpoint | Durable versioned progress, evidence, pending effects and remaining budgets for safe resume. |
| Evidence ledger | Application-owned observed sources/transformations/computations/receipts with access and lineage; not an automatic truth guarantee. |
| Used support | Observed, accessible evidence checked as support for a particular decision/claim, distinct from retrieval candidates. |
| Uncertainty map | Component-specific model need, reason, consequence and validation before architecture choice. |

## Global installation and methodology

Discovered central storage: `~/.cc-switch/skills` (`skillStorageLocation=cc_switch`, `skillSyncMethod=auto`). Codex/Claude expose central implementations through junctions in their global skills roots. CC Switch database/settings are not edited; UI toggle registration is not inferred from file presence. A fresh session may be needed for catalogue refresh.

Anthropic creator at `~/.cc-switch/skills/skill-creator` governs snapshots, progressive disclosure, official eval/trigger/grading schemas, validator, aggregator and review templates. Audit read all 17 v1 custom skills, all suites/resources, 18 creator files and 22 relevant third-party SKILL.md files. This task did not write third-party source. Third-party files drifted between session snapshots; the report preserves differences and verifies the final installation against a current read-only baseline.

User-supplied Orchestrate observations motivate rules, not statistical/causal claims. Original reports/article were not supplied. No provider choice is prescribed from participation counts. No separate model-selection-and-routing or technical-defence skill: existing owners cover those workflows.

## Skills, scope and evidence

| Skill | Author | Purpose | Triggers | Non-triggers | Relationships | Eval status | Validation | Files |
|---|---|---|---|---|---|---|---|---|
| [agent-architecture](agent-architecture/SKILL.md) | Sathvik | Choose the simplest AI-system architecture that correctly handles the task’s uncertainty. | designing or reviewing runtime autonomy, deciding whether a product needs an agent, or placing reasoning, tools, state and authority boundaries. | ordinary application architecture or executing a coding plan without an AI runtime design decision. | Uncertainty/component boundaries; workflow coordinates lifecycle; orchestration owns next-step controller | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-architecture/evals/evals.json), [evals/trigger-evals.json](agent-architecture/evals/trigger-evals.json), [SKILL.md](agent-architecture/SKILL.md) |
| [agent-cost-and-latency](agent-cost-and-latency/SKILL.md) | Sathvik | Optimize AI-system cost and latency per verified successful outcome using measured budgets. | profiling model/tool/retrieval spend or delays, setting agent run ceilings, choosing model routing/escalation, caching, batching or parallelism under quality constraints. | general application performance without model/agent costs, speculative model recommendations, or reducing tokens without outcome measurements. | Outcome economics/role-routing experiments; orchestration controls transitions, evals owns rigor | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 19/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-cost-and-latency/evals/evals.json), [evals/trigger-evals.json](agent-cost-and-latency/evals/trigger-evals.json), [references/cost-comparison.md](agent-cost-and-latency/references/cost-comparison.md), [SKILL.md](agent-cost-and-latency/SKILL.md) |
| [agent-development-workflow](agent-development-workflow/SKILL.md) | Sathvik | Coordinate the complete engineering lifecycle for substantial AI-agent or model-assisted workflow builds. | building, productionizing or substantially redesigning an agent, adding major tools/state/RAG/orchestration, or evaluating and hardening a whole agent system. | one bug, tiny prompt/schema/API changes, ordinary app work, simple deterministic utilities, conceptual agent explanations, or a narrow task owned by one specialist. | Lifecycle coordination; optional specialist use; installed planning/TDD/debugging/verification retain mechanics | Fresh targeted v2 10/10; without_skill 8/10; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-development-workflow/evals/evals.json), [evals/trigger-evals.json](agent-development-workflow/evals/trigger-evals.json), [references/decision-and-defence.md](agent-development-workflow/references/decision-and-defence.md), [SKILL.md](agent-development-workflow/SKILL.md) |
| [agent-evals](agent-evals/SKILL.md) | Sathvik | Define evaluation-first quality gates for an AI agent or model-powered workflow. | specifying agent success before implementation, building gold task sets, comparing agent variants, or diagnosing outcome and trajectory regressions. | ordinary unit-test writing or tool-interface usability alone without an agent quality measurement question. | Population/scoring/release experiment; testing owns implementation checks; tool-evals isolates interaction | Fresh targeted v2 7/7; old_skill 6/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-evals/evals/evals.json), [evals/trigger-evals.json](agent-evals/evals/trigger-evals.json), [references/scoring.md](agent-evals/references/scoring.md), [SKILL.md](agent-evals/SKILL.md) |
| [agent-failure-recovery](agent-failure-recovery/SKILL.md) | Sathvik | Design bounded retries and durable recovery for AI-agent runs and side effects. | handling interrupted agent execution, ambiguous tool commits, partial completion, checkpoints/resume, poison tasks or retry/timeout policy. | general bug diagnosis, ordinary synchronous exception handling, or session handoff with no runtime recovery problem. | Bounded recovery/unknown effects; state owns checkpoint representation, debugging diagnoses defects | Fresh targeted v2 7/7; old_skill 6/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-failure-recovery/evals/evals.json), [evals/trigger-evals.json](agent-failure-recovery/evals/trigger-evals.json), [SKILL.md](agent-failure-recovery/SKILL.md) |
| [agent-guardrails](agent-guardrails/SKILL.md) | Sathvik | Assemble and verify layered runtime guardrails for an AI system without confusing guidance with enforcement. | designing agent safety/quality containment, abstention gates, policy enforcement, permissions, runtime limits or approval layers, or reviewing a prompt-only guardrail claim. | security threat modeling alone, writing admission code alone, generic input validation, or making a system prompt sound safer. | Layer composition/bypass/false blocking; security threats, admission and approvals have separate owners | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-guardrails/evals/evals.json), [evals/trigger-evals.json](agent-guardrails/evals/trigger-evals.json), [SKILL.md](agent-guardrails/SKILL.md) |
| [agent-observability](agent-observability/SKILL.md) | Sathvik | Instrument AI-agent trajectories so actions, evidence, state and quality can be reconstructed. | designing or reviewing traces/metrics for agent model calls, tools, approvals, retries, state, evals, cost or latency, or debugging an opaque agent run. | general service logging without an agent trajectory, full private reasoning collection, or quality scoring rules alone. | Reconstructable events/actionable signals; evals defines scoring, provenance defines support | Fresh targeted v2 7/7; old_skill 6/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-observability/evals/evals.json), [evals/trigger-evals.json](agent-observability/evals/trigger-evals.json), [SKILL.md](agent-observability/SKILL.md) |
| [agent-orchestration](agent-orchestration/SKILL.md) | Sathvik | Design bounded next-step control for an AI runtime, from fixed routing to adaptive tool/retrieval choice and justified workers. | choosing who controls the next step, implementing agent routing, handoffs, fan-out/fan-in, shared state, cancellation or aggregate budgets. | coding-subagent dispatch, ordinary parallel utilities, whole-system lifecycle planning alone, or tool contracts without a runtime control-flow question. | Fixed/adaptive control; optional justified workers; coding-subagent dispatch stays in Superpowers | Fresh targeted v2 8/8; old_skill 8/8; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-orchestration/evals/evals.json), [evals/trigger-evals.json](agent-orchestration/evals/trigger-evals.json), [SKILL.md](agent-orchestration/SKILL.md) |
| [agent-security](agent-security/SKILL.md) | Sathvik | Threat-model and harden AI-agent trust boundaries, tools and data flows. | reviewing agent prompt injection, malicious retrieval/tool output, exfiltration, confused-deputy execution, tool poisoning or sandbox/credential boundaries. | general application security without a model/tool trust flow, or layering operational quality guardrails alone. | Model-mediated attacker-to-effect paths; existing hardening remains baseline application security | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-security/evals/evals.json), [evals/trigger-evals.json](agent-security/evals/trigger-evals.json), [SKILL.md](agent-security/SKILL.md) |
| [agent-state-and-memory](agent-state-and-memory/SKILL.md) | Sathvik | Design agent runtime state, checkpoints and memory without confusing recall with authoritative facts. | deciding what an AI system should persist, handling long-running context, cross-run memory, checkpoint/resume, provenance, expiry or deterministic state transitions. | coding-session context setup, a normal database migration, or conversational summarization with no runtime persistence design. | Runtime persistence/source of truth; context-engineering owns coding-session packing | Unchanged instructions: retained v1 10/10; no fresh v2 behavior run; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-state-and-memory/evals/evals.json), [evals/trigger-evals.json](agent-state-and-memory/evals/trigger-evals.json), [SKILL.md](agent-state-and-memory/SKILL.md) |
| [agent-testing](agent-testing/SKILL.md) | Sathvik | Build a risk-based test pyramid and CI verification strategy for an AI-agent runtime. | implementing agent tests across deterministic admission/state, schemas, tool contracts, integration, trajectories, eval suites, adversarial behavior or restart/recovery. | ordinary test-first coding without an AI runtime, writing a gold-set scoring strategy alone, or browser automation unrelated to agent behavior. | Runtime test pyramid/CI and fault fixtures; TDD mechanics and gold evaluation remain separate | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](agent-testing/evals/evals.json), [evals/trigger-evals.json](agent-testing/evals/trigger-evals.json), [SKILL.md](agent-testing/SKILL.md) |
| [deterministic-authority](deterministic-authority/SKILL.md) | Sathvik | Build deterministic admission and authorization between model proposals and side effects. | an LLM can propose state changes, money movements, permission decisions or actions subject to executable constraints, or reviewing whether a model can override policy. | purely advisory text generation or ordinary business logic with no model-to-action trust boundary. | Executable admission/invariants; approval UX and layered composition remain separate | Fresh targeted v2 6/6; old_skill 6/6; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](deterministic-authority/evals/evals.json), [evals/trigger-evals.json](deterministic-authority/evals/trigger-evals.json), [SKILL.md](deterministic-authority/SKILL.md) |
| [evidence-provenance](evidence-provenance/SKILL.md) | Sathvik | Design and verify source-to-decision-to-output evidence lineage for AI systems. | implementing evidence ledgers, distinguishing retrieved from used support, reconciling decision/explanation/citation IDs, or preventing fabricated, stale or spoofed provenance across tools and model stages. | retrieval ranking/chunking alone, ordinary bibliography formatting, general logging, coding-source lookup, or answers with no evidence-lineage contract. | Source/transform/decision/claim reconciliation; RAG retrieves, observability records, authority admits | Fresh targeted v2 9/9; without_skill 9/9; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](evidence-provenance/evals/evals.json), [evals/trigger-evals.json](evidence-provenance/evals/trigger-evals.json), [references/ledger-and-reconciliation.md](evidence-provenance/references/ledger-and-reconciliation.md), [SKILL.md](evidence-provenance/SKILL.md) |
| [human-in-the-loop](human-in-the-loop/SKILL.md) | Sathvik | Place proportional human review and approval gates in an AI system's execution path. | designing approval/escalation for agent actions with financial, external, destructive or permission impact, preview-before-commit flows, or uncertainty that warrants human judgment. | requesting routine coding confirmation, imposing approval on harmless reads, or deterministic authorization logic alone. | Proportional human review and bound grants; authority enforces and cannot waive hard rules | Unchanged instructions: retained v1 9/9; no fresh v2 behavior run; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](human-in-the-loop/evals/evals.json), [evals/trigger-evals.json](human-in-the-loop/evals/trigger-evals.json), [SKILL.md](human-in-the-loop/SKILL.md) |
| [prompt-engineering](prompt-engineering/SKILL.md) | Sathvik | Design concise, versioned production prompts with responsibilities, trust boundaries and measurable behavior. | building or revising deployed agent/workflow prompts, defining instruction hierarchy, tool/output guidance, uncertainty or termination, or evaluating a prompt regression. | generic prompt tricks, one-off prose requests, repository context setup, or using a prompt as authorization/security enforcement. | Shipped model responsibilities/outputs; prompts guide, code enforces; context-engineering owns sessions | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](prompt-engineering/evals/evals.json), [evals/trigger-evals.json](prompt-engineering/evals/trigger-evals.json), [SKILL.md](prompt-engineering/SKILL.md) |
| [rag-engineering](rag-engineering/SKILL.md) | Sathvik | Design, diagnose and evaluate retrieval-grounded generation with evidence provenance. | building or improving document-backed AI answers, measuring retrieval quality, investigating unsupported citations, or deciding whether chunking, hybrid search, reranking or query transformation helps. | ordinary database search without generation, general browsing, or memory persistence design without a retrieval-quality problem. | Retrieval/assembly/grounded-generation pipeline; provenance owns end-to-end ledger; source-driven owns docs lookup | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](rag-engineering/evals/evals.json), [evals/trigger-evals.json](rag-engineering/evals/trigger-evals.json), [references/retrieval-scoring.md](rag-engineering/references/retrieval-scoring.md), [SKILL.md](rag-engineering/SKILL.md) |
| [structured-output-design](structured-output-design/SKILL.md) | Sathvik | Design and validate model-produced structured proposals before application use. | specifying JSON or typed outputs from an LLM, handling refusals or malformed generations, validating semantic constraints, or migrating model output contracts. | routine API serialization or database schema design without model-generated data. | Generated proposal shape/semantics; provenance reconciles support; authority authorizes effects | Fresh targeted v2 7/7; old_skill 7/7; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](structured-output-design/evals/evals.json), [evals/trigger-evals.json](structured-output-design/evals/trigger-evals.json), [references/proposal-contract.md](structured-output-design/references/proposal-contract.md), [SKILL.md](structured-output-design/SKILL.md) |
| [tool-design](tool-design/SKILL.md) | Sathvik | Design model-facing tools with coherent capabilities, strict contracts and predictable side effects. | exposing APIs or operations to an LLM agent, redesigning ambiguous agent tools, or specifying tool names, descriptions, arguments, results and execution semantics. | ordinary REST design with no model consumer, MCP transport implementation alone, or evaluating tool selection without changing contracts. | Model-facing capability contracts; existing API/MCP skills own protocol/backend mechanics | Fresh targeted v2 6/6; old_skill 6/6; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](tool-design/evals/evals.json), [evals/trigger-evals.json](tool-design/evals/trigger-evals.json), [SKILL.md](tool-design/SKILL.md) |
| [tool-evals](tool-evals/SKILL.md) | Sathvik | Measure whether an LLM agent can discover, select, compose and recover with a tool surface. | testing model-facing tool usability, argument accuracy, response interpretation, multi-step tool chains, unnecessary calls or tool failure handling. | backend API contract tests alone, MCP server scaffolding, or whole-agent answer-quality benchmarking without a tool-use question. | Discovery/selection/argument/chain usability; agent-evals owns whole-task quality | Unchanged instructions: retained v1 9/9; no fresh v2 behavior run; routing proxy 20/20, actual invocation unverified | Official validator + local structural checks passed on stage; installed audit in report | [evals/evals.json](tool-evals/evals/evals.json), [evals/trigger-evals.json](tool-evals/evals/trigger-evals.json), [SKILL.md](tool-evals/SKILL.md) |

## Responsibilities and verification limits

Lifecycle coordinates boundaries, without importing all specialists on every task. Optional companion names are discoverability hints, not mandatory circular dependencies. No custom production scripts were added. Evidence membership is necessary, not sufficient for support; semantic review is distinguished from deterministic predicates.

Behavior suites retain v1 coverage and add targeted revision cases. Sixteen modified/new skills have fresh paired targeted/adversarial runs; unchanged state/memory, approval and tool-usability procedures retain clearly labeled v1 evidence. Not every stored v1 case was re-executed against v2. Single samples are smoke evidence, not repeated-run reliability. Baseline ties do not establish incremental benefit.

Current Claude CLI preflight is not logged in; untouched official trigger runner fails with WinError 10038 on Windows pipes. Infrastructure failure is not a valid negative trigger result. The 380-case metadata-selection proxy is separate from actual automatic invocation/optimization. Human review and repeated held-out variance remain outstanding. See revision validation report and official review HTML.

## Directory structure

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
