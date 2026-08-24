<a id="readme-top"></a>

# Institutional Content Ops

Deterministic content gates and accountable workflows for institutional publishing.

[![Quality workflow](https://img.shields.io/github/actions/workflow/status/ChrysFu/institutional-content-ops/quality.yml?branch=main&style=flat)](https://github.com/ChrysFu/institutional-content-ops/actions/workflows/quality.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-15803D?style=flat)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/ChrysFu/institutional-content-ops?style=flat)](https://github.com/ChrysFu/institutional-content-ops/commits/main)
[![Python](https://img.shields.io/badge/Python-3.11--3.14-3776AB?logo=python&logoColor=white&style=flat)](https://www.python.org/)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-15803D?style=flat)](CONTRIBUTING.md)

<p align="center">
  <img src="assets/readme/institutional-content-ops-banner.svg" alt="Institutional Content Ops banner" width="100%" />
</p>

<div align="right"><a href="#简体中文">简体中文</a> | <a href="#english">English</a></div>

<details>
<summary>目录 / Table of contents</summary>

- [简体中文](#简体中文)
  - [项目概览](#项目概览)
  - [核心能力](#核心能力)
  - [工作流](#工作流)
  - [快速开始](#快速开始)
  - [策略配置](#策略配置)
  - [报告与审计](#报告与审计)
  - [退出码](#退出码)
  - [验证与文档](#验证与文档)
  - [安全边界](#安全边界)
  - [参与贡献与许可](#参与贡献与许可)
- [English](#english)
  - [Overview](#overview)
  - [Capabilities](#capabilities)
  - [Workflow model](#workflow-model)
  - [Quick start](#quick-start-en)
  - [Policy configuration](#policy-configuration)
  - [Reports and audit data](#reports-and-audit-data)
  - [Exit codes](#exit-codes)
  - [Validation and documentation](#validation-and-documentation)
  - [Safety boundary](#safety-boundary)
  - [Contributing and license](#contributing-and-license)

</details>

<a id="简体中文"></a>

## 简体中文

### 项目概览

Institutional Content Ops 面向会务筹备和机构内容发布，将可执行的纯 Python 内容门禁与人工负责的运营状态机结合起来。项目覆盖任务受理、素材准备、起草、自动预检、编辑复审、负责人终审、排期、发布、数据回收和事件处置。

自动化负责发现可确定的问题并阻止不安全流转；事实、人物头衔、机构名称、数字、授权、合规判断与最终发布始终由人负责。

### 核心能力

- **兼容的单文件预检**：`preflight()` 和 `--draft` 继续返回既有字段并保持 `0/1/2` 退出语义。
- **确定性批量扫描**：`--scan` 可重复使用，递归扫描目录中的 `.md` 与 `.txt`，忽略其他扩展名；空批次失败关闭。
- **可治理规则**：内置规则和自定义规则均有稳定 ID；支持 `required_term`、`forbidden_term` 和 `regex`，严重级别为 `error`、`warning` 或 `note`。
- **JSON 与 SARIF 2.1.0**：同一规范化 finding 模型生成两种报告，包含规则元数据、文件、消息及可用的行列位置。
- **审计可追溯**：报告保存内容 ID、revision、策略版本、策略哈希、文档哈希和确定性 scan ID，但不保存正文。
- **失败关闭**：内容阻断返回退出码 `1`；路径、编码、策略或输出错误返回 `2`，不会被误判为通过。

### 工作流

<p align="center">
  <img src="assets/readme-architecture.svg" alt="机构内容工作流与人工责任边界" width="100%" />
</p>

流程明确规定入口/出口条件、revision、失败回路、重试上限、升级规则、幂等原则与最小审计字段。自动检查通过只允许内容进入 `EditorialReview`，不能跳过人工复审或终审。

完整状态机见 [workflows.md](workflows.md)，故障分级与回滚见[运行手册](docs/operations-runbook.md)。

### 快速开始

项目运行时只使用 Python 标准库，支持 Python 3.11–3.14，无需安装第三方运行依赖。

运行兼容性冒烟检查：

```bash
python3 src/content_guard.py --self-test
```

检查单个 UTF-8 草稿：

```bash
python3 src/content_guard.py \
  --draft examples/draft-ready.md \
  --policy content-policy.example.json \
  --output artifacts/preflight.json \
  --fail-on-issues
```

批量扫描目录并生成 SARIF：

```bash
python3 src/content_guard.py \
  --scan examples \
  --policy content-policy.example.json \
  --format sarif \
  --content-id launch-2026 \
  --revision 4 \
  --policy-version editorial-v2 \
  --output artifacts/content-scan.sarif \
  --fail-on-issues
```

使用多个 `--scan` 可组合文件与目录；单文件模式可传 `--draft -` 从标准输入读取。

### 策略配置

[content-policy.example.json](content-policy.example.json) 展示完整策略。顶层字段如下：

| 字段 | 类型 | 默认值 | 作用 |
|---|---|---|---|
| `required_terms` | 非空字符串数组 | `[]` | 每份文档必须包含的词语 |
| `forbidden_terms` | 非空字符串数组 | `[]` | 命中后产生内置 error finding |
| `case_sensitive` | boolean | `true` | 控制词语与 regex 的大小写匹配 |
| `rules` | 规则对象数组 | `[]` | 具有稳定 ID 和严重级别的扩展规则 |

自定义规则必须包含 `id`、`type`、`severity`、`message`，并按类型提供 `term` 或 `pattern`。规则 ID 必须唯一，不能冒用 `content.unresolved_check`、`content.required_term` 或 `content.forbidden_term`。

```json
{
  "rules": [
    {
      "id": "CLAIM001",
      "type": "regex",
      "pattern": "唯一(指定|授权)",
      "severity": "warning",
      "message": "核验排他性表述的证据与授权范围。"
    }
  ]
}
```

`error` 阻止进入人工审阅；`warning` 与 `note` 只报告、不阻断。所有结果的 `release_approved` 始终为 `false`。

### 报告与审计

JSON 批量报告包含总体严重级别计数、规则目录、逐文档 SHA-256 与 findings。SARIF 2.1.0 适合 CI 制品、代码扫描消费者和逐行定位。两种格式都来自同一次扫描，不会改变门禁判断。

调用方通过 `--content-id`、`--revision`、`--policy-version` 传入业务上下文；工具追加 `policy_sha256` 与确定性 `scan_id`。策略或内容变化会改变相应哈希，便于审计系统判断旧结果是否失效。

### 退出码

| 退出码 | 含义 |
|---:|---|
| `0` | 命令正常完成；启用 `--fail-on-issues` 时表示没有 error finding |
| `1` | 已启用 `--fail-on-issues`，且内容存在阻断问题 |
| `2` | 输入、UTF-8 编码、策略、扫描或原子输出失败 |

### 验证与文档

`Quality` workflow 在 Pull Request、推送到 `main` 和手动触发时验证 Python 3.11–3.14。其依赖固定到 commit，使用只读权限、超时与并发取消。

```bash
ruff check src tests
python3 -m compileall -q src tests
python3 -m unittest discover -s tests -v
python3 src/content_guard.py --self-test
python3 src/repository_checks.py .
```

| 主题 | 文档 |
|---|---|
| 近期活跃对标项目、优点、取舍与路线图 | [docs/github-landscape.md](docs/github-landscape.md) |
| 状态机、批量预检、重试、升级与审计字段 | [workflows.md](workflows.md) |
| 事件分级、恢复、SARIF 审计和回滚 | [docs/operations-runbook.md](docs/operations-runbook.md) |
| 会务与发布 SOP、核对清单和更正流程 | [skills.md](skills.md) |
| 封闭素材 Prompt、验证标记和编辑边界 | [prompt-engineering.md](prompt-engineering.md) |
| 内容定位、读者、栏目与模板 | [product-design.md](product-design.md) |
| 准实验和数据质量规则 | [data-analysis.md](data-analysis.md) |

### 安全边界

> [!IMPORTANT]
> 预检通过不等于事实核查、法律审查、授权核验、政治或合规审查，也不等于批准发布。

- 工具异常必须失败关闭，不能解释为内容通过。
- 策略或内容变化后，应以新 revision 重新扫描并重新完成所需人工审批。
- 不在策略、测试、报告或日志中放入机密正文、凭据、私有分析数据或非必要个人信息。

### 参与贡献与许可

测试优先的开发循环、兼容性要求和 Pull Request 检查单见 [CONTRIBUTING.md](CONTRIBUTING.md)。本仓库的代码、测试、文档、模板、示例与视觉资产统一采用 [MIT License](LICENSE)。

<p align="right">(<a href="#readme-top">返回顶部</a>)</p>

<a id="english"></a>

## English

### Overview

Institutional Content Ops combines an executable, standard-library Python content gate with a human-owned operating state machine for meeting preparation and institutional publishing. It covers intake, source preparation, drafting, automated preflight, editorial review, final approval, scheduling, publication, measurement, and incident response.

Automation detects deterministic issues and blocks unsafe transitions. People remain responsible for facts, titles, organization names, numbers, permissions, compliance judgment, and the final release decision.

### Capabilities

- **Compatible single-file preflight**: `preflight()` and `--draft` preserve existing fields and `0/1/2` exit semantics.
- **Deterministic batch scans**: repeat `--scan` to scan files and recursively discover `.md` and `.txt` documents; unsupported files are ignored and empty batches fail closed.
- **Governable rules**: built-in and custom rules have stable IDs. Custom types are `required_term`, `forbidden_term`, and `regex`, with `error`, `warning`, or `note` severity.
- **JSON and SARIF 2.1.0**: both formats come from one canonical finding model with rule metadata, files, messages, and line/column locations when available.
- **Audit traceability**: reports record content ID, revision, policy version, policy hash, document hashes, and a deterministic scan ID without storing document bodies.
- **Fail-closed behavior**: blocking content returns `1`; path, encoding, policy, scan, or output failures return `2` and cannot be interpreted as a pass.

### Workflow model

<p align="center">
  <img src="assets/readme-architecture.svg" alt="Institutional content workflow and human responsibility boundaries" width="100%" />
</p>

The process defines entry and exit criteria, revisions, failure loops, retry limits, escalation, idempotency, and minimum audit fields. A passing automated scan permits only a transition to `EditorialReview`; it cannot bypass editorial or final human approval.

See [workflows.md](workflows.md) for the full state machine and the [operations runbook](docs/operations-runbook.md) for incident classification and rollback.

<a id="quick-start-en"></a>

### Quick start

The runtime uses only the Python standard library, supports Python 3.11–3.14, and requires no third-party runtime packages.

Run the compatibility smoke check:

```bash
python3 src/content_guard.py --self-test
```

Check one UTF-8 draft:

```bash
python3 src/content_guard.py \
  --draft examples/draft-ready.md \
  --policy content-policy.example.json \
  --output artifacts/preflight.json \
  --fail-on-issues
```

Scan a directory and emit SARIF:

```bash
python3 src/content_guard.py \
  --scan examples \
  --policy content-policy.example.json \
  --format sarif \
  --content-id launch-2026 \
  --revision 4 \
  --policy-version editorial-v2 \
  --output artifacts/content-scan.sarif \
  --fail-on-issues
```

Repeat `--scan` to combine files and directories. In single-file mode, pass `--draft -` to read standard input.

### Policy configuration

[content-policy.example.json](content-policy.example.json) demonstrates the full policy shape.

| Field | Type | Default | Purpose |
|---|---|---|---|
| `required_terms` | array of non-empty strings | `[]` | Terms every document must contain |
| `forbidden_terms` | array of non-empty strings | `[]` | Terms that produce a built-in error finding |
| `case_sensitive` | boolean | `true` | Controls case matching for terms and regex rules |
| `rules` | array of rule objects | `[]` | Extension rules with stable IDs and severity |

Each custom rule requires `id`, `type`, `severity`, and `message`, plus `term` or `pattern` for its type. IDs must be unique and cannot reuse `content.unresolved_check`, `content.required_term`, or `content.forbidden_term`.

```json
{
  "rules": [
    {
      "id": "CLAIM001",
      "type": "regex",
      "pattern": "唯一(指定|授权)",
      "severity": "warning",
      "message": "Verify the evidence and permission scope for exclusivity claims."
    }
  ]
}
```

An `error` blocks entry to human review. A `warning` or `note` is reported but does not block. `release_approved` is always `false`.

### Reports and audit data

The JSON batch report contains aggregate severity counts, a rule catalog, per-document SHA-256 values, and findings. SARIF 2.1.0 supports CI artifacts, code-scanning consumers, and line-level locations. Selecting a format does not change gate behavior.

Callers supply business context through `--content-id`, `--revision`, and `--policy-version`; the tool adds `policy_sha256` and a deterministic `scan_id`. Content or policy changes alter the corresponding hashes so audit systems can invalidate stale results.

### Exit codes

| Exit code | Meaning |
|---:|---|
| `0` | Command completed; with `--fail-on-issues`, no error finding exists |
| `1` | `--fail-on-issues` is enabled and blocking content issues remain |
| `2` | Input, UTF-8 encoding, policy, scan, or atomic output handling failed |

### Validation and documentation

The `Quality` workflow validates Python 3.11–3.14 on pull requests, pushes to `main`, and manual dispatches. Actions are commit-pinned and run with read-only permissions, a timeout, and superseded-run cancellation.

```bash
ruff check src tests
python3 -m compileall -q src tests
python3 -m unittest discover -s tests -v
python3 src/content_guard.py --self-test
python3 src/repository_checks.py .
```

| Topic | Document |
|---|---|
| Recently active peer projects, strengths, tradeoffs, and roadmap | [docs/github-landscape.md](docs/github-landscape.md) |
| State machine, batch preflight, retries, escalation, and audit fields | [workflows.md](workflows.md) |
| Incident classification, recovery, SARIF audit, and rollback | [docs/operations-runbook.md](docs/operations-runbook.md) |
| Meeting and publishing SOPs, checklists, and corrections | [skills.md](skills.md) |
| Closed-source prompting, verification markers, and editorial boundaries | [prompt-engineering.md](prompt-engineering.md) |
| Positioning, audiences, columns, and templates | [product-design.md](product-design.md) |
| Quasi-experiments and data-quality rules | [data-analysis.md](data-analysis.md) |

### Safety boundary

> [!IMPORTANT]
> A passing preflight is not fact checking, legal review, permission verification, political or compliance review, or publication approval.

- Tool failures must fail closed and cannot be interpreted as content approval.
- Policy or content changes require a new revision, a new scan, and the applicable human approvals.
- Do not place confidential bodies, credentials, private analytics, or unnecessary personal data in policies, tests, reports, or logs.

### Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) for the test-first loop, compatibility rules, and pull-request checklist. Code, tests, documentation, templates, examples, and visual assets are licensed under the [MIT License](LICENSE).

<p align="right">(<a href="#readme-top">back to top</a>)</p>
