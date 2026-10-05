---
name: evidence-provenance
description: >-
  Design and verify source-to-decision-to-output evidence lineage for AI systems. Use when implementing evidence ledgers, distinguishing retrieved from used support, reconciling decision/explanation/citation IDs, or preventing fabricated, stale or spoofed provenance across tools and model stages. Do not use for retrieval ranking/chunking alone, ordinary bibliography formatting, general logging, coding-source lookup, or answers with no evidence-lineage contract.
metadata:
  author: Sathvik
  collection: "Sathvik — Agent Engineering"
  version: "2.1.0"
---

# Evidence Provenance

Provenance is an application-owned record of observed sources/transformations, not citations appended after generation. Known IDs are necessary but do not prove support.

## Establish observed evidence

1. Define evidence for the task: accessible source/span/version, typed observation, deterministic computation or committed receipt. Assign IDs through trusted ingestion; source text/model output cannot mint authoritative entries. Record tenant/access scope, origin/time/version, digest, retrieval/tool/run ID and status. Bound retention/payloads under privacy policy.
2. Preserve source → retrieval → normalization → ledger lineage. Record transformation input/output IDs, versions and digest/span mappings. Summaries are derived claims with parent support, not replacements for source identity. Recheck consequential facts against fresh authoritative state; history does not prove current validity.
3. Distinguish retrieved candidates, model-visible context, used support and rejected/conflicting evidence. Record discarded/truncated status. A model’s used-ID list is a proposal; verify visibility and claim support without collecting private reasoning. Ledger membership alone cannot establish genuine use or entailment.

## Bind decisions and claims

4. Bind structured facts/decisions to observed evidence or computation inputs/rule/version. Bind emitted claims to supporting decisions/facts/source spans; label inference, uncertainty and gaps. Preserve contradictory sources rather than deleting inconvenient evidence.
5. Reconcile contradictions explicitly before deciding. Detect evidence that disagrees about the same fact (value, date, status, identity) and resolve it only by a declared, versioned rule—for example authoritative source over derived summary, or newer version over stale where the domain permits. Record the rule and both sources. If no rule resolves it, mark the fact contested and abstain, return a typed conflict status, or escalate; never silently pick the convenient source or let the model choose without a recorded basis.
6. Reconcile before emission: decision ↔ facts ↔ explanation ↔ ledger ↔ cited IDs. Enforce emitted IDs ⊆ accessible ledger AND supported used IDs for the relevant claim. Reject guessed IDs, unrelated known IDs, cross-tenant/stale versions and unobserved citations. Do not append provenance to conceal an unsupported decision.
7. Encode decidable checks in code: ID existence/scope/version, source visibility, transform ancestry, arithmetic and cross-field relations. For semantic entailment/support use evidence-based review or calibrated grader when needed; an ID whitelist is insufficient. A hash does not prove truth. Explanation cannot invent facts absent from the admitted structured path.

## Recover without laundering evidence

8. When support is missing, retrieve/construct a supported candidate or revise/remove the claim within finite budgets, then reconcile under unchanged rules. If none can be established, return explicit unsupported/insufficient-evidence status or fail the required output gate. Critical unsupported decisions fail closed; never fabricate entries or hide uncertainty behind citations.
9. Carry pointers through tools, compaction, checkpoints and resume. Recheck access/freshness at use; historical IDs may be unauthorized now. Log IDs and validation safely for reconstruction without duplicating sensitive content everywhere.

Deliver ledger/lineage contract, claim-support mapping, reconciliation validator/checker, supported/rejected examples and tests. Read [ledger example](references/ledger-and-reconciliation.md) when implementing records. Verify unknown IDs, retrieved-but-unused/irrelevant citations, spoofed envelopes, lost transform parents, contradictory explanation, conflicting sources resolved by rule versus left contested, revoked access and valid support.

RAG owns retrieval/ranking; this skill owns lineage/reconciliation across evidence-producing stages. Observability records decisions, structured-output-design owns proposal shape/semantics, deterministic-authority owns effect admission. No mandatory dependency chain.
