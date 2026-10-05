---
name: prompt-engineering
description: >-
  Design concise, versioned production prompts with responsibilities, trust boundaries and measurable behavior. Use when building or revising deployed agent/workflow prompts, defining instruction hierarchy, tool/output guidance, uncertainty or termination, or evaluating a prompt regression. Do not use for generic prompt tricks, one-off prose requests, repository context setup, or using a prompt as authorization/security enforcement.
metadata:
  collection: "Agent Engineering"
  version: "2.0.1"
---

# Prompt Engineering

Treat a production prompt as a versioned interface to a bounded reasoning component. It cannot confer permissions or enforce a security boundary.

## Define and minimize the contract

1. Identify the model's responsibilities, inputs, observable outputs and failure/abstention behavior. Assign calculations, permissions, state transitions and budgets to deterministic code. Remove tasks the model is being asked to guess despite available authoritative data.
2. Separate instruction hierarchy from untrusted content. Put stable role/responsibilities and boundaries in trusted instructions, current task and relevant evidence in clear sections, and source data in labeled containers with provenance. Follow the actual provider/harness hierarchy; do not let a quoted document redefine it.
3. State scope, forbidden assumptions, tool choice/preconditions, output contract, evidence requirements and stop conditions in short concrete rules. Reference authoritative schema/tool definitions instead of pasting conflicting copies. Tell the model what to do when facts, access or required evidence are absent: construct a supported candidate or retrieve a missing fact within budget, then validate; otherwise abstain, return a typed gap or request a meaningful clarification. Do not default to refusal when a safe valid candidate can be established.
4. Include few-shot examples only for ambiguous decisions or recurrent errors. Cover safe refusal/insufficient evidence when useful, but keep examples distinct from held-out evals. Do not add examples that teach fabricated IDs or approval from confidence.
5. Place stable instructions and current task-critical context deliberately; bound retrieved material and remove stale or irrelevant instructions. Test placement rather than assuming every model handles long context identically. Summarization preserves source attribution and uncertainty; it cannot create authority.

## Evaluate changes as code changes

6. Save prompt version/hash, model/sampling, schema/tool versions and context-assembly version. Externalize dynamic data rather than baking customer/project facts into a global prompt. Make prompt rollbacks possible without incompatible state/schema changes.
7. Freeze representative cases and a baseline before changing the prompt. Test normal tasks, ambiguity, missing evidence, poisoned documents, refusal, unsupported actions, output validation and termination. Judge observable output/calls against deterministic assertions and a calibrated semantic rubric where needed.
8. Change one responsibility or example at a time; run paired comparisons and repeated stochastic cases. Retain improvements that beat baseline noise without violating safety, latency or cost gates. A longer defensive prompt is not a substitute for enforced constraints.
9. Trace failures to instruction conflict, absent context, schema mismatch, tool affordance or capability limits before adding more wording. Delete redundant/contradictory clauses and unhelpful examples. Resolve semantic policy ambiguity in software/specification, not by telling the model to improvise.

Deliver the prompt artifact, responsibility/trust table, version metadata, eval cases and measured comparison/rollback decision. Example rule: “Use only returned resource IDs; if evidence is missing, return insufficient_evidence.” The executor still checks IDs and authority.

Coding-session context is out of scope (a context-engineering skill may cover it); this skill governs model instructions shipped as part of a product. Use structured-output-design for schemas and agent-evals for measurement; neither requires a giant prompt.

State that model output is a fallible proposal. Returned evidence IDs must describe support actually used for decisions/claims, not every retrieved item. Natural-language explanation must agree with the structured decision and supported facts. Test contradictory explanations and fabricated/irrelevant IDs. Prompts request these behaviors; executable reconciliation and admission enforce decidable constraints.
