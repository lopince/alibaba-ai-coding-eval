# Alibaba AI Coding Evaluation

A comprehensive evaluation framework for Alibaba's AI coding ecosystem, benchmarking models, tools, and agent harnesses against the frontier landscape.

---

## 1. AliCloud AI Product Overview

### 1.1 LLM Provider — Model Studio (Bailian)

Alibaba Cloud's central AI platform is **Model Studio (百炼/Bailian)**, hosting 300+ models via an OpenAI-compatible API through DashScope.

| Category | Key Models | Context | Notes |
|---|---|---|---|
| **Qwen3.7-Max** | Proprietary flagship | 128K+ | 80.4% SWE-bench Verified, 60.6% SWE-bench Pro |
| **Qwen3.6** | Open-weight latest gen | 128K+ | Stability + real-world utility focus |
| **Qwen3.5** | 27B, 35B-A3B, 0.8B–9B | 262K (~1M expandable) | Native vision (early fusion), MCP support, 201 languages |
| **Qwen3** | 0.6B–235B (dense + MoE) | 32K–128K | Hybrid thinking, 119 languages, Apache 2.0 |
| **Qwen3-Coder** | 480B (flagship), 80B-Next (3B active) | 128K+ | Code-specialized; 480B matches Claude Sonnet 4 on agentic benchmarks |
| **Qwen3-VL** | 2B–235B-A22B | 256K (1M expandable) | Vision-language; images, video, GUI screenshots, OCR |
| **Qwen3-Omni** | 30B-A3B | 128K+ | Full multimodal: text + vision + audio in/out; "Thinker-Talker" architecture |

**API Pricing (DashScope):**
| Tier | Input / 1M tokens | Output / 1M tokens |
|---|---|---|
| Qwen3.5-Flash | ~$0.03 | ~$0.06 |
| Qwen3-Coder (Coding Plan) | ~$0.05 | ~$0.10 |
| Qwen3.7-Max | ~$1.00 | ~$3.00 |

**Coding Plan**: ~$3–5/month subscription bundling multiple coding-optimized models with higher rate limits.

### 1.2 Agent Infrastructure

| Layer | Product | Description |
|---|---|---|
| **Open-source Framework** | Qwen-Agent | Lightweight agent orchestration SDK |
| **Enterprise Toolkit** | ADK (Agent Development Kit) / ADP (Agent Deployment Platform) | Enterprise agent build + deploy |
| **Cloud Runtime** | AgentBay | Sandboxed cloud execution environment for agents |
| **Platform Builders** | Model Studio Workflow / Agent / RAG Builders | No-code/low-code agent, workflow, and RAG pipeline builders inside Bailian |

### 1.3 AI Products Portfolio

| Product | Category | Description |
|---|---|---|
| **Tongyi Qianwen (Qwen)** | LLM | Foundation model family (see above) |
| **Tongyi Wanxiang** | Image Generation | Text-to-image / video generation |
| **Tongyi Lingma** | AI Coding | IDE plugin for VS Code / JetBrains; inline completion + chat |
| **Qwen Code** | Terminal Agent | Open-source terminal coding agent (comparable to Claude Code) |
| **PAI (Platform for AI)** | MLOps | Training, fine-tuning, deployment platform |
| **Model Studio (Bailian)** | AI Platform | Unified model marketplace, API gateway, agent builder |

### 1.4 Strategic Investment

- **RMB 380 billion (~$52B)** three-year AI infrastructure commitment
- Global expansion: Singapore, Germany, US East, and other regions
- All open-source models under **Apache 2.0** license

---

## 2. Qoder Product Overview

### 2.1 What is Qoder?

Qoder is an **agentic coding platform** (founded 2024, Alibaba ecosystem). It positions as an "Autonomous Development Desktop" — not just code completion, but a full platform integrating context engineering with intelligent agents.

### 2.2 Product Line

| Product | Description |
|---|---|
| **Qoder IDE (Desktop)** | Standalone autonomous development desktop (VS Code-based); Windows/macOS/Linux |
| **Qoder IDE Extension (VS Code)** | Plugin bringing Qoder's agentic features into VS Code |
| **Qoder IDE Extension (JetBrains)** | Plugin for IntelliJ, PyCharm, etc. |
| **Qoder CLI** | Terminal-based AI coding agent (direct competitor to Claude Code) |
| **Qoder CN** | Chinese-localized version at qoder.com.cn |

### 2.3 Key Feature Comparison: Qoder vs. Claude Series

| Dimension | **Qoder** | **Claude Code / Claude (Anthropic)** |
|---|---|---|
| **Model Support** | Multi-provider (GPT, Gemini, Qwen, Claude, etc.) with auto-routing | Claude models only (Opus 4.7, Sonnet 4.6, Haiku 4.5) |
| **Memory/Knowledge** | Built-in Knowledge Engine: Repo Wiki, Knowledge Cards, Conversation Memory | CLAUDE.md files (user/project/local), Auto-Memory, modular rules |
| **Skills/Extensions** | Skills system + MCP + Plugin marketplace | Skills + MCP + custom slash commands |
| **Multi-Agent** | Experts Mode: structured DAG-based orchestration with 5 specialized expert roles | Agent Teams: peer-to-peer collaboration, shared registry, dependency resolution |
| **IDE** | Full standalone IDE + VS Code + JetBrains extensions | VS Code + JetBrains extensions only (no standalone IDE) |
| **Autonomous Delegation** | Quest Mode: dedicated workspace for long-running agent tasks with kanban boards | Headless mode, GitHub Actions integration, remote sessions |
| **Context Window** | Not publicly disclosed | 1M tokens |
| **Voice** | Not available | Supported |
| **Local/Offline Models** | Not supported | Supported |
| **Pricing** | Free tier; $20–$200/mo paid plans | $0–$200/mo (Claude Code included in Max $100–$200/mo) |

### 2.4 Qoder Experts Mode (Multi-Agent Deep Dive)

**Architecture:**
- **Experts Leader** (orchestrator): Breaks down requirements, assigns tasks, tracks progress, consolidates results. Does NOT implement code.
- **Expert Team** (subagents): Domain-specific agents with isolated toolsets. No peer-to-peer communication; all routing via Leader's centralized mailbox loop.
- **Task Graph**: Lightweight DAG supporting dependency-aware parallel scheduling.

**Built-in Expert Roles:**

| Expert | Function |
|---|---|
| Research Expert | Tech selection, root-cause analysis, impact/risk assessment |
| Coding Expert | Feature dev, bug fixes, refactoring, API/DB integration |
| QA (Verify) Expert | Regression testing, pre-commit gates, functional validation |
| Code Review Expert | PR/MR review, architecture/security/performance assessment |
| Browser Expert | Frontend UI/E2E testing, visual regression, cross-browser validation |

**Self-Evolution Loop**: `Complete -> Extract -> Store -> Recall -> Execute` — reusable skills are automatically extracted and persisted.

### 2.5 Claude Code Agent Teams (Comparison)

**Architecture:**
- One session as **team lead** coordinating work
- Multiple worker instances with **isolated memory**
- Workers communicate **directly with each other** (peer-to-peer, not just through manager)
- Shared registry with automatic dependency resolution

**Key Differences from Qoder Experts Mode:**
- Qoder uses centralized orchestration (Leader-only routing); Claude uses decentralized peer-to-peer
- Qoder has predefined expert roles; Claude uses generic workers with role profiles
- Qoder includes a dedicated knowledge engine; Claude relies on CLAUDE.md memory files

---

## 3. Qoder CLI Evaluation

### 3.1 Evaluation Scope

Head-to-head comparison of **Qoder CLI** vs. **Claude Code** across feature dimensions.

### 3.2 Feature Comparison Matrix

#### Core Features

| Feature | Qoder CLI | Claude Code | Eval Method |
|---|---|---|---|
| **Memory System** | Knowledge Engine (Repo Wiki + Knowledge Cards + Conversation Memory) | CLAUDE.md (user/project/local) + Auto-Memory + modular path-scoped rules | Test: multi-session memory persistence and recall accuracy |
| **Skills** | Extensible skills system + marketplace + MCP | Skills + MCP + custom slash commands | Test: create, install, invoke custom skills |
| **Knowledge Base** | Auto-generated repo wiki, knowledge cards, persistent conversation memory | File-based CLAUDE.md, auto-memory learned from interactions | Test: large repo knowledge extraction quality |
| **Tool Use** | MCP servers + built-in tools | MCP servers + built-in tools | Test: multi-tool orchestration scenarios |

#### Advanced / Agent Features

| Feature | Qoder CLI | Claude Code | Eval Method |
|---|---|---|---|
| **Subagents** | Expert Team (5 roles, isolated toolsets, Leader-routed) | Subagents (single-window, originator-only results) | Test: parallel subagent task completion |
| **Agent Teams** | Experts Mode with DAG scheduling | Peer-to-peer Agent Teams (experimental) | Test: multi-agent collaboration on complex feature |
| **Dynamic Workflows** | Quest Mode with kanban, progress tracking, artifact review | Headless mode + GitHub Actions + remote sessions | Test: end-to-end autonomous feature development |
| **Self-Evolution** | Automatic skill extraction and reuse loop | Auto-memory for pattern persistence | Test: repeated similar tasks — does performance improve? |
| **Model Routing** | Multi-provider auto-routing (GPT, Gemini, Qwen, Claude) | Single provider (Claude models only) | Test: task-specific model selection effectiveness |

### 3.3 Evaluation Tasks

| # | Task | Tests | Scoring |
|---|---|---|---|
| 1 | **Repo Onboarding**: Import a 50K+ LOC repo, ask architecture questions | Knowledge Engine, memory | Accuracy, completeness, time |
| 2 | **Bug Fix**: Fix a multi-file bug from issue description | Tool use, code editing, test running | Correctness, steps taken |
| 3 | **Feature Build**: Implement a feature from spec to PR | Autonomous delegation, workflow | PR quality, test pass rate, time |
| 4 | **Multi-Agent Task**: Complex feature requiring research + coding + testing + review | Agent teams, experts mode | Task decomposition quality, parallelism, final output |
| 5 | **Refactor**: Large-scale refactor across 20+ files | Context management, multi-file edits | Correctness, preservation of behavior |
| 6 | **Memory Persistence**: Work across 5 sessions, test recall of prior decisions | Memory/knowledge | Recall accuracy across sessions |
| 7 | **Custom Skill**: Create and use a project-specific skill | Skills system | Ease of creation, effectiveness |

### 3.4 Session 1 Results — Memory Eval (2026-06-06)

**Setup**: Synthetic FastAPI repo with legacy patterns. 5 memory seeds planted in a single session. Both tools used **qwen3.7-max** as the underlying model.

| Memory Seed | Test | Claude Code | Qoder CLI |
|---|---|---|---|
| M1: `/v2/` prefix for new endpoints | Create `/v2/comments` | 2/2 | 2/2 |
| M2: `@require_auth` decorator | Create decorator + PUT endpoint | 2/2 | 2/2 |
| M3: `is_active` soft-delete | Add column + soft-delete + filter | 2/2 | 2/2 |
| M4: Pydantic for new code | Create Tag schemas with pydantic | 2/2 | 2/2 |
| M5: pytest (implicit, never stated) | Switch to pytest without being told | 0/2 | 0/2 |
| | **Total** | **8/10** | **8/10** |

**Key observations:**
- Both tools applied explicit instructions (M1–M4) correctly and immediately
- Both failed the implicit test (M5) — followed existing `unittest` conventions rather than switching. This is arguably correct default behavior
- Qoder CLI was more thorough on M3 (added `is_active` filter to update/delete endpoints; Claude Code only filtered list/get)
- Code organization differed: Qoder created a separate `tags.py`; Claude Code appended to existing `schemas.py`

### 3.5 Industry Evaluation Methodology — CLI Coding Tools

#### Enterprise Evaluation Process (4 Phases)

| Phase | Duration | Activities |
|---|---|---|
| **Requirements Definition** | 1 week | Cross-functional team (eng, security, legal, procurement). Define 3-5 measurable success criteria |
| **Controlled Pilot** | 4-6 weeks | A/B test: one group uses the tool, control group doesn't. Single workflow/team scope |
| **Measurement** | Ongoing | Compare AI-touched code vs human-only code. Trace output to specific PRs |
| **Security & Procurement** | Parallel | SOC 2 Type II, zero-retention policy, no-training-on-data clauses, regional data residency |

#### Key Metrics to Track

| Category | Metrics |
|---|---|
| **Velocity** | Lead time, deployment frequency, cycle duration |
| **Throughput** | PR volume, suggestion acceptance rate, task completion count |
| **Quality** | Change failure rate, defect frequency, code review velocity, revision loops |
| **Adoption** | Daily active users, seat utilization, engagement depth by team |
| **Cost** | Cost per useful outcome (not lines of code generated) |

#### Industry Frameworks

- **DORA** (delivery health): lead time, deploy frequency, failure rate, recovery time
- **SPACE** (developer experience): satisfaction, performance, activity, communication, efficiency
- **Gartner Magic Quadrant** for AI Code Assistants (published Sep 2025) — leaders: GitHub, Amazon, GitLab, Google Cloud
- **DX ROI Calculator** — financial modeling for AI coding tool investment

#### ROI Reality

- Industry average: ~25% cycle time improvement, ~12% PR throughput gain
- Typical 100-developer annual spend: **$400K–$600K** (seats + tokens + training + verification tax)
- Companies with systematic evaluation achieve **3-4x more value** than ad-hoc adoption
- **Critical warning**: faster code generation doesn't mean faster delivery — automation can shift bottlenecks into review/testing. Track where delays migrate

#### Security Non-Negotiables

- SOC 2 Type II certification
- Zero-retention for code inputs
- Explicit contractual prohibition on training on customer data
- Regional data residency guarantees
- Air-gapped deployment option for regulated environments
- SAST/SCA scans on AI-generated code

---

## 4. Qwen3.x Series Evaluation

### 4.1 Model Lineup Summary

| Model | Type | Params (Total / Active) | Key Strength |
|---|---|---|---|
| Qwen3.7-Max | Proprietary API | Undisclosed | 80.4% SWE-bench Verified |
| Qwen3-Coder 480B | Open-weight | 480B | Flagship coding model |
| Qwen3-Coder-Next | MoE | 80B / 3B active | Local-deployable coding agent |
| Qwen3.5-27B | Dense | 27B | General + coding + vision |
| Qwen3.5-35B-A3B | MoE | 35B / 3B active | Efficient general model |
| Qwen3-235B-A22B | MoE | 235B / 22B active | Flagship reasoning |
| Qwen3-Omni 30B-A3B | MoE | 30B / 3B active | Full multimodal |

### 4.2 Standard Benchmark Scores

| Model | MMLU | GPQA Diamond | MATH | AIME25 |
|---|---|---|---|---|
| Qwen3-235B-A22B (Thinking) | 90.6% | — | — | — |
| Qwen3-235B-A22B | 87.8% | — | — | — |
| Qwen3.5-27B | 86.1% (MMLU-Pro) | 85.5% | — | — |
| Qwen3-Omni 30B-A3B | 86.6% (MMLU-Redux) | — | — | 65.0 |

### 4.3 Coding Benchmark Scores

| Model | SWE-bench Verified | SWE-bench Pro | Aider Polyglot | LiveCodeBench v6 | EvalPlus |
|---|---|---|---|---|---|
| Qwen3.7-Max | 80.4% | 60.6% | — | — | — |
| Qwen3-Coder-Next | 71.3% | 42.7% | 66.2% | 58.9 | 86.6 |
| Qwen3.5-27B | 72.4% | — | — | 80.7 | — |

**Reference — Frontier Comparisons:**

| Model | SWE-bench Verified | SWE-bench Pro |
|---|---|---|
| Claude Opus 4.5 | ~78.2% | — |
| DeepSeek V4 | 80.6% | — |
| GLM-5.1 | 77.8% | 58.4% |
| Kimi K2.6 | 80.2% | 58.6% |

### 4.4 Multimodality Matrix

| Model | Text | Vision | Audio | Video | Speech Out |
|---|---|---|---|---|---|
| Qwen3 (base) | Yes | No | No | No | No |
| Qwen3-Coder | Yes | No | No | No | No |
| Qwen3-VL | Yes | Yes | No | Yes | No |
| Qwen3-Omni | Yes | Yes | Yes | Yes | Yes |
| Qwen3.5 | Yes | Yes (native) | No | Yes | No |

### 4.5 Benchmark Frameworks to Use

| Framework | What It Tests | Setup | Why Use It |
|---|---|---|---|
| **SWE-bench Verified** | Real GitHub issue resolution (500 tasks) | Docker harness; 120GB storage, 16GB RAM, 8 CPU cores; `pip install swebench` | Industry standard for coding agent evaluation |
| **SWE-bench Pro** | Harder variant by Scale AI with stricter eval | Same infra, access via Scale AI | Differentiates frontier models better |
| **Aider Polyglot** | 225 Exercism tasks across 6 languages (C++, Go, Java, JS, Python, Rust) | `aider` CLI + model API | Tests multi-language coding + instruction following |
| **LiveCodeBench** | Continuously updated competitive programming | Web-based at livecodebench.github.io | Contamination-free (problems published after training cutoff) |
| **BigCodeBench** | 1,140 function-level tasks with complex instructions | Docker or Gradio; supports vLLM, OpenAI, Anthropic | Tests practical function-level coding |
| **EvalPlus** | HumanEval + MBPP with 80x/35x more test cases | `pip install evalplus` | More rigorous version of classic benchmarks |
| **Terminal-Bench 2.0** | CLI/terminal-based coding + agentic interaction | Terminal harness | Tests agent-style terminal workflows |

### 4.6 Evaluation Plan

**Phase 1 — Baseline Benchmarks:**
- Run SWE-bench Verified on: Qwen3.7-Max, Qwen3-Coder 480B, Qwen3-Coder-Next, Qwen3.5-27B
- Run Aider Polyglot on same models
- Compare against published scores for Claude, GPT-5, DeepSeek, GLM, Kimi

**Phase 2 — Coding-Specific Deep Dive:**
- LiveCodeBench v6 for algorithmic coding
- BigCodeBench for practical function-level tasks
- EvalPlus for rigorous basic coverage
- Terminal-Bench 2.0 for agentic terminal coding

**Phase 3 — Multimodality (if applicable):**
- Qwen3-VL and Qwen3-Omi on vision-language tasks (MMMU, MathVision)
- GUI understanding and screenshot-based coding tasks

### 4.7 Industry Benchmark Reliability & Enterprise Evaluation Practices

#### Benchmark Trust Hierarchy

From most to least trustworthy:

| Tier | Benchmark Type | Examples | Use For |
|---|---|---|---|
| **1 (Highest)** | Private benchmarks on proprietary code | Internal PR history tasks | Final decision |
| **2** | Temporally-gated benchmarks | LiveCodeBench, LiveBench | Reliable comparison |
| **3** | Fresh public benchmarks | SWE-bench Pro, Aider (new exercises) | Pre-filtering |
| **4 (Lowest)** | Established benchmarks | HumanEval, MBPP, original SWE-bench | Sanity checks only |

#### Known Contamination Issues

| Benchmark | Problem | Status |
|---|---|---|
| **SWE-bench Verified** | OpenAI [abandoned it](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) — frontier models reproduce exact historical patches from training data | Use SWE-bench Pro instead |
| **HumanEval / MBPP** | Saturated (95%+ for frontier models) | Can't differentiate models |
| **MMLU** | Score inflation; lost differentiating power | Use MMLU-Pro or GPQA Diamond |
| **SWE-bench (original)** | 12 public repos almost certainly in all training corpora | Replaced by Verified/Pro |

#### Enterprise Model Evaluation Process (5 Steps)

1. **Clarify requirements** — primary use case (completion, debugging, refactoring, agents?), constraints (data residency, latency, token limits)
2. **Public benchmarks as filter** — 2-3 benchmarks to narrow 20+ → 5-6 candidates
3. **Private bake-off** — build custom test suite from your own PR history (50-200 tasks). Test all candidates in identical conditions
4. **Custom weighting** — rank by your criteria, not public standings. A model excelling on your workload may rank poorly on leaderboards
5. **Quarterly re-evaluation** — models upgrade, tests saturate, data leakage inflates public metrics

#### Cost Efficiency: The Key Metric

The industry is shifting from **cost per token** to **cost per successful task**:

```
Cost per Success = (Run Cost + Human Review Cost + Overhead) / Successful Tasks
```

A cheap model that fails often costs MORE than an expensive model that succeeds. **Dynamic routing** (cheap models for simple tasks, premium for complex) is industry best practice — reduces costs 5-10x.

#### Private Benchmarking Platforms

| Platform | Strength |
|---|---|
| **Braintrust** | Eval-centric, CI/CD-native testing |
| **LangSmith** (LangChain) | Tracing + eval, multi-method scoring |
| **Langfuse** | Open-source, $300/mo enterprise tier |
| **SonarQube** | Static analysis: defect density, security, complexity of generated code |

#### What Benchmarks Miss

| Real-World Need | Benchmark Coverage |
|---|---|
| Navigating proprietary codebases | None |
| Vague/evolving requirements | None |
| Multi-step architectural decisions | None |
| Long-term code maintainability | SonarQube only |
| Integration with internal tools/APIs | None |
| Iterative debugging across sessions | Minimal |

#### Bridging the Real-World Gap

- **Production telemetry**: Track suggestion acceptance rate, code survival rate (persists after 1 week/1 month), iteration count before success
- **Blind A/B deployments**: Deploy multiple models simultaneously; developers don't know which model they're using
- **Multi-signal evaluation**: Combine 2-3 public benchmarks + private benchmarks + code quality analysis + human preference + production KPIs

---

## 5. Coding Harness Evaluation (Model + CLI)

### 5.1 Evaluation Matrix

| Harness Combination | Model | CLI Tool | Purpose |
|---|---|---|---|
| **Qwen3.x + Qoder** | Qwen3.7-Max, Qwen3-Coder 480B, Qwen3-Coder-Next | Qoder CLI | Alibaba's native stack |
| **3rd Models + Qoder** | DeepSeek V4, GLM-5.1, Kimi K2.6 | Qoder CLI | Qoder as model-agnostic tool |
| **Qwen3.x + OpenCode** | Qwen3.7-Max, Qwen3-Coder-Next | OpenCode | Open-source CLI baseline |
| **Qwen3.x + Claude Code** | Qwen3.7-Max, Qwen3-Coder-Next | Claude Code (CC) | Cross-vendor tool comparison |

### 5.2 Third-Party Models

| Model | Vendor | Params (Total / Active) | Architecture | SWE-bench Verified | License | API Pricing (per 1M tokens) |
|---|---|---|---|---|---|---|
| **DeepSeek V4** | DeepSeek | 1.6T MoE | MoE | 80.6% | MIT (open source) | $1.74 in / $3.48 out |
| **GLM-5.1** | Zhipu AI | 744B MoE | MoE | 77.8% (58.4% Pro) | MIT (open source) | $1.00 in / $3.20 out |
| **Kimi K2.6** | Moonshot AI | 1T MoE (32B active) | MoE | 80.2% (58.6% Pro) | Open source | — |

**Notable Capabilities:**
- **DeepSeek V4**: Strongest open-source coding model; 1.6T MoE with exceptional SWE-bench score
- **GLM-5.1**: Trained entirely on Huawei Ascend 910B chips; cheapest API pricing
- **Kimi K2.6**: Agent Swarm (300 sub-agents), 12+ hour continuous execution; unique long-horizon capability

### 5.3 Agent Harness Evaluation Frameworks

| Framework | Description | How to Use for Harness Eval |
|---|---|---|
| **SWE-bench + SWE-Agent** | Standard SWE-bench with SWE-Agent harness | Fix the agent harness, swap only the LLM backend; compare patch resolution rates |
| **SWE-bench + OpenHands** | SWE-bench with OpenHands agent framework | Supports parallel Docker execution (30x speedup); swap LLM provider |
| **Terminal-Bench 2.0** | CLI/terminal-based agentic evaluation | Test model+CLI combinations on terminal coding tasks |
| **AgentBench** | Multi-environment agent evaluation | Tests agents across OS, DB, web, and code environments |
| **DevBench** | End-to-end software development benchmark | Tests full SDLC: design → implementation → testing → review |
| **ML-Dev-Bench** | ML development workflow evaluation | Tests agent on ML-specific development tasks |

### 5.4 Fair Comparison Methodology

To ensure fair comparison across model+CLI combinations:

1. **Fixed Agent Harness**: Use a consistent agent framework (SWE-Agent, OpenHands, or mini-SWE-agent) and swap only the underlying LLM
2. **Standardized Task Partitions**: Use the same SWE-bench Verified task set for all combinations
3. **Resource Limits**: Equal token budgets, time limits, and compute constraints per task
4. **Reproducibility**: Docker-based evaluation with pinned versions and fixed seeds
5. **Multiple Runs**: 3+ runs per combination to account for stochasticity

### 5.5 Evaluation Tasks

| # | Task Category | Benchmark | Metrics |
|---|---|---|---|
| 1 | **Issue Resolution** | SWE-bench Verified (500 tasks) | % Resolved, time per task, token cost |
| 2 | **Multi-Language Coding** | Aider Polyglot (225 tasks, 6 languages) | Pass rate, cost per task |
| 3 | **Algorithmic Coding** | LiveCodeBench v6 | Pass@1, self-repair rate |
| 4 | **Function-Level Tasks** | BigCodeBench (1,140 tasks) | pass@k (completion + instruction modes) |
| 5 | **Terminal Agent Tasks** | Terminal-Bench 2.0 | Task completion rate |
| 6 | **Full SDLC** | DevBench | Design → implement → test → review quality |
| 7 | **Real-World Feature** | Custom: implement a feature spec in a real OSS project | PR acceptance, test pass rate, code review score |

### 5.6 Results Template

| Harness | SWE-bench Verified | Aider Polyglot | LiveCodeBench | Terminal-Bench | Cost/Task | Notes |
|---|---|---|---|---|---|---|
| Qwen3.7-Max + Qoder | — | — | — | — | — | — |
| Qwen3-Coder 480B + Qoder | — | — | — | — | — | — |
| DeepSeek V4 + Qoder | — | — | — | — | — | — |
| GLM-5.1 + Qoder | — | — | — | — | — | — |
| Kimi K2.6 + Qoder | — | — | — | — | — | — |
| Qwen3-Coder-Next + OpenCode | — | — | — | — | — | — |
| Qwen3-Coder-Next + Claude Code | — | — | — | — | — | — |

### 5.7 Industry Harness Evaluation Practices

#### The Harness Effect (Critical Finding)

A 2025 study ([arXiv 2605.27922](https://arxiv.org/html/2605.27922v1)) measured a **23.8-point gap** between the best and worst harness for the same model. Performance must be reported at the **model+harness** level, not attributed to the model alone.

#### Agent Evaluation Platforms

| Platform | Description | URL |
|---|---|---|
| **SWE-bench** | Foundational benchmark + evaluation harness + public leaderboard | [swebench.com](https://swebench.com) |
| **HAL** (Princeton) | 9 benchmarks; tracks cost-performance, consistency, robustness, self-awareness | [hal.cs.princeton.edu](https://hal.cs.princeton.edu) |
| **Artificial Analysis** | 30+ coding tools tracked with token/cost data | [artificialanalysis.ai/agents/coding](https://artificialanalysis.ai/agents/coding) |
| **Kilo.ai** | Ranks by actual developer usage (token consumption); refreshes every 5 min | [kilo.ai/leaderboard](https://kilo.ai/leaderboard) |
| **Codesota** | Aggregates 8 benchmarks; no composite scores, full transparency | [codesota.com/llm](https://www.codesota.com/llm) |

#### Agent Frameworks for Evaluation

| Framework | Use Case | Setup Complexity |
|---|---|---|
| **mini-SWE-agent** | Fairest harness for model comparison (100 lines, no framework bias) | `pip install mini-swe-agent` |
| **SWE-Agent** (full) | Custom tool configurations, advanced memory | Moderate; requires x86, Docker, YAML config |
| **OpenHands** | Distributed cloud eval at 30x speedup (32 concurrent workers) | Docker-based; remote runtime in beta |

#### Infrastructure & Cost

| Component | Option | Cost |
|---|---|---|
| **Compute** | Modal (serverless, SWE-bench integration) or 32-core/128GB VM | $20-50 |
| **Sandbox** | Docker per task (Epoch AI optimized images: 67 GiB vs 684 GiB raw) | Included |
| **GPU** | **Not needed** for API-based models; only CPU for Docker | $0 |
| **API (frontier models)** | 500 tasks × 7 combos | $500-1,500 |
| **API (budget models)** | DeepSeek, Qwen | $10-50 |
| **Engineering time** | Full evaluation | 4-6 days |
| **Total** | 5-7 combinations with statistical rigor | **$520-1,600** |

#### Recommended Execution Plan

| Phase | Time | Activities |
|---|---|---|
| **Setup** | 1-2 days | Choose mini-SWE-agent as baseline harness. Provision Modal or 32-core VM. Pre-build Docker images |
| **Pilot** | 1 day | Run SWE-bench Lite (534 tasks) with one combo as dry run. Validate pipeline, check cost/task |
| **Full Eval** | 2-3 days | Run SWE-bench Verified (500 tasks) per combo in parallel. 3-5 repetitions for statistical significance |
| **Analysis** | 1 day | Comparison matrix: resolve rate, cost/task, tokens, consistency, time. Identify Pareto frontier |

#### Fair Comparison Methodology

1. **Fix the harness, vary the model** — use mini-SWE-agent for all models to isolate model quality
2. **Fix the model, vary the harness** — test same model across harnesses to understand tooling impact
3. **Measure beyond pass/fail** (HAL approach): cost, efficiency, consistency (3-5 runs), robustness, self-awareness
4. **Report model+harness together** — never attribute performance to the model alone

#### Quick-Start Tip

Run **SWE-bench Lite** (534 tasks) first — gives directional results in under a day at ~1/4 the cost. Then run full SWE-bench Verified only on the top 2-3 contenders.

---

## 6. Execution Timeline

| Phase | Duration | Activities |
|---|---|---|
| **Phase 1: Setup** | Week 1 | Set up evaluation infrastructure (SWE-bench harness, Docker envs, API keys) |
| **Phase 2: Baseline Benchmarks** | Week 2–3 | Run standard benchmarks on all Qwen3.x models |
| **Phase 3: CLI Feature Eval** | Week 3–4 | Qoder CLI vs Claude Code feature comparison (§3) |
| **Phase 4: Harness Eval** | Week 4–6 | Run all model+CLI combinations through coding harness benchmarks (§5) |
| **Phase 5: Analysis & Report** | Week 7 | Compile results, statistical analysis, final report |
