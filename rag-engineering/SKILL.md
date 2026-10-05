---
name: rag-engineering
description: >-
  Design, diagnose and evaluate retrieval-grounded generation with evidence provenance. Use when building or improving document-backed AI answers, measuring retrieval quality, investigating unsupported citations, or deciding whether chunking, hybrid search, reranking or query transformation helps. Do not use for ordinary database search without generation, general browsing, or memory persistence design without a retrieval-quality problem.
metadata:
  collection: "Agent Engineering"
  version: "2.0.0"
---

# RAG Engineering

Establish a labeled query/source set before stacking retrieval components. Diagnose whether evidence is absent, not retrieved, discarded during assembly, or misused during generation.

## Build the minimal pipeline

1. Define answerable/unanswerable queries, relevant source IDs/spans, freshness, tenant/permissions, citation requirements and latency/cost budgets. Version the corpus and index. Deduplicate documents and label source relevance without injecting gold answer keys or scoring annotations into the generation context; legitimate accessible evidence remains eligible.
2. Baseline query → candidate generation → metadata/access filtering → context assembly → grounded generation → citation/provenance verification. Enforce access before model-visible results, including caches/reranking. Choose sparse retrieval for exact identifiers/terms and dense retrieval for semantic similarity based on task evidence, not fashion.
3. Test chunk boundaries, size/overlap, document structure, metadata and embedding model/index consistency. Preserve parent document/span/version IDs; deduplicate overlapping chunks. More chunks are not more independent evidence.
4. Add query transformation, hybrid candidate fusion or reranking only after a specific failure analysis and matched ablation. Bound fan-out, candidate count and stage time. Preserve the user's constraints during rewriting; hallucinated rewrites can retrieve convincing irrelevant evidence.
5. Assemble context with bounded tokens, relevance, diversity, freshness and provenance. Preserve citation anchors and essential neighboring text. Mark truncation and conflicts. Retrieved text remains untrusted data; it cannot alter tool policy or instructions.
6. Generate claims only from sufficient evidence, distinguish quoted facts from inference, cite supporting sources and abstain when unsupported/conflicting beyond the task's tolerance. Verify that a citation supports its associated claim and belongs to the accessible source/version, not merely that its URL exists.

## Evaluate each stage

7. Measure Recall@K over labeled relevant documents/spans; use MRR for first relevant rank and nDCG for graded/ranked relevance when useful. Define relevance granularity, K and treatment of unanswerable queries before computing. Deduplicate document identities for document-level scores. Read [retrieval scoring](references/retrieval-scoring.md) for worked metrics and error attribution.
8. Evaluate context evidence retention and final correctness, groundedness, citation precision/support, abstention and hallucinations separately. Compare generation using oracle evidence with actual retrieval to separate retrieval from generation errors. Include poisoned sources and access-boundary cases.
9. Freeze splits by source/time/entity where leakage is plausible, repeat stochastic generation, and compare sparse, dense, hybrid, reranker and rewrite variants one at a time. Keep a component only if quality gains exceed noise and operational/complexity costs. Tune on development queries, then evaluate once on held-out sources/tasks.

Deliver a pipeline/data contract, query gold set, stage metrics, error taxonomy, provenance/citation example and ablation decision. Do not assume a vector database, framework, reranker or multi-agent retriever is required. source-driven-development owns checking engineering docs; this skill owns an application's evidence pipeline.

## Hand evidence to the decision path

Track retrieved candidates, context-visible spans and actual decision/claim support separately. Retrieval relevance does not prove support for an emitted answer. Carry source/span/version and transformation lineage into an application-owned ledger; proposed used IDs require reconciliation against observed accessible evidence and actual claim support. Cite used support, not every candidate. Hand this contract to evidence-provenance; retain retrieval metrics/pipeline ablations here. Reconcile structured facts, explanation and citations before returning grounded answers.
