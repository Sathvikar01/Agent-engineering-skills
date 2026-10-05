---
name: structured-output-design
description: >-
  Design and validate model-produced structured proposals before application use. Use when specifying JSON or typed outputs from an LLM, handling refusals or malformed generations, validating semantic constraints, or migrating model output contracts. Do not use for routine API serialization or database schema design without model-generated data.
metadata:
  collection: "Agent Engineering"
  version: "2.0.0"
---

# Structured Output Design

Treat generated data as a proposal. Parsing and schema validation establish shape; application rules establish meaning; authorization establishes permission. None implies the others.

## Define the consumer contract

1. List the exact decisions the consumer must make. Remove ornamental fields and model assertions of permission or success. Distinguish model-extracted/proposed fields from trusted server-generated identity, time, state version and calculations.
2. Choose a JSON Schema dialect and the supported subset of the actual provider; verify support rather than assuming full schema coverage. Use enums for closed choices, required fields for necessary decisions, and explicit optional/missing/null semantics. Bound lengths, arrays and numeric ranges; reject extra properties where supported.
3. Use discriminated variants for materially different states: proposed action, insufficient evidence, refusal or no action. Require variant-specific fields and disallow contradictory combinations. Handle provider-level refusal, truncation and transport errors outside the success schema when required by the API.
4. Include contract version and evidence references when the consumer needs them. Do not let the model generate an execution receipt or approval token. Read [proposal example](references/proposal-contract.md) when specifying action unions and admission stages.

## Validate in separate stages

5. Bound bytes/depth before parsing. Decide how to handle duplicate keys and non-finite numbers; parsers can silently disagree. Validate shape, then cross-field rules, units, identifiers, tenant ownership, evidence provenance, freshness and business constraints. Recompute money and permissions in trusted code.
6. Normalize only explicitly allowed representational differences. Preserve raw output and validation errors for provenance under privacy controls. Canonicalize the validated representation with a documented algorithm for hashing/deduplication; changing meanings is not normalization. Never default a missing safety-critical field to a permissive value.
7. Promote only validated fields into a typed proposal. Pass it to deterministic-authority for authorization; keep model output distinct from authoritative application state. A valid JSON object can still contain a fabricated ID or prohibited action.

## Recover and evolve

8. Distinguish transport errors, provider refusal/truncation, parse failure, schema failure and semantic rejection. Fail closed on admission failure. Permit bounded reconstruction for recoverable formatting or semantic candidate errors using safe validation feedback, authorized facts and the unchanged contract; revalidate from the start. Do not execute the original output while reconstruction runs or repair missing evidence into invented facts. Construct → verify → admit: try a safe supported alternative when available; exhaust bounded admissible search before terminal failure without weakening policy. Return a typed failure/abstention when the repair budget is exhausted.
9. Version contracts and test compatibility across producer/consumer versions. Reject unknown versions before execution; migrate through explicit deterministic adapters. Preserve rejection semantics through migration. Do not silently broaden an enum to make a failing generation pass.

Deliver the schema, field trust/meaning table, staged validator, malformed/refusal examples, bounded recovery policy and migration tests. Verify valid-but-unauthorized, contradictory variants, unsupported evidence, duplicate keys, unknown version and missing critical fields. Ordinary API contract skills still own transport serialization; this skill owns uncertainty and trust at the model boundary.

Check decision ↔ facts ↔ explanation ↔ evidence ↔ state before promotion. Examples: WAIT with an immediate date; installments not totaling the required amount; SUPPORTED with an explanation asserting contradiction; evidence ID absent from observations; transition skipping an allowed state. Encode decidable relations in code. For genuinely semantic support, use calibrated evidence-based review and mark unresolved meaning unsupported. evidence-provenance owns ledger/claim reconciliation.
