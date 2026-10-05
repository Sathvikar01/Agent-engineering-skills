# Cost per outcome

Variant A: total spend 20, verified successes 80/100 → 0.25 per successful task. Variant B: total spend 12, successes 40/100 → 0.30 per success. B's smaller bill is not better outcome economics and its lower success rate may violate quality requirements. Include all failures, retries, escalation, worker overhead and relevant cache costs in total spend. Zero successes makes this ratio undefined.

Track safe abstentions and task mix separately so a system cannot make its metric look better by refusing hard tasks or redefining eligibility after measurement. Include denominators and predefined quality/safety floors. Report user-facing p95 completion latency and interactive first-response latency separately when they differ materially.

For a routing experiment, compare direct larger-model execution to smaller→larger fallback using actual route frequency, quality and total spend. A confidence score alone is not a calibrated escalation policy. Freeze the route definition and test difficult cases and provider errors.

For caching, include tenant/principal access, canonical input, model/prompt/schema/tool/index versions and freshness in the key. A permission revocation must prevent a previously cached disclosure. Do not cache approval as authority. Distinguish warm and cold measurements and provider cache creation/read charges.

Measure the critical path before parallelizing. Independent reads may overlap; dependent mutations still require ordered admission/version checks. Atomic aggregate budget reservation prevents each worker consuming the entire nominal run cap. Resume preserves expenditure and remaining ceilings.
