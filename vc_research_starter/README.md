# 海外 VC 案例研究工作台 MVP

这是一个 provenance-first 的 VC 案例研究工作台：先结构化事实、来源和 Claim-Evidence，再做中国对标、融资历史、QA 和中文 Markdown 报告渲染。

## 安装

```bash
python -m pip install -e ".[dev]"
```

## 每日最小操作

```bash
vc-research init-db
vc-research import-candidates data/raw/fixture_candidates.csv
vc-research score-candidates
vc-research seed-fixture-cases
vc-research validate --case-id case_pass
vc-research render --case-id case_pass
vc-research weekly-review --week 2026-W26
```

渲染结果默认写入 `data/output/case_pass.md`。

## 当前实现

- 融资候选 CSV/JSON 导入、幂等去重和评分。
- Company、FinancingEvent、Investor、Source、Claim、Comparable、FinancingHistory 数据模型。
- Claim-Evidence 可信度和来源绑定。
- 中国对标六维评分与 direct/adjacent/reference 分类。
- 融资历史和投资机构主体映射字段。
- 确定性 QA 红线规则。
- 中文 Markdown 日报渲染，包含 `as_of_date` 和来源清单。
- 三个完全虚构 fixture：通过、金额冲突失败、低分直接对标失败。
- 单元测试和端到端 smoke test。

## Fixture QA 预期

```bash
vc-research seed-fixture-cases
vc-research validate --case-id case_pass
vc-research validate --case-id case_conflict
vc-research validate --case-id case_low_comparable
```

- `case_pass`：应通过。
- `case_conflict`：应因关键金额低可信度和来源冲突失败。
- `case_low_comparable`：应因低于 75 分却标为直接对标失败。

## 质量检查

完成前必须实际运行：

```bash
python -m ruff format .
python -m ruff check .
python -m mypy src/vc_research
python -m pytest
```

## 真实数据源待接入

当前没有真实 API 凭证，也不抓取登录、验证码或付费页面，因此只实现 adapter 预留、手工 CSV/JSON 和 fixture。后续可接入：

- SEC EDGAR / Form D 官方公开数据；
- Companies House 官方 API；
- 公司官网、投资机构官网、公开 RSS；
- 授权商业数据库导出 CSV。

所有接入都必须保留 Source 元数据，不伪造 API 返回，不绕过访问控制。

## 原始启动包说明

目标：每个工作日产出一份可追溯的海外 VC 投资案例研究，覆盖：

1. 最新融资事实；
2. 海外标的基础研究；
3. 投资逻辑与关键假设；
4. 中国直接/邻近对标；
5. 中国对标公司的融资历史与投资机构；
6. 中外市场适用性判断；
7. 逐条证据、质量检查与后续追踪。

## 使用顺序

1. 阅读 `START_HERE.md`，确定行业、地区、阶段和发布时间窗口。
2. 修改 `config/project.yaml`。
3. 将整个文件夹初始化为 Git 仓库，并在 Codex 中打开。
4. 把 `prompts/CODEX_BOOTSTRAP_PROMPT.md` 全文交给 Codex。
5. Codex 完成后，先运行 3 个样例案例；人工验收通过后，再接入定时采集。

## 文件说明

- `START_HERE.md`：整体 Plan、里程碑和日/周/月节奏。
- `SOP.md`：单个案例从发现到发布的标准作业流程。
- `DATA_SOURCES.md`：数据源分级、采集方式和合规边界。
- `DATA_MODEL.md`：结构化数据模型与证据模型。
- `ACCEPTANCE.md`：验收标准、评分卡和红线。
- `AGENTS.md`：Codex 在本仓库长期遵循的规则。
- `.agents/skills/`：三个可复用 Codex Skills 草案。
- `prompts/CODEX_BOOTSTRAP_PROMPT.md`：首次初始化代码库的完整提示词。
- `templates/`：文章、候选池、融资历史和证据日志模板。
- `config/`：项目范围、数据源、质量门槛和分类体系。
- `schemas/`：案例与证据 JSON Schema。

## MVP 的边界

第一版只做“半自动研究台”，不做无人审核的自动发布：

- 自动：RSS/API/公开页面发现、去重、结构化、评分、模板渲染、规则检查。
- 半自动：对标候选、投资逻辑草稿、来源冲突提示。
- 人工：关键数字核验、直接对标确认、最终观点、发布审批。

商业数据库、登录页面、验证码页面和付费内容只允许人工录入或使用官方授权 API，不绕过访问控制。
