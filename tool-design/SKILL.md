---
name: tool-design
description: >-
  Design model-facing tools with coherent capabilities, strict contracts and predictable side effects. Use when exposing APIs or operations to an LLM agent, redesigning ambiguous agent tools, or specifying tool names, descriptions, arguments, results and execution semantics. Do not use for ordinary REST design with no model consumer, MCP transport implementation alone, or evaluating tool selection without changing contracts.
metadata:
  author: Sathvik
  collection: "Sathvik — Agent Engineering"
  version: "2.0.0"
---

# Tool Design

Design the smallest coherent capability surface for the agent's tasks. Existing API/interface skills own backend API mechanics; MCP builder owns protocol, transports and SDK code. This skill adds the contract an LLM must select and use correctly.

## Derive the surface from tasks

1. List representative user intents, required observations and permitted mutations. Map each intent to a short call sequence. Remove tools that provide authority the task does not need. Do not expose arbitrary SQL, shell or generic HTTP simply because the backend supports them.
2. Group operations by a stable goal and permission boundary. Prefer a few coherent tools over an omnibus action/args bag or dozens of tiny field setters. Separate read, preview and commit where risk or authorization differs; do not force a preview for harmless reads.
3. Name tools with explicit action and resource. Describe what they do, when to choose them, explicit USE WHEN and DO NOT USE WHEN choices, preconditions, postconditions, effects and return semantics. Disambiguate overlapping tools using one concrete choice example. Tool metadata describes capabilities; it does not authorize calls.

## Make misuse detectable

4. Specify strict input and output schemas: types, enums, required fields, bounds, units, identifier formats and version. Reject unexpected fields where supported. Define missing versus null. Trusted identity, tenant, permissions and server-derived fields come from execution context, not model-supplied claims.
5. Return bounded structured results with stable identifiers, provenance/version, explicit empty/truncated status, and opaque pagination cursors. Bound page size and result bytes; document stable ordering and stale cursor behavior. Put verbose evidence behind a bounded follow-up capability rather than silently clipping an essential fact.
6. Return machine-readable errors with code, safe message, retryability and relevant field/conflict details. Distinguish validation, authorization, not-found, version-conflict, rate-limit, transient failure and unknown commit outcome. A retryable hint is advisory; the caller still enforces a finite retry budget. Never expose credentials or internal stack traces in normal results.
7. State side effects and their visibility, cancellation behavior and concurrency semantics. For mutations, bind an idempotency key to principal, operation and canonical request hash; persist result/reconciliation status and reject key reuse with different arguments. Specify deduplication retention and optimistic state version checks. Do not promise exactly-once execution without an actual transactional mechanism.
8. Apply least privilege, deterministic semantic validation and authorization immediately before execution. Cap deadlines, input size and downstream fan-out. A tool result can be untrusted text even when the transport is authenticated.

## Deliver and verify

Deliver a capability map, names/descriptions, input/output/error schemas, side-effect/idempotency rules, and representative request/response plus success/denial/unknown-outcome exchanges for each important capability. Include purpose, permissions, pre/postconditions and which neighboring tool to choose instead. Walk through an ambiguous intent, invalid argument, page boundary, denied mutation and lost mutation response.

Use structured-output-design for model-produced proposal validation and tool-evals for model usability. Do not add a large implementation scaffold before the contract shows the actual need.
