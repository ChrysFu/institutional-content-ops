# GitHub 同类项目调研与实践提炼

> 调研日与截止日：2026-08-24。活跃窗口为 2025-08-24（含）至 2026-08-24（含）；下文时间均为 UTC。

## 1. 范围与方法

本调研关注两类项目：一是内容治理、编辑检查与发布质量门禁，二是通用工作流编排与自动化。候选项目必须同时满足：

1. 在活跃窗口内存在可核验的提交或 Release；
2. 相关能力能由 GitHub 仓库、官方文档、源码或 Release 直接证明；
3. 至少有一项实践可迁移到本项目的纯 Python 标准库、确定性执行和向后兼容约束中；
4. AI 内容生成不是其主要定位。

从候选集中按“领域相关性、证据质量、实践互补性”精选 8 个项目。Stars 只用于初筛，不作为优点或技术正确性的证据。所有功能判断均引用固定提交的源码/文档；“建议”是基于这些事实对本项目作出的工程推导，不等同于上游项目承诺。

## 2. 当前项目基线

研究开始时，当前项目已经具备一条可靠但偏单文件的内容预检链路：

- `preflight()` 保持简单稳定的 Python 返回契约，能发现 `[CHECK]` 标记、缺失必需词和禁用词，并始终令 `release_approved=false`（[实现](../src/content_guard.py)、[兼容测试](../tests/test_content_guard.py)）。
- CLI 支持 UTF-8 文件或 stdin、严格的 JSON 策略键校验、原子结果写入，以及 `0=正常完成`、`1=内容问题`、`2=系统错误` 的失败关闭语义（[实现](../src/content_guard.py)、[README](../README.md#配置与退出码)）。
- 操作文档已经定义内容状态机、人工终审边界、revision/policy version、幂等原则、失败分类和最小审计字段（[工作流](../workflows.md#五机构内容生产状态机)、[运行手册](operations-runbook.md)）。
- CI 在 Python 3.11–3.14 上执行 Ruff、编译、行为测试、预检 smoke test、JSON/SARIF 示例检查和仓库文档/JSON 校验；Action 固定到 commit，并使用只读权限、超时和并发取消（[Quality workflow](../.github/workflows/quality.yml)）。

本轮更新针对的主要缺口不是“再增加一个关键词规则”，而是把单文件结果提升为可治理的运行结果：稳定规则 ID 与严重级别、目录级确定性发现、每文件与全局汇总、JSON/SARIF、运行级审计元数据，以及系统错误时整批失败关闭。

## 3. 精选项目与活跃性证据

| 项目 | 与本项目的关系 | 窗口内活跃证据 | 许可证 |
|---|---|---|---|
| [Vale](https://github.com/vale-cli/vale) | 面向 prose/markup 的可配置编辑规则引擎 | [v3.18.0](https://github.com/vale-cli/vale/releases/tag/v3.18.0)，2026-08-20；[最新核验提交](https://github.com/vale-cli/vale/commit/d0e65f4187c304b174f9bcb2854f02ebb455708f)，2026-08-21 | [MIT](https://github.com/vale-cli/vale/blob/d0e65f4187c304b174f9bcb2854f02ebb455708f/LICENSE) |
| [textlint](https://github.com/textlint/textlint) | 可插拔自然语言 lint、规则严重级别与机器格式 | [v15.8.0](https://github.com/textlint/textlint/releases/tag/v15.8.0)，2026-08-01；[最新核验提交](https://github.com/textlint/textlint/commit/ca7d1109313bf2bc110647d09ae1de03f650e39a)，2026-08-20 | [MIT](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/LICENSE) |
| [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) | Markdown 批量门禁、配置 schema 与 JSON/SARIF formatter | [最新核验提交](https://github.com/DavidAnson/markdownlint-cli2/commit/b82a6c8896e491b9cb377a99ff3412131920681b)，2026-07-27 | [MIT](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/LICENSE) |
| [reviewdog](https://github.com/reviewdog/reviewdog) | 把多种诊断格式接入代码审查与质量门禁 | [v0.21.0](https://github.com/reviewdog/reviewdog/releases/tag/v0.21.0)，2025-09-03；[最新核验提交](https://github.com/reviewdog/reviewdog/commit/fb20cda1ac47feb047898a6a849bbec4f823df0d)，2026-08-22 | [MIT](https://github.com/reviewdog/reviewdog/blob/fb20cda1ac47feb047898a6a849bbec4f823df0d/LICENSE) |
| [Ruff](https://github.com/astral-sh/ruff) | 稳定规则编码、递归发现、确定输出与 SARIF 参考 | [0.16.4](https://github.com/astral-sh/ruff/releases/tag/0.16.4)，2026-08-20；[最新核验提交](https://github.com/astral-sh/ruff/commit/e84cb8df98b93227f999fd10155a01e11e9efcae)，2026-08-24 | [MIT](https://github.com/astral-sh/ruff/blob/e84cb8df98b93227f999fd10155a01e11e9efcae/LICENSE) |
| [Conftest](https://github.com/open-policy-agent/conftest) | 策略检查、递归批处理、warn/fail 和 JSON/SARIF | [v0.69.0](https://github.com/open-policy-agent/conftest/releases/tag/v0.69.0)，2026-08-03；[最新核验提交](https://github.com/open-policy-agent/conftest/commit/6a3fd606993c1003de444a0ea93c7e916b845d4c)，2026-08-22 | [Apache-2.0 文本](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/LICENSE)（GitHub API 当前返回 `NOASSERTION`） |
| [Argo Workflows](https://github.com/argoproj/argo-workflows) | 显式状态、分类重试、终态处理和幂等缓存原则 | [v4.1.2](https://github.com/argoproj/argo-workflows/releases/tag/v4.1.2)，2026-08-21；[最新核验提交](https://github.com/argoproj/argo-workflows/commit/f016ad89eb269d282aec06dc491c29f396a38df4)，2026-08-21 | [Apache-2.0](https://github.com/argoproj/argo-workflows/blob/f016ad89eb269d282aec06dc491c29f396a38df4/LICENSE) |
| [Prefect](https://github.com/PrefectHQ/prefect) | Python 工作流的状态、恢复、事务与事件审计原则 | [3.8.3](https://github.com/PrefectHQ/prefect/releases/tag/3.8.3)，2026-08-13；[最新核验提交](https://github.com/PrefectHQ/prefect/commit/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98)，2026-08-21 | [Apache-2.0](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/LICENSE) |

## 4. 各项目可取之处

### 4.1 Vale：编辑规则应有稳定身份、范围和级别

Vale 将规则与 prose 的结构语义结合，而非把所有 markup 当纯文本；其 README 明确列出 markup 感知和自定义 style 扩展能力（[README](https://github.com/vale-cli/vale/blob/d0e65f4187c304b174f9bcb2854f02ebb455708f/README.md#L83-L91)）。配置模型保存 `MinAlertLevel`、单规则级别和按语法级别覆盖，CLI 同时提供 glob、最小告警级别、排序和路径规范化选项（[配置结构](https://github.com/vale-cli/vale/blob/d0e65f4187c304b174f9bcb2854f02ebb455708f/internal/core/config.go#L135-L185)、[CLI flags](https://github.com/vale-cli/vale/blob/d0e65f4187c304b174f9bcb2854f02ebb455708f/cmd/vale/flag.go#L14-L45)）。

**可迁移精华**：给当前三类内建检查分配长期稳定的规则 ID，并把“是否展示”和“是否阻断”从 message 文案中分离；目录结果按规范化相对路径和规则 ID 排序，保证重复运行可比较。

### 4.2 textlint：诊断数据契约与退出语义分离

textlint 的规则配置支持 `error`、`warning`、`info`；warning/info 不导致错误退出（[配置文档](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/docs/configuring.md#L135-L161)）。formatter 契约明确包含 `filePath`、`ruleId`、`message` 和 `severity`，提供 JSON 与 GitHub Actions annotation 输出（[formatter 文档](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/docs/formatter.md#L8-L66)、[JSON/GitHub formatter](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/docs/formatter.md#L97-L220)）。其 CLI 还明确区分 lint findings（1）与文件发现/输出错误（2）（[退出码文档](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/docs/faq/exit-status.md#L8-L21)）。

**可迁移精华**：保留当前 `0/1/2` 语义，同时让每条 finding 自带 rule ID、severity、path 和 message；阈值决定退出码，序列化格式不改变门禁判断。

### 4.3 markdownlint-cli2：配置和报告也是公共契约

markdownlint-cli2 接受多个 glob，支持目录级配置覆盖，并用 JSON Schema 约束配置（[README](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/README.md)、[配置 schema](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/schema/markdownlint-cli2-config-schema.json)）。它把 `0=无错误`、`1=发现 lint error`、`2=工具失败` 写成 CLI 契约（[退出码](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/README.md#exit-codes)）。同仓库的独立 formatter 包分别定义包含文件、行、规则 ID/别名和 severity 的 JSON，以及带 rules、`ruleId`、level、location 和帮助链接的 SARIF 2.1.0（[JSON formatter](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/formatter-json/README.md)、[SARIF formatter](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/formatter-sarif/README.md)）。

**可迁移精华**：对 policy 和报告格式做严格、可测试的 schema 约束；扫描核心与 formatter 解耦。其 JSON/SARIF 是独立包而非 CLI 核心默认输出，本项目应借鉴边界，不应误称为单一内建通道。

### 4.4 reviewdog：一次规范化，多处消费

reviewdog 接受 errorformat、Checkstyle、RDJSON/RDJSONL 和 SARIF 2.1.0，再把规范化诊断送往 PR review、check 或 annotation（[输入格式](https://github.com/reviewdog/reviewdog/blob/fb20cda1ac47feb047898a6a849bbec4f823df0d/README.md#L156-L312)）。其配置为不同工具保留 `name`、`format` 与 `level`，GitHub check 状态又能按级别映射为 neutral/failure（[配置与门禁](https://github.com/reviewdog/reviewdog/blob/fb20cda1ac47feb047898a6a849bbec4f823df0d/README.md#L338-L418)）。

**可迁移精华**：内部只维护一个 canonical finding/scan model，JSON 和 SARIF 都从该模型生成；不要为每种输出格式各写一套扫描逻辑。

### 4.5 Ruff：显式规则集、确定性发现和标准 SARIF

Ruff 的规则使用稳定代码（如 `F401`），并建议从显式小规则集开始，避免升级时因隐式 `ALL` 自动引入新门禁（[规则选择](https://docs.astral.sh/ruff/linter/#rule-selection)）。它接受文件或目录，目录会递归发现目标，并明确处理 include/exclude 与 Git ignore（[lint 输入](https://docs.astral.sh/ruff/linter/)、[文件发现配置](https://docs.astral.sh/ruff/configuration/#config-file-discovery)）。Ruff 的 SARIF emitter 固定输出 SARIF 2.1.0，去重并排序 rule metadata，再把诊断映射到 `ruleId`、level、location 和 message（[SARIF 源码](https://github.com/astral-sh/ruff/blob/e84cb8df98b93227f999fd10155a01e11e9efcae/crates/ruff_linter/src/message/sarif.rs#L17-L89)）；其 CLI 把 findings 与异常退出分开（[退出码](https://docs.astral.sh/ruff/linter/#exit-codes)）。

**可迁移精华**：扫描文件集和结果都稳定排序；SARIF `driver.rules` 去重，`results[].ruleId` 与规则表一致；用户显式选择扩展名/排除项，默认规则升级不暗中扩大阻断面。

### 4.6 Conftest：批量策略评估与多消费者报告

Conftest 对目录递归查找支持的文件，并允许正则 ignore；warning 与 failure 分开，`--fail-on-warn` 可调整门禁（[目录、ignore 与门禁](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/docs/options.md#L155-L171)）。同一结果可输出 JSON、JUnit、GitHub、Azure DevOps 或 SARIF；SARIF 示例包含 tool、rules、invocation、ruleId、level 和 location（[输出文档](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/docs/output.md#L1-L83)）。它还向策略提供当前文件名/目录等上下文，JSON 可保留额外 metadata（[输入上下文与 metadata](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/docs/index.md#L75-L83)、[结构化结果](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/docs/index.md#L111-L141)）。

**可迁移精华**：目录扫描应返回每文件结果和总汇总；审计元数据属于 run envelope，不污染单文件 `preflight()` 兼容返回值；报告需保留工具执行成功与否。

### 4.7 Argo Workflows：只重试可恢复故障，终态处理总要执行

Argo 将 retry policy 与条件表达式组合，区分 application failure、controller error 和 transient error，并支持重试上限与 backoff（[重试文档](https://github.com/argoproj/argo-workflows/blob/f016ad89eb269d282aec06dc491c29f396a38df4/docs/retries.md#L1-L123)）。`onExit` 无论成功或失败都会执行，可用于清理、通知和发布最终状态（[exit handlers](https://github.com/argoproj/argo-workflows/blob/f016ad89eb269d282aec06dc491c29f396a38df4/docs/walk-through/exit-handlers.md#L1-L40)）。memoization 通过输入相关 key 和有效期复用纯步骤结果，并明确提示有外部副作用的步骤不满足“纯步骤”假设（[memoization](https://github.com/argoproj/argo-workflows/blob/f016ad89eb269d282aec06dc491c29f396a38df4/docs/memoization.md#L1-L50)）。

**可迁移精华**：内容 findings 不重试；文件读写等系统错误失败关闭；运行结束始终生成审计摘要；未来缓存必须用内容 hash + policy version 作为 key，且不得缓存发布副作用。

### 4.8 Prefect：状态、事务与事件顺序是不同问题

Prefect 区分 Completed、Failed、Crashed、Paused、Retrying 等状态，并指出 state type 驱动编排、state name 用于可读记录（[状态模型](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/concepts/states.mdx#L8-L59)）。它支持任务级重试、退避、jitter 与条件重试（[重试策略](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/how-to-guides/workflows/retries.mdx#L8-L112)）。事务文档把 BEGIN/STAGE/ROLLBACK/COMMIT、唯一 key 和幂等性分开说明（[事务生命周期](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/advanced/transactions.mdx#L56-L139)）；状态 hook 文档还指出进程内 hook 不保证执行，以及关联事件需显式因果引用才能确定顺序（[hook 可靠性与事件顺序](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/how-to-guides/workflows/state-change-hooks.mdx#L34-L121)）。

**可迁移精华**：审计元数据至少区分 run ID、开始/结束时间、工具状态、输入 hash 和 policy hash；“检查完成”“检查通过”“人工批准发布”必须是不同状态，不能因报告生成成功而混为一谈。

## 5. 综合最佳实践

把上述项目的共同做法压缩到当前仓库，可形成六条设计原则：

1. **稳定身份优先于可读文案**：规则 ID 是筛选、基线、SARIF 和历史统计的主键；message 可演进，ID 不随措辞变化。
2. **严重级别与门禁阈值分离**：finding 记录自己的 severity，调用方决定 warning 是否阻断；格式选择不改变退出码。
3. **先统一模型，再增加输出**：单文件与批量扫描共同产出 canonical findings；JSON、SARIF、stdout 只是适配层。
4. **确定性是审计能力**：路径正规化、文件集排序、finding 排序、规则表去重排序、固定字段与 UTC 时间格式，使相同输入和策略能稳定比较。含当前时间的审计字段本身不要求字节完全一致。
5. **内容失败与系统失败严格分层**：内容问题可汇总返回；文件发现、解码、策略、报告写入或内部异常应使整次 run `execution_successful=false` 并返回系统错误，不能产出“部分通过”的误导结论。
6. **自动化止于人工审阅入口**：`ready_for_human_review` 只表示自动规则未阻断；`release_approved` 永远不能由扫描器置为 true。

### 建议的最小数据流

```text
输入路径 + 策略
  -> 确定性文件发现 / 严格配置校验
  -> 逐文件复用 preflight 核心规则
  -> canonical findings（rule_id / severity / path / message）
  -> run envelope（run_id / timestamps / hashes / totals / execution status）
  -> JSON 或 SARIF 2.1.0 adapter
  -> 原子写入 + 0/1/2 退出码
```

## 6. 不应照搬的部分

- **不引入完整 plugin/package 生态**：Vale/textlint 的生态适合跨团队扩展，但本项目只有少量确定性规则；动态加载第三方代码会扩大供应链、版本和配置风险。先用内部规则注册表即可。
- **不引入 OPA/Rego、Node、Rust 或 Kubernetes 控制面**：Conftest、Ruff、Argo 的运行时解决的是更大规模问题；本项目可提取数据契约、输出和重试原则，而无需复制技术栈。
- **不构建工作流服务和数据库**：Prefect/Argo 的调度、分布式状态与 UI 超出仓库定位。扫描器保持无状态，持久化由调用方负责。
- **不默认扫描所有文本格式**：markup-aware parser 是 Vale/textlint 的核心优势，当前纯标准库实现没有等价 AST。首版只接受明确扩展名，避免把代码块、二进制或生成文件误报为正文。
- **不自动修复机构内容**：格式化器的 fix 模型不适用于事实、授权、头衔和合规判断；工具只能报告与阻断，不能代替编辑决定。
- **不为缓存牺牲可解释性**：在 policy version/hash、内容 hash 和工具版本未进入 key 前，不实现缓存；外部发布动作永不缓存。

## 7. 分阶段更新建议

### Now：本轮已实现

| 优先级 | 建议 | 验收要点 | 来源启发 |
|---:|---|---|---|
| P0 | 在不改变 `preflight()` 既有键和值的前提下，增加独立 canonical finding 映射 | 旧测试逐字通过；规则 ID 稳定；每条 finding 有 severity/path/message | Vale、textlint、Ruff |
| P0 | 新增目录批量扫描，限定 `.md`/`.txt` 扩展名 | 文件和结果稳定排序；空批次或任一系统错误令整批失败关闭 | Ruff、Conftest |
| P0 | 增加 JSON batch report 与 SARIF 2.1.0 adapter | 两种格式来自同一模型；result ruleId 可解析；finding 带行列位置 | reviewdog、Ruff、Conftest |
| P0 | 增加确定性 audit envelope | 包含 scan ID、content ID、revision、policy version/hash、文档 hash 和 severity totals；不包含正文 | Conftest、Prefect |
| P0 | 保持退出码兼容并按 severity 门禁 | 0=正常完成，1=启用 `--fail-on-issues` 且存在 error，2=系统/配置/输出错误；`release_approved=false` | textlint、Ruff |
| P1 | 为批处理、系统错误、稳定排序、JSON/SARIF schema 核心字段与向后兼容增加测试 | Python 3.11–3.14 行为一致；同一 fixture 在多次运行中除 run/time 外结果稳定 | Ruff、Conftest |

### Roadmap：完成首版后再评估

1. **策略版本与规则 registry**：策略显式声明 schema version；规则定义集中管理 ID、默认级别、描述和帮助 URI。先有迁移策略，再开放规则开关。
2. **窄范围例外机制**：例外必须绑定 rule ID、相对路径、原因和到期日；过期或未知规则的例外使配置失败，避免永久静默忽略。
3. **差异扫描**：在 CI 中只展示改动行的诊断，但全量扫描仍作为真值，避免已有问题掩盖新问题；可参考 reviewdog 的 diff filter 思路。
4. **GitHub Code Scanning 上传**：在无敏感正文泄漏、SARIF 路径正确且权限最小化后，增加可选上传 job；SARIF artifact 仍应保留供本地审计。
5. **内容感知解析**：仅在误报数据证明必要时，为 Markdown code fence/front matter 增加轻量解析；不要用正则冒充完整 Markdown AST。
6. **基于 hash 的增量缓存**：key 至少包含内容 hash、policy hash、工具 schema/version 和规则集；缓存仅用于纯扫描结果，且有显式失效规则。
7. **运行事件与持久化接口**：若未来接入外部台账，为 started/completed/failed 事件增加因果 ID；扫描器本身仍不承担审批状态持久化。
8. **排除模式与门禁阈值**：在有真实目录误报或不同渠道准入需求后，再增加显式 exclude 与 `fail-on` 阈值；默认行为继续保持兼容。

## 8. 一手来源索引

### 当前项目

- [内容预检实现](../src/content_guard.py)
- [内容预检兼容测试](../tests/test_content_guard.py)
- [仓库检查实现](../src/repository_checks.py)
- [Quality workflow](../.github/workflows/quality.yml)
- [内容状态机与审计字段](../workflows.md#五机构内容生产状态机)
- [Operations runbook](operations-runbook.md)

### 对标项目

- Vale：[固定提交](https://github.com/vale-cli/vale/commit/d0e65f4187c304b174f9bcb2854f02ebb455708f)、[README](https://github.com/vale-cli/vale/blob/d0e65f4187c304b174f9bcb2854f02ebb455708f/README.md)、[配置源码](https://github.com/vale-cli/vale/blob/d0e65f4187c304b174f9bcb2854f02ebb455708f/internal/core/config.go)、[CLI flags](https://github.com/vale-cli/vale/blob/d0e65f4187c304b174f9bcb2854f02ebb455708f/cmd/vale/flag.go)、[v3.18.0](https://github.com/vale-cli/vale/releases/tag/v3.18.0)
- textlint：[固定提交](https://github.com/textlint/textlint/commit/ca7d1109313bf2bc110647d09ae1de03f650e39a)、[配置](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/docs/configuring.md)、[formatter](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/docs/formatter.md)、[退出码](https://github.com/textlint/textlint/blob/ca7d1109313bf2bc110647d09ae1de03f650e39a/docs/faq/exit-status.md)、[v15.8.0](https://github.com/textlint/textlint/releases/tag/v15.8.0)
- markdownlint-cli2：[固定提交](https://github.com/DavidAnson/markdownlint-cli2/commit/b82a6c8896e491b9cb377a99ff3412131920681b)、[CLI 与退出码](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/README.md)、[配置 schema](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/schema/markdownlint-cli2-config-schema.json)、[JSON formatter](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/formatter-json/README.md)、[SARIF formatter](https://github.com/DavidAnson/markdownlint-cli2/blob/b82a6c8896e491b9cb377a99ff3412131920681b/formatter-sarif/README.md)
- reviewdog：[固定提交](https://github.com/reviewdog/reviewdog/commit/fb20cda1ac47feb047898a6a849bbec4f823df0d)、[输入格式、配置与门禁](https://github.com/reviewdog/reviewdog/blob/fb20cda1ac47feb047898a6a849bbec4f823df0d/README.md)、[v0.21.0](https://github.com/reviewdog/reviewdog/releases/tag/v0.21.0)
- Ruff：[固定提交](https://github.com/astral-sh/ruff/commit/e84cb8df98b93227f999fd10155a01e11e9efcae)、[linter 文档](https://docs.astral.sh/ruff/linter/)、[配置与文件发现](https://docs.astral.sh/ruff/configuration/)、[SARIF emitter](https://github.com/astral-sh/ruff/blob/e84cb8df98b93227f999fd10155a01e11e9efcae/crates/ruff_linter/src/message/sarif.rs)、[0.16.4](https://github.com/astral-sh/ruff/releases/tag/0.16.4)
- Conftest：[固定提交](https://github.com/open-policy-agent/conftest/commit/6a3fd606993c1003de444a0ea93c7e916b845d4c)、[策略与上下文](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/docs/index.md)、[批量与门禁选项](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/docs/options.md)、[JSON/SARIF 输出](https://github.com/open-policy-agent/conftest/blob/6a3fd606993c1003de444a0ea93c7e916b845d4c/docs/output.md)、[v0.69.0](https://github.com/open-policy-agent/conftest/releases/tag/v0.69.0)
- Argo Workflows：[固定提交](https://github.com/argoproj/argo-workflows/commit/f016ad89eb269d282aec06dc491c29f396a38df4)、[重试](https://github.com/argoproj/argo-workflows/blob/f016ad89eb269d282aec06dc491c29f396a38df4/docs/retries.md)、[exit handler](https://github.com/argoproj/argo-workflows/blob/f016ad89eb269d282aec06dc491c29f396a38df4/docs/walk-through/exit-handlers.md)、[memoization](https://github.com/argoproj/argo-workflows/blob/f016ad89eb269d282aec06dc491c29f396a38df4/docs/memoization.md)、[v4.1.2](https://github.com/argoproj/argo-workflows/releases/tag/v4.1.2)
- Prefect：[固定提交](https://github.com/PrefectHQ/prefect/commit/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98)、[状态](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/concepts/states.mdx)、[重试](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/how-to-guides/workflows/retries.mdx)、[事务与幂等](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/advanced/transactions.mdx)、[state hooks 与事件顺序](https://github.com/PrefectHQ/prefect/blob/ce79dd3d6cfa2b7337265498210dbc4d25bcdc98/docs/v3/how-to-guides/workflows/state-change-hooks.mdx)、[3.8.3](https://github.com/PrefectHQ/prefect/releases/tag/3.8.3)
