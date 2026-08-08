<a id="readme-top"></a>

# Institutional Content Ops

Operational workflows and deterministic preflight checks for accountable institutional content production.

<p>
  <a href="https://github.com/ChrysFu/institutional-content-ops/actions/workflows/quality.yml"><img alt="Quality workflow" src="https://img.shields.io/github/actions/workflow/status/ChrysFu/institutional-content-ops/quality.yml?branch=main&amp;style=flat" /></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-15803D?style=flat" /></a>
  <a href="https://github.com/ChrysFu/institutional-content-ops/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/ChrysFu/institutional-content-ops?style=flat" /></a>
  <a href="https://github.com/ChrysFu/institutional-content-ops/search?l=Python"><img alt="Top language" src="https://img.shields.io/github/languages/top/ChrysFu/institutional-content-ops?style=flat" /></a>
  <a href="CONTRIBUTING.md"><img alt="Pull requests welcome" src="https://img.shields.io/badge/PRs-welcome-15803D?style=flat" /></a>
</p>

<p align="center">
  <img src="assets/readme/institutional-content-ops-banner.svg" alt="Institutional Content Ops banner" width="100%" />
</p>

<div align="right"><a href="#english">English</a> | <a href="#简体中文">简体中文</a></div>

<details>
<summary>Table of Contents / 目录</summary>

- [English](#english)
  - [Overview](#overview)
  - [Workflow](#workflow)
  - [Quick start](#quick-start)
  - [Configuration and exit codes](#configuration-and-exit-codes)
  - [Validation](#validation)
  - [Documentation map](#documentation-map)
  - [Safety boundary](#safety-boundary)
  - [Contributing](#contributing)
  - [License](#license)
- [简体中文](#简体中文)
  - [项目概览](#项目概览)
  - [工作流](#工作流)
  - [快速开始](#快速开始)
  - [配置与退出码](#配置与退出码)
  - [验证](#验证)
  - [文档导航](#文档导航)
  - [安全边界](#安全边界)
  - [参与贡献](#参与贡献)
  - [许可证](#许可证)

</details>

<a id="english"></a>

## English

### Overview

Institutional Content Ops combines operational documentation with a Python standard-library preflight guard. It is designed for meeting preparation and institutional publishing where source traceability, titles, names, numbers, permissions, and human approval matter more than publishing speed.

The repository now covers the full path from intake and source preparation through drafting, automated preflight, editorial review, final approval, scheduling, publication, data collection, and incident handling. Automation may block unsafe transitions, but it can never approve a release.

### Workflow

<p align="center">
  <img src="assets/readme-architecture.svg" alt="Institutional content workflow and human responsibility boundaries" width="100%" />
</p>

The operational model has explicit entry and exit criteria, revision tracking, failure routes, retry limits, escalation rules, idempotency guidance, and minimum audit fields. The detailed state machine and failure matrix live in [workflows.md](workflows.md); incident response and rollback steps live in the [operations runbook](docs/operations-runbook.md).

### Quick start

No third-party package is required. Python 3.11 or later is recommended.

Run the built-in compatibility smoke check:

```bash
python3 src/content_guard.py --self-test
```

Evaluate a UTF-8 draft against a JSON policy and fail a pipeline when issues remain:

```bash
python3 src/content_guard.py \
  --draft examples/draft-ready.md \
  --policy content-policy.example.json \
  --output artifacts/preflight.json \
  --fail-on-issues
```

Use standard input by passing `--draft -`:

```bash
printf '%s\n' '来源：经授权的会议纪要。' | \
  python3 src/content_guard.py --draft - --policy content-policy.example.json
```

### Configuration and exit codes

The policy file accepts three fields:

| Field | Type | Default | Purpose |
|---|---|---|---|
| `required_terms` | array of non-empty strings | `[]` | Terms that must appear in the draft |
| `forbidden_terms` | array of non-empty strings | `[]` | Terms that block human review when found |
| `case_sensitive` | boolean | `true` | Controls Unicode-aware term matching |

The guard distinguishes content findings from system failures:

| Exit code | Meaning |
|---:|---|
| `0` | The command completed; with `--fail-on-issues`, the draft may enter human review |
| `1` | Content findings remain and `--fail-on-issues` was enabled |
| `2` | Draft, encoding, policy JSON, or output handling failed |

Results include issue lists, counts, and `ready_for_human_review`. `release_approved` is always `false`. The guard is stateless: the workflow caller owns `content_id`, revision, policy version, source hash, and audit-event persistence. Output files are written atomically so interrupted runs do not leave partial JSON.

### Validation

The `Quality` workflow runs on pull requests, pushes to `main`, and manual dispatches across Python 3.11–3.13. It uses read-only repository permissions, cancels superseded runs, sets a timeout, and executes the same checks available locally:

```bash
python3 -m compileall -q src tests
python3 -m unittest discover -s tests -v
python3 src/content_guard.py --self-test
python3 src/content_guard.py --draft examples/draft-ready.md --policy content-policy.example.json --fail-on-issues
python3 src/repository_checks.py .
```

`repository_checks.py` detects missing local Markdown targets and invalid JSON files. GitHub Action dependencies are pinned to commits and monitored by Dependabot.

### Documentation map

| Topic | Document |
|---|---|
| Project stages, content state machine, retries, escalation, audit fields | [workflows.md](workflows.md) |
| Meeting and publishing SOPs, preflight integration, correction process | [skills.md](skills.md) |
| Closed-source prompting, verification markers, editorial boundaries | [prompt-engineering.md](prompt-engineering.md) |
| Content positioning, audience, columns, and templates | [product-design.md](product-design.md) |
| Rotating quasi-experiments and data-quality rules | [data-analysis.md](data-analysis.md) |
| Incident classification, recovery, rollback, and closure | [docs/operations-runbook.md](docs/operations-runbook.md) |

### Safety boundary

> [!IMPORTANT]
> A passing preflight is not fact checking, legal review, permission verification, political or compliance review, or publication approval.

- AI may structure source material and produce drafts; people remain responsible for facts, tone, permissions, editing, and release decisions.
- A tool error fails closed and must not be interpreted as a pass.
- Policy changes invalidate results produced under an older policy version.
- Do not place confidential drafts, credentials, private analytics, or unnecessary personal data in tests or logs.

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the test-first development loop, validation commands, compatibility expectations, and pull-request requirements.

### License

Copyright (c) 2026 ChrysFu. The entire repository, including source code, tests, workflows, documentation, templates, examples, and visual assets, is licensed under the [MIT License](LICENSE). The license permits reuse and adaptation provided that the copyright and permission notices are retained; it does not grant trademark rights.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<a id="简体中文"></a>

## 简体中文

### 项目概览

Institutional Content Ops 将运营文档与纯 Python 标准库实现的内容预检工具结合起来，服务于会务筹备和机构内容发布。此类场景中，来源可追溯、人物头衔、机构名称、数字、授权和人工审批比发布速度更重要。

仓库现已覆盖从任务受理、素材准备、起草、自动预检、编辑复审、负责人终审、排期、发布、数据回收到事件处置的完整链路。自动化可以阻止不安全的状态流转，但永远不能批准发布。

### 工作流

<p align="center">
  <img src="assets/readme-architecture.svg" alt="机构内容工作流与人工责任边界" width="100%" />
</p>

运营模型明确规定了入口和出口条件、修订追踪、失败路径、重试上限、升级规则、幂等原则和最小审计字段。详细状态机与异常矩阵见 [workflows.md](workflows.md)，事件响应和回滚步骤见[运行手册](docs/operations-runbook.md)。

### 快速开始

项目不需要第三方包，建议使用 Python 3.11 或更高版本。

运行内置兼容性冒烟检查：

```bash
python3 src/content_guard.py --self-test
```

使用 JSON 策略检查 UTF-8 草稿，并在问题未解决时让流水线失败：

```bash
python3 src/content_guard.py \
  --draft examples/draft-ready.md \
  --policy content-policy.example.json \
  --output artifacts/preflight.json \
  --fail-on-issues
```

传入 `--draft -` 可从标准输入读取：

```bash
printf '%s\n' '来源：经授权的会议纪要。' | \
  python3 src/content_guard.py --draft - --policy content-policy.example.json
```

### 配置与退出码

策略文件支持三个字段：

| 字段 | 类型 | 默认值 | 作用 |
|---|---|---|---|
| `required_terms` | 非空字符串数组 | `[]` | 草稿中必须出现的词语 |
| `forbidden_terms` | 非空字符串数组 | `[]` | 命中后阻止进入人工审阅的词语 |
| `case_sensitive` | 布尔值 | `true` | 控制 Unicode 感知的大小写匹配 |

预检工具会区分内容问题和系统故障：

| 退出码 | 含义 |
|---:|---|
| `0` | 命令正常完成；启用 `--fail-on-issues` 时表示可进入人工审阅 |
| `1` | 启用了 `--fail-on-issues`，且内容问题仍未解决 |
| `2` | 草稿、编码、策略 JSON 或输出处理失败 |

结果包含问题清单、计数和 `ready_for_human_review`；`release_approved` 永远为 `false`。预检工具是无状态的，工作流调用方负责维护 `content_id`、修订号、策略版本、来源哈希和审计事件。输出文件采用原子写入，避免中断时留下不完整 JSON。

### 验证

`Quality` 工作流在 Pull Request、推送到 `main` 和手动触发时运行，覆盖 Python 3.11–3.13。它使用只读仓库权限、取消已被新提交替代的运行、设置超时，并执行与本地相同的检查：

```bash
python3 -m compileall -q src tests
python3 -m unittest discover -s tests -v
python3 src/content_guard.py --self-test
python3 src/content_guard.py --draft examples/draft-ready.md --policy content-policy.example.json --fail-on-issues
python3 src/repository_checks.py .
```

`repository_checks.py` 会发现缺失的 Markdown 本地目标和无效 JSON 文件。GitHub Action 依赖固定到具体提交，并由 Dependabot 监控更新。

### 文档导航

| 主题 | 文档 |
|---|---|
| 项目阶段、内容状态机、重试、升级和审计字段 | [workflows.md](workflows.md) |
| 会务与发布 SOP、预检接入和更正流程 | [skills.md](skills.md) |
| 封闭素材 Prompt、核对标记和编辑边界 | [prompt-engineering.md](prompt-engineering.md) |
| 内容定位、读者、栏目和模板 | [product-design.md](product-design.md) |
| 轮换式准实验与数据质量规则 | [data-analysis.md](data-analysis.md) |
| 事件分级、恢复、回滚和关闭 | [docs/operations-runbook.md](docs/operations-runbook.md) |

### 安全边界

> [!IMPORTANT]
> 预检通过不等于事实核查、法律审查、授权核验、政治或合规审查，也不等于批准发布。

- AI 可以整理素材结构和生成初稿；事实、语气、授权、编辑和发布决定仍由人工负责。
- 工具异常必须失败关闭，不能被解释为检查通过。
- 策略发生变化后，旧策略版本产生的检查结果失效。
- 不在测试或日志中放入机密草稿、凭据、私有分析数据或非必要个人信息。

### 参与贡献

测试优先的开发循环、验证命令、兼容性要求和 Pull Request 规范见 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 许可证

Copyright (c) 2026 ChrysFu。本仓库的源代码、测试、工作流、文档、模板、示例和视觉资产统一采用 [MIT License](LICENSE)。在保留版权和许可声明的前提下可以复用和修改；许可证不授予商标权。

<p align="right">(<a href="#readme-top">返回顶部</a>)</p>
