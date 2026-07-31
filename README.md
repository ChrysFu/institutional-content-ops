<div align="right"><a href="#简体中文">简体中文</a> | <a href="#english">English</a></div>

<a id="简体中文"></a>

# 机构内容运营工作流

<div align="center">

<strong>封闭素材输入 · 可核对初稿 · 人工三审 · 小样本复盘</strong>

![Workflow](https://img.shields.io/badge/Workflow-Human%20in%20the%20Loop-166534?style=flat-square)
![Input](https://img.shields.io/badge/Input-Closed%20Source%20Pack-0369A1?style=flat-square)
![Evidence](https://img.shields.io/badge/Evidence-%5BCHECK%5D-F59E0B?style=flat-square)
![Privacy](https://img.shields.io/badge/Identity-Anonymized-52525B?style=flat-square)
![Language](https://img.shields.io/badge/Language-Python%203-3776AB?style=flat-square&logo=python&logoColor=white)

📋 [协作台账](./workflows.md) · ✅ [执行 SOP](./skills.md) · ✍️ [内容 Prompt](./prompt-engineering.md) · 📰 [栏目与模板](./product-design.md) · 📊 [轮换复盘](./data-analysis.md)

</div>

> [!IMPORTANT]
> AI 只处理已提供的封闭素材。人物、机构、头衔、时间、地点、数字和政策表述缺失时必须输出 `[CHECK]`，不得自行补写背景或提高原素材的主张强度。

## 目录

- [简介](#简介)
- [项目亮点](#项目亮点)
- [效果展示](#效果展示)
- [功能清单](#功能清单)
- [工具与方法栈](#工具与方法栈)
- [安装与部署](#安装与部署)
- [项目结构](#项目结构)
- [发布前检查](#发布前检查)
- [FAQ](#faq)
- [可信度与保密边界](#可信度与保密边界)

## 简介

本仓库是一套面向机构公众号、行业资讯、会议报道和政策解读初稿的**内容生产工作流与 Prompt 工具包**。它把 AI 放在“整理结构、生成可核对初稿”的位置，把事实判断、表达分寸和发布责任保留给人工三审。

| 输入 | 中间产物 | 输出 |
|---|---|---|
| 封闭素材包、专名表、内容类型、发布规范、审核责任 | 初稿、引用映射、`[CHECK]` 清单、图片署名 | 三审记录、发布稿、发布检查表、栏目与轮换复盘 |

## 项目亮点

- 📦 **封闭素材包**：只基于议程、已确认要点、公开背景和授权图片工作。
- 🔖 **专名表回查**：机构、姓名、头衔和固定表述逐项核对。
- 🧷 **主张强度守恒**：不把“计划”“探索”“可能”升级成“完成”“领先”“必然”。
- 🚩 **待核对显式化**：证据不足时标记 `[CHECK]`，而不是补写合理猜测。
- 👥 **人工三审分工**：事实审、表达审和发布审关注点不同并保留记录。
- 📊 **小样本克制**：用轮换式准实验观察方向，不宣称随机 A/B 或因果结论。
- 🕶️ **公开资产匿名化**：不披露主体名称、联系人和未公开筹备信息。

## 效果展示

### 任务输入卡

```yaml
content_type: 会议报道
source_pack:
  - 议程
  - 已确认讲话要点
  - 公开背景资料
  - 授权图片
term_sheet: [机构全称, 人员姓名与头衔, 固定政策表述]
claims_policy: 不提高原素材的主张强度
reviewers:
  facts: 事实负责人
  language: 编辑负责人
  release: 发布负责人
required_output: [初稿, 引用映射, CHECK清单, 图片署名, 发布检查表]
```

### 可核对输出片段

```markdown
## 活动概况

活动于 [CHECK: 日期] 在 [CHECK: 地点] 举行，围绕“已确认主题”展开。

### 引用映射

- “已确认主题” → source_pack/议程/主题字段
- 发言人姓名与头衔 → term_sheet/人员表
- 参会规模 → [CHECK: 当前素材未提供，不写入正文]
```

### 编辑与审核链

<p align="center">
  <img src="./assets/readme-architecture.svg" alt="机构内容运营中封闭素材、AI 辅助初稿、人工三审、发布和复盘的责任边界流程图" width="100%">
</p>

<p align="center"><sub>可编辑版本：<a href="./assets/readme-architecture.drawio">readme-architecture.drawio</a></sub></p>

## 功能清单

| 资产 | 可复用能力 | 文档 |
|---|---|---|
| 内容定位 | 读者画像、栏目体系、标题规范 | [product-design.md](./product-design.md) |
| 三类模板 | 行业技术交流、专家观点、组织动态 | [product-design.md](./product-design.md) |
| Prompt 工具 | 封闭输入、专名回查、主张约束、待核对输出 | [prompt-engineering.md](./prompt-engineering.md) |
| 生产 SOP | 周节奏、三审分工、发布检查单 | [skills.md](./skills.md) |
| 协作台账 | 多线任务、依赖、风险、待决策项 | [workflows.md](./workflows.md) |
| 运营复盘 | 发布时间 × 图文结构的轮换记录 | [data-analysis.md](./data-analysis.md) |

## 工具与方法栈

| 层级 | 使用方式 |
|---|---|
| 内容工程 | 封闭素材包、专名表、引用映射、`[CHECK]` 清单 |
| Prompt Engineering | 结构模板、事实约束、禁写规则、主张强度检查 |
| 人工治理 | 事实审、表达审、发布审、责任留痕 |
| 运营管理 | 排期 SOP、多线台账、依赖与风险字段 |
| 数据分析 | 轮换式准实验、阅读/分享/互动等方向性指标 |
| 参考实现 | Python 3 标准库；`[CHECK]`、必需专名和禁用表达的发布前预检 |
| 文档表达 | Markdown、YAML、draw.io、SVG、GitHub Alerts |

## 安装与部署

### 获取工作流

```bash
git clone https://github.com/ChrysFu-FndVent/institutional-content-ops.git
cd institutional-content-ops
```

文档无需安装依赖。发布前预检参考实现使用 Python 3.9 或更高版本，不依赖第三方包：

```bash
python3 src/content_guard.py
python3 src/content_guard.py --self-test
```

脚本只发现未解决的 `[CHECK]`、缺失专名和禁用表达，不判断事实真伪，也不会授予发布权限。Markdown 模板仍可直接用于团队知识库、编辑 SOP 或支持结构化 Prompt 的 AI 工具。

### 部署方式

本仓库没有常驻服务。可将 `preflight` 作为本地编辑工具、CI 检查或内容系统提交审核前的同步步骤调用：

```python
from src.content_guard import preflight
```

部署时由调用方传入草稿、必需专名和禁用表达，并保存检查结果。只有脚本检查通过且事实审、表达审、发布审全部完成后，内容才可以进入发布系统；脚本本身不应持有账号发布凭证。

### 一次内容任务的推荐顺序

1. 用 [product-design.md](./product-design.md) 选择读者、栏目和内容模板。
2. 建立封闭素材包、专名表、禁写规则和图片授权清单。
3. 按 [prompt-engineering.md](./prompt-engineering.md) 生成初稿、引用映射和 `[CHECK]` 清单。
4. 依照 [skills.md](./skills.md) 完成事实审、表达审和发布审。
5. 使用 [workflows.md](./workflows.md) 更新任务状态、依赖、风险与待决策项。
6. 将发布数据写入 [data-analysis.md](./data-analysis.md) 的轮换记录，只做多周期方向判断。

> [!TIP]
> 素材包、专名表或最终事实负责人任一缺失时，任务应停在准备阶段。

## 项目结构

```text
institutional-content-ops/
├── README.md              # 工作流入口、使用方式与 FAQ
├── .gitignore             # Python 缓存忽略规则
├── assets/
│   ├── readme-architecture.drawio  # 可编辑责任边界源文件
│   └── readme-architecture.svg     # README 矢量展示图
├── src/
│   └── content_guard.py    # Python 内容发布前预检参考实现
├── workflows.md           # 筹备流程、多线台账与协作节奏
├── skills.md              # 会务与内容生产排期 SOP
├── prompt-engineering.md  # 三类内容 Prompt 与事实约束
├── product-design.md      # 内容定位、栏目与模板规范
└── data-analysis.md       # 轮换式准实验与指标口径
```

## 发布前检查

- [ ] 人物、机构、头衔、时间、地点和数字均能回到素材原文
- [ ] `[CHECK]` 项已解决，或明确从正文中删除
- [ ] 引语、政策表述与数据没有被提高主张强度
- [ ] 图片来源、授权、署名、裁切和替代文本完整
- [ ] 事实审、表达审、发布审均有负责人和记录
- [ ] 内部联系人、未公开节点和敏感筹备信息已移除
- [ ] 发布后的指标记录不被表述为因果结论

## FAQ

<details>
<summary><strong>素材不完整时，AI 能否用公开常识补齐？</strong></summary>

不能默认补齐。缺失信息应标为 `[CHECK]`，由事实负责人提供来源。只有明确加入封闭素材包并允许使用的公开资料，才可以进入正文。
</details>

<details>
<summary><strong>为什么同一篇内容需要三次人工审核？</strong></summary>

三审不是重复检查：事实审确认信息和来源，表达审检查结构、语气和主张强度，发布审检查权限、格式、图片、链接和最终版本。
</details>

<details>
<summary><strong>出现专名错误或身份混淆怎么办？</strong></summary>

停止发布，回到专名表逐项核对，并检查同名人员、历史头衔和简称映射。修正后重新执行事实审，不只改正文中的单个位置。
</details>

<details>
<summary><strong>小样本数据可以用来选择“最佳发布时间”吗？</strong></summary>

不能直接下结论。单账号、非随机样本更适合做多周期轮换观察；内容主题、外部事件和样本量都可能影响结果，应表述为下一轮测试方向。
</details>

<details>
<summary><strong>内容预检脚本通过后可以自动发布吗？</strong></summary>

不可以。脚本只能发现格式化的 `[CHECK]`、缺失专名和配置中的禁用表达，不能验证事实、图片授权、政策语境或发布权限。通过结果只表示可以进入人工三审，不代表允许发布。
</details>

## 可信度与保密边界

- 公开版本保留真实形成的流程和方法，不补写未提供的耗时、差错率或增长数字。
- 企业、机构、账号主体和协作单位均保持匿名。
- 内部筹备数量、联系人、未公开计划和协商信息不进入公开版本。
- AI 不具备发布权限，最终责任由人工审核人与账号负责人承担。

---

<a id="english"></a>

# Institutional Content Operations Workflow

<div align="center">

<strong>Closed-source input · Verifiable drafts · Three-stage human review · Small-sample retrospectives</strong>

![Workflow](https://img.shields.io/badge/Workflow-Human%20in%20the%20Loop-166534?style=flat-square)
![Input](https://img.shields.io/badge/Input-Closed%20Source%20Pack-0369A1?style=flat-square)
![Evidence](https://img.shields.io/badge/Evidence-%5BCHECK%5D-F59E0B?style=flat-square)
![Privacy](https://img.shields.io/badge/Identity-Anonymized-52525B?style=flat-square)
![Language](https://img.shields.io/badge/Language-Python%203-3776AB?style=flat-square&logo=python&logoColor=white)

📋 [Collaboration Ledger](./workflows.md) · ✅ [Execution SOP](./skills.md) · ✍️ [Content Prompts](./prompt-engineering.md) · 📰 [Columns and Templates](./product-design.md) · 📊 [Rotation Review](./data-analysis.md)

</div>

> [!IMPORTANT]
> AI processes only the supplied closed-source material. When a person, institution, title, time, place, number, or policy statement is missing, it must output `[CHECK]`; it must not invent background or strengthen claims beyond the source material.

## Table of Contents

- [Introduction](#introduction)
- [Highlights](#highlights)
- [Example](#example)
- [Capabilities](#capabilities)
- [Tool and Method Stack](#tool-and-method-stack)
- [Installation and Deployment](#installation-and-deployment)
- [Project Structure](#project-structure)
- [Pre-Publication Checklist](#pre-publication-checklist)
- [FAQ](#faq)
- [Credibility and Confidentiality Boundaries](#credibility-and-confidentiality-boundaries)

## Introduction

This repository is a **content-production workflow and prompt toolkit** for institutional public accounts, industry news, conference reports, and first drafts of policy explainers. AI is assigned to organize structure and create a verifiable draft, while factual judgment, editorial restraint, and publication responsibility remain with a three-stage human review.

| Input | Intermediate Artifacts | Output |
|---|---|---|
| Closed source pack, proper-name sheet, content type, publication rules, and review owners | Draft, citation mapping, `[CHECK]` list, and image credits | Three-stage review record, publishable copy, publication checklist, columns, and rotation retrospective |

## Highlights

- 📦 **Closed source pack**: work only from agendas, confirmed talking points, public background, and authorized images.
- 🔖 **Proper-name verification**: check institutions, names, titles, and fixed wording item by item.
- 🧷 **Preserve claim strength**: do not upgrade “planned,” “exploring,” or “may” into “completed,” “leading,” or “will.”
- 🚩 **Make verification gaps explicit**: mark insufficient evidence as `[CHECK]` instead of filling it with plausible guesses.
- 👥 **Three distinct human reviews**: fact, expression, and publication reviews have different focuses and retained records.
- 📊 **Small-sample restraint**: use a rotation-based quasi-experiment to observe direction, without claiming random A/B testing or causality.
- 🕶️ **Anonymized public assets**: do not disclose entity names, contacts, or unpublished preparations.

## Example

### Task Input Card

```yaml
content_type: Conference report
source_pack:
  - Agenda
  - Confirmed talking points
  - Public background material
  - Authorized images
term_sheet: [full institution names, participant names and titles, fixed policy wording]
claims_policy: Do not strengthen claims beyond the source material
reviewers:
  facts: Fact owner
  language: Editorial owner
  release: Publication owner
required_output: [draft, citation mapping, CHECK list, image credits, publication checklist]
```

### Verifiable Output Fragment

```markdown
## Event Overview

The event was held on [CHECK: date] at [CHECK: location] and focused on the “confirmed theme.”

### Citation Mapping

- “Confirmed theme” → source_pack/agenda/theme
- Speaker name and title → term_sheet/people
- Attendance → [CHECK: not present in current material; omit from the body]
```

### Editorial and Review Chain

<p align="center">
  <img src="./assets/readme-architecture.svg" alt="Responsibility-boundary workflow for institutional content operations, from closed materials and AI-assisted drafting through three-stage human review, publication, and retrospective" width="100%">
</p>

<p align="center"><sub>Editable source: <a href="./assets/readme-architecture.drawio">readme-architecture.drawio</a></sub></p>

## Capabilities

| Asset | Reusable Capability | Document |
|---|---|---|
| Content positioning | Reader personas, column system, and headline rules | [product-design.md](./product-design.md) |
| Three template types | Industry/technical exchange, expert viewpoints, and organizational updates | [product-design.md](./product-design.md) |
| Prompt tools | Closed inputs, proper-name verification, claim constraints, and verification flags | [prompt-engineering.md](./prompt-engineering.md) |
| Production SOP | Weekly cadence, three-stage review roles, and publication checklist | [skills.md](./skills.md) |
| Collaboration ledger | Parallel workstreams, dependencies, risks, and pending decisions | [workflows.md](./workflows.md) |
| Operations retrospective | Rotation records for publication time × content structure | [data-analysis.md](./data-analysis.md) |

## Tool and Method Stack

| Layer | Usage |
|---|---|
| Content engineering | Closed source packs, proper-name sheets, citation mapping, and `[CHECK]` lists |
| Prompt Engineering | Structural templates, factual constraints, prohibited wording, and claim-strength checks |
| Human governance | Fact review, expression review, publication review, and accountability records |
| Operations management | Scheduling SOP, parallel-work ledger, dependencies, and risk fields |
| Data analysis | Rotation-based quasi-experiments and directional metrics such as reads, shares, and interactions |
| Reference implementation | Python 3 standard library; publication preflight for `[CHECK]`, required proper names, and prohibited language |
| Documentation | Markdown, YAML, draw.io, SVG, and GitHub Alerts |

## Installation and Deployment

### Get the Workflow

```bash
git clone https://github.com/ChrysFu-FndVent/institutional-content-ops.git
cd institutional-content-ops
```

The documentation has no installation dependencies. The pre-publication checker requires Python 3.9 or later and has no third-party dependencies:

```bash
python3 src/content_guard.py
python3 src/content_guard.py --self-test
```

The script only finds unresolved `[CHECK]` markers, missing proper names, and prohibited expressions. It does not determine factual truth or grant publication permission. Markdown templates can be used directly in a team knowledge base, editing SOP, or AI tool that supports structured prompts.

### Deployment

This repository has no persistent service. `preflight` can be invoked as a local editing tool, a CI check, or a synchronous step before a content system submits a draft for review:

```python
from src.content_guard import preflight
```

The caller supplies the draft, required proper names, and prohibited expressions, then stores the results. Content may enter the publication system only after the script passes and all fact, expression, and publication reviews are complete. The script itself must not hold publishing credentials.

### Recommended Order for One Content Task

1. Use [product-design.md](./product-design.md) to select readers, a column, and a content template.
2. Build the closed source pack, proper-name sheet, prohibited-language rules, and image-authorization list.
3. Use [prompt-engineering.md](./prompt-engineering.md) to produce the draft, citation mapping, and `[CHECK]` list.
4. Complete fact, expression, and publication reviews according to [skills.md](./skills.md).
5. Update task state, dependencies, risks, and pending decisions in [workflows.md](./workflows.md).
6. Add publication data to the rotation record in [data-analysis.md](./data-analysis.md), and use it only for multi-cycle directional judgment.

> [!TIP]
> If the source pack, proper-name sheet, or final fact owner is missing, keep the task in the preparation stage.

## Project Structure

```text
institutional-content-ops/
├── README.md              # Workflow entry point, usage, and FAQ
├── .gitignore             # Python cache ignore rules
├── assets/
│   ├── readme-architecture.drawio  # Editable responsibility-boundary source
│   └── readme-architecture.svg     # README vector diagram
├── src/
│   └── content_guard.py    # Python pre-publication checker reference
├── workflows.md           # Preparation flow, parallel ledger, and collaboration cadence
├── skills.md              # Event and content-production scheduling SOP
├── prompt-engineering.md  # Three content prompts and factual constraints
├── product-design.md      # Content positioning, columns, and template rules
└── data-analysis.md       # Rotation-based quasi-experiment and metric definitions
```

## Pre-Publication Checklist

- [ ] Every person, institution, title, time, place, and number maps back to source material
- [ ] All `[CHECK]` items are resolved or explicitly removed from the body
- [ ] Quotations, policy wording, and data do not strengthen the source claims
- [ ] Image source, authorization, credit, crop, and alternative text are complete
- [ ] Fact, expression, and publication reviews each have an owner and a record
- [ ] Internal contacts, unpublished milestones, and sensitive preparations are removed
- [ ] Post-publication metrics are not presented as causal conclusions

## FAQ

<details>
<summary><strong>Can AI fill gaps with public knowledge when the source material is incomplete?</strong></summary>

Not by default. Missing information must be marked `[CHECK]` and sourced by the fact owner. Only public material explicitly added to the closed source pack and approved for use may enter the text.
</details>

<details>
<summary><strong>Why does the same content require three human reviews?</strong></summary>

They are not duplicate checks. Fact review confirms information and sources; expression review examines structure, tone, and claim strength; publication review verifies permissions, formatting, images, links, and the final version.
</details>

<details>
<summary><strong>What if a proper name is wrong or identities are confused?</strong></summary>

Stop publication, verify every item against the proper-name sheet, and check namesakes, historical titles, and abbreviation mappings. After correction, repeat fact review rather than changing only one occurrence in the draft.
</details>

<details>
<summary><strong>Can a small sample determine the “best publication time”?</strong></summary>

No direct conclusion is justified. A single account with non-random samples is better suited to multi-cycle rotation observations. Topic, external events, and sample size may all affect results, so findings should be stated as directions for the next test.
</details>

<details>
<summary><strong>Can content be published automatically after the preflight script passes?</strong></summary>

No. The script can only find formatted `[CHECK]` markers, missing proper names, and configured prohibited expressions. It cannot verify facts, image rights, policy context, or publication permissions. A passing result means only that the draft may enter the three-stage human review; it does not authorize publication.
</details>

## Credibility and Confidentiality Boundaries

- The public version retains the actual workflow and methods; it does not invent unavailable duration, error-rate, or growth figures.
- Companies, institutions, account owners, and partner organizations remain anonymous.
- Internal preparation counts, contacts, unpublished plans, and negotiation details do not enter the public version.
- AI has no publishing permissions; final responsibility remains with human reviewers and the account owner.

---

<p align="right"><a href="#english">Back to English</a></p>

---
