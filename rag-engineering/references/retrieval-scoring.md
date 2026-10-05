# Retrieval metrics and error attribution

Choose document or span relevance and deduplication order first. With gold documents {A,C}, raw ranking B,A,A,C and raw K=3, unique relevant hits in the top three are {A}: Recall@3=1/2. If you deduplicate before applying K, the ranking is B,A,C and Recall@3=2/2. Both conventions can be valid when explicitly stated; compare variants under the same convention. Reciprocal rank of the first relevant result is 1/2 in either ranking. Average reciprocal ranks across answerable queries to obtain MRR.

For graded relevance, DCG@K = sum((2^relevance_i - 1)/log2(i+1)) over ranks i starting at 1. nDCG divides by the ideal DCG for the same labels/K. When the ideal score is zero, define/report the handling policy rather than silently divide by zero. Evaluate unanswerable queries through abstention/false-positive retrieval, not an undefined recall denominator.

Use the stage matrix:

| Observation | First diagnosis |
|---|---|
| Required evidence absent from corpus | Coverage/source freshness |
| Evidence in corpus but absent from candidates | Retrieval/filter/chunking |
| Candidates contain evidence, assembled context does not | Reranking, deduplication or context budget |
| Context contains evidence, answer wrong/unsupported | Generation/instruction/grounding |
| Answer right but citations point elsewhere | Attribution/claim support |
| Inaccessible source exposed | Security/access boundary regardless of correctness |

Compare actual context with oracle evidence for the same query; an oracle gain indicates a retrieval/assembly contribution, not proof that generation is flawless. Check citations claim by claim against accessible source span/version. Poisoned source instructions remain untrusted data even when the legitimate factual content is relevant.

Ablate one component at a time: sparse, dense, hybrid, reranker, query rewrite, chunk strategy. Freeze corpus/index/query split and stage budgets, report metric denominators, p95 latency and cost. Keep extra components only for measured benefit on held-out cases. Do not inject held-out answer keys or scoring annotations into retrieval fixtures during tuning; ordinary authorized source documents may contain the required answer.
