# AgentKit — research-backed agent capability and near-unlimited tool candidates

Status: literature and public-project survey completed for the first pass on 2026-10-21. This is a sourced candidate catalog, not a claim that packages are installed, secure in this environment, or benchmarked against this project. Recheck project health, license, version and hardware fit before adoption.

## Executive finding

The most defensible practical gains come from letting an agent **observe a real environment, use a tool to act, receive objective feedback, and verify or repair the result**. That changes a task from generating a plausible answer into producing an artifact that passes a check.

Evidence-derived priority:
1. **Execution + real environment feedback:** shell/test runner, Python interpreter, browser automation, repository navigation and external data sources.
2. **Objective verification:** tests, assertions, type checks, linters, validators and postcondition checks with persisted evidence.
3. **Task-relevant retrieval:** search the actual repository and trusted local documentation instead of relying only on model weights or a huge prompt.
4. **Adaptive inference-time search:** try another candidate or planning path when the first attempt fails; select with a verifier rather than ungrounded “confidence.”
5. **Durable state and recovery:** checkpoints, diffs, test evidence and a record of what may already have happened before retrying.
6. **Multiple agents only where work is meaningfully independent:** do not add debating agents by default.

This order is a decision synthesized across papers, not a universal ranking for every task. “More tools” or “more agents” alone has not been shown to create general intelligence.

## Evidence interpretation

- Paper results describe a particular experiment, model, dataset and baseline, not a guarantee for another setup.
- **Near-unlimited** means running locally or on a self-managed server without per-token hosted-model fees. It remains bounded by hardware, electricity, speed, context, RAM/VRAM, model license and time. There is no literally unlimited free compute.
- An open-source agent framework does not remove hosted-model fees or provider rate limits unless it is configured to use local inference.
- A reported paper gain does not prove the corresponding tool will improve this project; candidate integrations must be compared on fixed representative tasks.

## Research evidence: what improves performance, and where it stops generalizing

### A. Tool use and real environment feedback — highest priority

| Research | Reported finding | Practical conclusion | Limit |
|---|---|---|---|
| **PAL: Program-aided Language Models** (2022), https://arxiv.org/abs/2211.10435 | The model generates a program and delegates arithmetic/symbolic execution to an interpreter. On GSM8K, the paper reports Codex + PAL outperforming PaLM-540B with chain-of-thought by **15 percentage points**. | For calculations, data transforms and algorithmic work, generate code then execute it instead of trusting internally generated arithmetic. | The problem must be correctly translated into a program; code can encode a wrong interpretation. |
| **ReAct: Synergizing Reasoning and Acting in Language Models** (ICLR 2023), https://arxiv.org/abs/2210.03629 | Interleaving reasoning, actions and observations improved results in the paper's QA/fact-verification and interactive benchmarks; reported absolute success-rate advantages were **34 points on ALFWorld** and **10 points on WebShop** against their respective comparison methods. | Give the agent narrowly described tools and feed their output into its next decision: search, inspect, act, observe, correct. | Numbers are benchmark- and baseline-specific; tool quality and available observations matter. |
| **SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering** (2024), https://arxiv.org/abs/2405.15793 | Shows that interface design affects agent effectiveness; its purpose-built agent-computer interface reported pass@1 of **12.5% on SWE-bench** and **87.7% on HumanEvalFix** in the evaluated setup. | Tool ergonomics matter: repository-aware navigation, bounded edits and simple test execution can outperform an unstructured shell/prompt interface. | Historical results are not a current leaderboard estimate and do not isolate every design factor. |

**Decision:** make the execution/observation/verification loop the core AgentKit pattern. Prefer task-specific commands with structured results over a large list of vague tools.

### B. Objective verification and tests — very high priority

**SWE-bench** tests whether an agent can resolve real GitHub issues and whether patches satisfy test requirements: https://arxiv.org/abs/2310.06770. It illustrates the gap between generating code and solving a repository issue. OpenAI's 2026 assessment says SWE-bench Verified is increasingly contaminated for measuring frontier coding ability and recommends SWE-bench Pro: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/.

**Decision:** every success receipt should report actual test/validator output, exit status, environment version and artifact paths. A model claiming success is not acceptance evidence. Prefer private/project-specific regression tasks when validating this repository.

Candidate verification tools:
- Existing project runners: pytest, language-native test runners, builds/type checks and schema validators.
- **Hypothesis** for property-based testing and generated edge cases: https://hypothesis.readthedocs.io/en/latest/.
- **Inspect AI** for reproducible model/agent evaluations, tool use, sandboxing and scored tasks; it advertises over 200 available evaluations: https://inspect.aisi.org.uk/ and https://github.com/UKGovernmentBEIS/inspect_ai.
- **Promptfoo** for local/CI prompt, agent and RAG evaluations and security red-teaming: https://github.com/promptfoo/promptfoo. Hosted model providers may still require API credentials and incur fees.

Start with deterministic tests. Add model-graded scoring only for criteria that cannot be checked objectively.

### C. Diverse candidates and extra inference-time compute — high but conditional priority

| Research | Reported finding | Practical conclusion | Limit |
|---|---|---|---|
| **Self-Consistency Improves Chain of Thought Reasoning** (ICLR 2023), https://arxiv.org/abs/2203.11171 | Sampling diverse reasoning paths and selecting the most consistent answer improved reported results, including GSM8K (+17.9%), SVAMP (+11.0%), AQuA (+12.2%), StrategyQA (+6.4%) and ARC-challenge (+3.9%). | For hard questions, generate a few independent candidates and use agreement or an objective checker. Escalate only if a cheap first attempt fails. | Extra samples consume compute; correlated errors can survive majority voting. |
| **Tree of Thoughts** (2023), https://arxiv.org/abs/2305.10601 | In the narrow Game of 24 experiment, GPT-4 with chain-of-thought solved 4% while the Tree-of-Thoughts search setup solved 74%. | Search/backtracking can be valuable for problems with explicit intermediate states and a useful evaluator. | This is not a universal 18.5× gain. It is task-specific and requires more model calls plus a useful state evaluator. |
| **Revisiting Test-Time Scaling** survey (2025), https://arxiv.org/abs/2506.04611 | Surveys sampling-based, search-based and trajectory-optimization methods that trade additional inference compute for reasoning performance; diversity affects whether extra samples help. | Use a bounded ladder: single attempt → test/critique → limited alternate candidates → verify. | Additional compute does not automatically help; a weak evaluator can select a bad answer. |

**Decision:** use bounded adaptive retries/search rather than always “thinking longer” or always sampling many answers. Track calls, runtime, tokens where available, and pass rate.

### D. Retrieval and external memory — high priority for repository/document tasks

**Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** (2020), https://arxiv.org/abs/2005.11401, reports strong results on three open-domain QA tasks and more specific, diverse and factual language than a parametric-only baseline in its experiments.

**Decision:** retrieve current project files, docs, source references and test evidence when the task depends on them. Start with exact search and repository maps because they are low-cost and inspectable. Add a local vector index only when retrieval evaluation shows that exact search is insufficient. Retrieval helps access relevant knowledge; it does not automatically improve planning or make retrieved text trustworthy.

Candidates:
- **Aider repository map** as a codebase-context pattern: https://github.com/Aider-AI/aider.
- **Chroma** for a local vector store when semantic retrieval is justified: https://github.com/chroma-core/chroma.
- **Microsoft GraphRAG** for graph-based retrieval across large unstructured corpora, but the project currently describes itself as largely in maintenance mode. Treat it as a specialist experiment, not the default dependency: https://github.com/microsoft/graphrag.
- Versioned Markdown/JSON checkpoints and source-linked notes are the simplest persistent memory. Prefer them before deploying a memory service without a measured need.

### E. Self-reflection and iterative refinement — conditional priority

**Self-Refine: Iterative Refinement with Self-Feedback** (NeurIPS 2023), https://arxiv.org/abs/2303.17651, reports approximately **20% absolute average task-performance improvement** across seven evaluated tasks against one-shot generation in its setup.

However, **When Hindsight Is Not 20/20** (Findings of NAACL 2024), https://aclanthology.org/2024.findings-naacl.237/, found that reflection without external feedback helped TruthfulQA but hurt HotpotQA in its study. The effect depended on initial answer reliability and task difficulty.

**Decision:** reflection should inspect concrete evidence—test failures, diffs, source excerpts, counterexamples and acceptance criteria—not merely ask a model to reconsider its unsupported answer. Self-critique is not proof.

### F. Multi-agent debate/coordination — selective, not a default multiplier

**Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs** (ICML 2024), https://proceedings.mlr.press/v235/smit24a.html, found that multi-agent debate did **not reliably outperform** self-consistency or ensembling in its comparisons and was sensitive to tuning.

The 2026 Nature Machine Intelligence study **Capable language models can outgrow the benefits of collaboration**, https://www.nature.com/articles/s42256-026-01268-y, reports controlled comparisons across 260 configurations, six benchmarks, five coordination architectures and three LLM families. Its key conclusion is that baseline single-agent capability strongly predicts whether collaboration helps; adding agents can be neutral or harmful past a capability threshold.

**Decision:** add agents where tasks split into independent branches (for example, one researches sources while another audits code), or where a genuinely distinct reviewer is available. Do not make repeated debate the default for tightly coupled sequential work. Record exact model/provider identities and verify findings against evidence.

## Candidate catalog: open-source and self-hosted options

These are candidates for evaluation, not mandatory dependencies. Prefer one tool per capability slot instead of installing every framework. Self-hosted applications still need a capable model; hosted-model use may reintroduce fees, quotas and provider terms.

| Layer | Candidate(s) | Near-unlimited profile | Best fit | Priority |
|---|---|---|---|---|
| Local inference | **Ollama**, https://github.com/ollama/ollama | A: local model serving without per-token hosted API charges; limited by device speed, memory, model license and power. | Easiest local serving path and integration with compatible endpoints. | P0 |
| Local inference | **llama.cpp**, https://github.com/ggml-org/llama.cpp | A: local quantized inference with CPU/GPU and multiple accelerator backends; still hardware-limited. | Low-VRAM/CPU-heavy devices, GGUF models and portable inference. | P0 |
| Local model server | **vLLM**, https://github.com/vllm-project/vllm | A on a self-managed GPU server; more operationally complex and not intended as the first pick for small devices. | High-throughput batching and shared GPU model serving. | P1, hardware-dependent |
| Coding agent | **Aider**, https://github.com/Aider-AI/aider | A with compatible local inference; B if a hosted model API is used. | Terminal edits, many languages, repository maps and reviewable changes. | P0 candidate |
| Coding agent | **SWE-agent**, https://github.com/SWE-agent/SWE-agent | A with a working local compatible model; B with hosted providers. | Repository issue-solving, specialized agent-computer interface and trajectories. | P0 candidate |
| Coding agent/workspaces | **OpenHands Software Agent SDK**, https://github.com/OpenHands/software-agent-sdk | A with local inference and local/ephemeral sandbox; B/C with hosted backends. | Longer multi-tool code tasks, isolated workspaces and extensible agent construction. | P1 candidate |
| Coding agent/IDE | **Cline**, https://github.com/cline/cline | A with a local model endpoint such as Ollama/LM Studio; otherwise model-dependent. | Human-visible approval flow, editor/terminal work and MCP integration. | P1 candidate |
| Browser execution | **Playwright MCP**, https://github.com/microsoft/playwright-mcp | Local/open-source automation layer; model can be local. Website logins, limits and real-world side effects remain external. | Page navigation, accessibility snapshots, forms, network/storage, screenshots/traces. | P0 |
| Browser agent | **Browser Use**, https://github.com/browser-use/browser-use | A with local library + local LLM + local browser. Cloud browser/API features may have fees or limits. | High-level browser planning when raw Playwright actions are insufficient. | P1 |
| Evaluation framework | **Inspect AI**, https://github.com/UKGovernmentBEIS/inspect_ai | A for local evaluations; scoring model can be local or hosted. | Agent benchmarks, tool use, sandboxing and repeatable scored tasks. | P0/P1 |
| Evaluation/red-team CLI | **Promptfoo**, https://github.com/promptfoo/promptfoo | A for local deterministic/local-model tests; B if hosted model APIs are used. | Prompt/agent/RAG regression matrix, security tests and CI reports. | P1 |
| Property-based tests | **Hypothesis**, https://hypothesis.readthedocs.io/en/latest/ | A: local test library, no model API needed. | Generated edge cases and invariant checks. | P0 for Python |
| Semantic retrieval | **Chroma**, https://github.com/chroma-core/chroma | A as a local index; embedding-model compute is still required. | Semantic search over a large local corpus after exact-search limitations are measured. | P2 |
| Complex-corpus retrieval | **GraphRAG**, https://github.com/microsoft/graphrag | Can be self-hosted, but indexing can require substantial compute and an LLM; maintenance-mode caveat applies. | Specialist graph-based retrieval experiment, not the default first step. | P3 |
| Durable memory | Versioned Markdown/JSON records, checkpoints, Git diffs and test manifests | A: local files/Git, with no hosted model request needed to persist state. | Resume after interruption, audit decisions and retain acceptance evidence. | P0 |
| Deterministic repository navigation | Existing search/index tools, compiler/type checker and native test runners | A: local commands; most checks need no model usage. | Find definitions/usages, test changes and validate generated artifacts. | P0 |

### Recommended near-unlimited combinations

**Combination 1 — general local coding agent**
- Ollama for the simple local-serving path or llama.cpp for more quantization/runtime control.
- Aider or SWE-agent for focused code editing; evaluate OpenHands only if longer multi-tool work and sandbox lifecycle justify more setup.
- Native tests and Hypothesis where applicable; persist patch and test evidence.
- This removes per-token API billing only if inference actually stays local. It does not guarantee frontier-model-level quality.

**Combination 2 — browser and UI work**
- Playwright MCP + local model for browser state/actions, with Playwright Test for deterministic assertions.
- Add Browser Use only if high-level planning solves a demonstrated gap.
- Keep authenticated profiles isolated; require approval for submit/delete/purchase/post actions. Local browser control does not eliminate remote site limits or side effects.

**Combination 3 — project knowledge and long tasks**
- Start with exact local search and source-linked Markdown/JSON checkpoints.
- Add Chroma or another local vector index only after evaluating retrieval recall on representative questions.
- Link material claims to the exact retrieved source or test evidence.

**Combination 4 — measured quality improvement**
- Inspect AI or a small deterministic harness runs a fixed regression set.
- Use a small, bounded number of alternate attempts after objective failure; select using tests/validators rather than self-confidence.
- Add an independent reviewer only when the second model is genuinely different or the role has a distinct checklist. Reviewer output remains advisory.

## Deprioritize or avoid as default

- **Unbounded multi-agent debate:** expensive and not reliably better than single-agent sampling; reserve it for independent work or a distinct evidence-backed review.
- **Reflection without external feedback:** may repeat or entrench a bad answer; require tests, source excerpts, counterexamples or explicit criteria.
- **A giant MCP/tool catalog:** increases routing, context and security overhead without proving capability improvement. Prefer a small task-matched set with measurable outcomes.
- **Heavy GraphRAG/vector infrastructure before measuring baseline search:** start with exact search, project maps and source-linked files.
- **Automatic installation of every candidate:** packages can consume storage, change configuration, use network access or expose credentials. Probe first; install only when the environment policy allows it.
- **Using public SWE-bench Verified scores as current proof of coding skill:** OpenAI's 2026 assessment warns of contamination and recommends SWE-bench Pro for frontier coding evaluation.

## AgentKit integration plan

1. **Inventory without execution:** detect local model runtimes, user-configured endpoints (without reading or emitting secrets), browser binaries, Playwright/MCP config, test runners, Docker/Podman and available resource indicators.
2. **Select candidates:** recommend one agent frontend, one inference runtime, one browser/test path and project-native validators. Do not auto-install.
3. **Build safe adapter interfaces:** task-scoped shell, workspace-contained filesystem/patching, browser actions and bounded inference/search attempts.
4. **Emit an evidence packet:** task ID, acceptance checks, model/provider identity where known, runtime/tool version, command, exit status, bounded output, changed files, test IDs/results, artifact links and limitations.
5. **Recover adaptively:** after an objective failure, use bounded repair attempts; before retrying an operation with uncertain external side effects, re-observe state.
6. **Evaluate security/reliability:** fixed representative tasks, prompt-injection fixtures in pages/files, path traversal, command timeout, output flooding, stale auth, interrupted operations and retry/idempotency cases.
7. **Benchmark locally:** compare baseline and candidate on the same task set using comparable model/context/compute budgets; report pass rate, runtime, call count, failure class and reproducibility.

## Acceptance criteria

- Each research claim links to the paper/authoritative source and explains tested task/limits.
- No package is described as installed until an environment probe verifies it.
- Discovery never executes unknown tools or installs packages.
- Local/self-hosted, hosted API, free-tier and paid options are distinct.
- Model/provider identity, versions, test output and uncertainty are retained where available.
- The same evaluation tasks can be rerun to compare outcomes against a baseline.
- A candidate is promoted only when measured task outcomes improve without unacceptable safety, reliability, latency or cost regressions.

## Sources and review date

Literature reviewed 2026-10-21:
- PAL: https://arxiv.org/abs/2211.10435
- ReAct: https://arxiv.org/abs/2210.03629
- SWE-agent: https://arxiv.org/abs/2405.15793
- SWE-bench: https://arxiv.org/abs/2310.06770
- SWE-bench Verified: https://openai.com/index/introducing-swe-bench-verified/
- SWE-bench evaluation limitations: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- Self-Consistency: https://arxiv.org/abs/2203.11171
- Tree of Thoughts: https://arxiv.org/abs/2305.10601
- Test-Time Scaling survey: https://arxiv.org/abs/2506.04611
- RAG: https://arxiv.org/abs/2005.11401
- Self-Refine: https://arxiv.org/abs/2303.17651
- Reflection limits: https://aclanthology.org/2024.findings-naacl.237/
- Multi-agent debate: https://proceedings.mlr.press/v235/smit24a.html
- Collaboration limits: https://www.nature.com/articles/s42256-026-01268-y
- Playwright MCP: https://github.com/microsoft/playwright-mcp
- Browser Use: https://github.com/browser-use/browser-use
- OpenHands SDK: https://github.com/OpenHands/software-agent-sdk
- Aider: https://github.com/Aider-AI/aider
- SWE-agent: https://github.com/SWE-agent/SWE-agent
- Cline: https://github.com/cline/cline
- Ollama: https://github.com/ollama/ollama
- llama.cpp: https://github.com/ggml-org/llama.cpp
- vLLM: https://github.com/vllm-project/vllm
- Inspect AI: https://github.com/UKGovernmentBEIS/inspect_ai
- Promptfoo: https://github.com/promptfoo/promptfoo
- Hypothesis: https://hypothesis.readthedocs.io/en/latest/
- Chroma: https://github.com/chroma-core/chroma
- GraphRAG: https://github.com/microsoft/graphrag

Research catalog only. Runtime availability, local-model quality, hardware fit, security review and task-level gains remain UNKNOWN until tested.
