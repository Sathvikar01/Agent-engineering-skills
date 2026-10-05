---
name: agent-state-and-memory
description: >-
  Design agent runtime state, checkpoints and memory without confusing recall with authoritative facts. Use when deciding what an AI system should persist, handling long-running context, cross-run memory, checkpoint/resume, provenance, expiry or deterministic state transitions. Do not use for coding-session context setup, a normal database migration, or conversational summarization with no runtime persistence design.
metadata:
  collection: "Agent Engineering"
  version: "1.0.1"
---

# Agent State and Memory

Start with a storage ownership table. Do not call every persisted string memory or let a remembered claim update critical application state.

## Assign each datum a role

| Kind | Purpose | Authority |
|---|---|---|
| Conversation context | Messages/evidence visible to the current model call | Input data; may be incomplete or malicious |
| Working memory | Temporary plan, scratch observations and intermediate proposals | Run-local, advisory |
| Persisted state | Typed runtime status, cursors, budgets, pending actions and receipts | Application-owned transitions |
| Episodic memory | Prior event/outcome summaries with evidence | Historical recall; verify consequential facts |
| Semantic memory | Searchable learned facts or document knowledge | Provenance-bound; not automatic truth |
| User preferences | Consented presentation/interaction defaults | Preferences cannot grant permissions |
| Authoritative application state | Current balances, entitlements and committed records | Trusted source for critical decisions |

## Design lifecycle and reads

1. Specify owner, tenant/user scope, provenance, source timestamp/version, sensitivity, expiry and deletion path for each persistent field. Persist only what supports a concrete task or resume requirement. Exclude credentials, unnecessary personal data, raw private reasoning and unverified model claims of success.
2. Treat memory writes as proposals requiring validation, consent/policy where applicable, deduplication and provenance. Distinguish asserted facts from verified outcomes. Preserve conflicting sources and status rather than silently overwriting a newer authoritative fact with an older summary.
3. Retrieve with tenant/permission filters before exposing candidates; rank by task relevance and freshness within a bounded context budget. Expire or revalidate consequential facts. Protect memory from cross-user contamination, indirect injection and poisoned preference writes. Revoked access also revokes retrieval/cache access.
4. Compact conversation into claims plus source pointers, unresolved questions, remaining budgets and pending action IDs. Preserve provenance and uncertainty. A summary is lossy; re-fetch critical evidence before execution. Do not keep obsolete approval text as an authorization grant.

## Make progress durable

5. Define typed run states and deterministic allowed transitions. Accept transition events only with expected version, authorized actor and required evidence; use compare-and-set or transaction semantics for concurrent writers. Append immutable receipts and record partial completion rather than asking the model to rewrite status prose.
6. Checkpoint at durable operation boundaries: run/task ID, completed effects and idempotency keys, pending/unknown outcomes, remaining budget, state/policy/prompt versions and evidence pointers. Avoid snapshotting an in-flight action as completed. Choose recovery behavior for a crash before versus after commit.
7. Resume by validating checkpoint version, identity, access, expiry and unresolved effects against trusted stores. Reconcile ambiguous commits before repeating them. Reauthorize pending actions and preserve cumulative budgets across restarts; a restart must not reset limits.

Deliver the ownership/lifecycle table, transition contract, checkpoint example, compaction/read policy and isolation/deletion tests. Verify a stale success memory against current failure, simultaneous writers, expired preference, cross-tenant retrieval and restart after unknown commit.

Developer-session context packing and handoff are out of scope (a context-engineering skill may cover them). This skill owns the product runtime's persistence and source-of-truth boundary; agent-failure-recovery owns its recovery policy.
