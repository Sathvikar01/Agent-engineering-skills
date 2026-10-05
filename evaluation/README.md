# Evaluation evidence

Each skill directory contains its behavioral cases in `evals/evals.json` and positive/negative trigger cases in `evals/trigger-evals.json`. The collection-level findings and preserved failed assertions are in the repository-root `VALIDATION-REPORT.md`.

The complete evaluation archive, `evaluation-evidence-v2.zip` (1,194 entries, 13.6 MB uncompressed), is published as a [GitHub Release asset](https://github.com/Sathvikar01/Agent-engineering-skills/releases/tag/evidence-v2) so it does not inflate the repository. [`MANIFEST.json`](MANIFEST.json) records its download URL, size and SHA-256; verify a download with `sha256sum evaluation-evidence-v2.zip`. It preserves run transcripts, grader outputs, generated test programs, command logs, revision history, routing queries and results, integrity audits, and the 35 HTML behavior/trigger review pages. It also retains the v1 snapshot and earlier iterations so the comparison history remains inspectable. The official review-page license and attribution files are inside the archive.

The selected behavioral comparison ran 68 paired cases across 16 modified or new skills. The revised outputs met 116/116 graded assertions, compared with 111/116 for the baselines; four skills improved their observed score and twelve tied. The separate trigger-selection proxy scored 379/380 across 380 balanced queries and 35 candidate skill descriptions. These are bounded evaluation results, not estimates of production reliability or automatic skill activation.

The archive preserves failed and superseded runs alongside corrected iterations. See `VALIDATION-REPORT.md` for the exact failures, scope of each rerun, and unresolved limitations. Actual automatic invocation and official description optimization could not be measured in this environment; repeated-run variance and human review also remain outstanding.

The archive records the work and includes individual test artifacts where generated. It is not a single-command, provider-independent replay harness: some checks depend on the original evaluation runner, model access, or the fixture context described in their run records.

[`v2.1/`](v2.1/README.md) holds the paired, blinded smoke run of the seven cases added in revision 2.1.0, with every answer, grade and the ID-to-version map.
