# Agent Engineering Skills

A framework-agnostic collection of 19 agent skills for designing, building, evaluating, and operating AI agents and model-powered workflows.

The core idea: **models handle uncertainty; deterministic code handles authority.** A model may propose an action, but trusted software validates it, authorizes it, and records the evidence. Every skill applies that boundary to one part of the system, and every skill says when *not* to use it, so agents load only the one that fits.

## Install

With the [skills CLI](https://skills.sh) (works with Claude Code, Codex, Cursor and other agents that read `SKILL.md`):

```bash
npx skills add Sathvikar01/Agent-engineering-skills
```

Install a single skill:

```bash
npx skills add Sathvikar01/Agent-engineering-skills --skill agent-evals
```

List the skills without installing:

```bash
npx skills add Sathvikar01/Agent-engineering-skills --list
```

## Skills

| Area | Skill | Use it to |
|---|---|---|
| Design | [agent-architecture](agent-architecture/SKILL.md) | Choose the simplest architecture that handles the task's real uncertainty — deterministic code, workflow, single agent, tools or multi-agent |
| | [agent-development-workflow](agent-development-workflow/SKILL.md) | Coordinate the full lifecycle of a substantial agent build, from uncertainty map to verified release |
| | [agent-orchestration](agent-orchestration/SKILL.md) | Decide who controls the next step; bound routing, handoffs, fan-out/fan-in and budgets |
| Contracts | [tool-design](tool-design/SKILL.md) | Design model-facing tools with strict schemas, errors, idempotency and side-effect semantics |
| | [structured-output-design](structured-output-design/SKILL.md) | Specify and validate model-produced JSON as a proposal, not trusted data |
| | [prompt-engineering](prompt-engineering/SKILL.md) | Write versioned production prompts with clear responsibilities and trust boundaries |
| Authority & safety | [deterministic-authority](deterministic-authority/SKILL.md) | Put executable admission and authorization between model proposals and side effects |
| | [human-in-the-loop](human-in-the-loop/SKILL.md) | Place proportional approval gates bound to the exact action |
| | [agent-guardrails](agent-guardrails/SKILL.md) | Compose layered runtime controls without confusing guidance with enforcement |
| | [agent-security](agent-security/SKILL.md) | Threat-model prompt injection, tool poisoning, exfiltration and confused-deputy paths |
| Data | [rag-engineering](rag-engineering/SKILL.md) | Build and measure retrieval-grounded generation stage by stage |
| | [evidence-provenance](evidence-provenance/SKILL.md) | Track source → decision → claim lineage; separate retrieved from actually used evidence |
| | [agent-state-and-memory](agent-state-and-memory/SKILL.md) | Design runtime state, checkpoints and memory without treating recall as truth |
| Operations | [agent-failure-recovery](agent-failure-recovery/SKILL.md) | Bound retries and recover safely from interrupted runs and unknown side effects |
| | [agent-observability](agent-observability/SKILL.md) | Instrument trajectories so any run can be reconstructed from events |
| | [agent-cost-and-latency](agent-cost-and-latency/SKILL.md) | Optimize cost and latency per *verified successful* outcome |
| Quality | [agent-evals](agent-evals/SKILL.md) | Define evaluation-first quality gates, gold sets and release decisions |
| | [agent-testing](agent-testing/SKILL.md) | Build a risk-based test pyramid and CI strategy for an agent runtime |
| | [tool-evals](tool-evals/SKILL.md) | Measure whether a model can discover, select and recover with your tools |

See [AGENT-ENGINEERING-SKILLS.md](AGENT-ENGINEERING-SKILLS.md) for each skill's triggers, non-triggers, relationships and the recommended end-to-end build flow.

## Companion skills

Skills mention each other by name as optional companions; none is a required dependency. Some also defer general engineering mechanics to widely used skills you may already have — for example `systematic-debugging`, `verification-before-completion`, `context-engineering`, `security-and-hardening`, `performance-optimization`, `source-driven-development` and `mcp-builder`. They are not part of this collection; each skill still works without them.

## Evaluation

Each skill ships behavioral cases (`evals/evals.json`) and 20 balanced trigger queries (`evals/trigger-evals.json`).

- **Behavioral:** 68 paired runs over the 16 new or revised skills. Revised skills met 116/116 graded assertions versus 111/116 for their baselines; 4 skills improved and 12 tied. Each case ran once and graders were not blinded, so this is smoke evidence, not a measure of reliability.
- **Triggering:** a catalogue-selection proxy chose the right skill in 379/380 queries. Real automatic activation inside an agent harness was not measured.

[VALIDATION-REPORT.md](VALIDATION-REPORT.md) records every preserved failure and open limitation. [`evaluation/`](evaluation/README.md) holds the full run archive.

## License

[MIT](LICENSE)
