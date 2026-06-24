# 架构说明

MVP 采用 Python 3.11、Pydantic、Typer、SQLite 和 Jinja2。当前环境无法稳定创建 `docs/` 目录，因此本文件暂放仓库根路径；内容等价于 `docs/ARCHITECTURE.md`。

## 分层

- `data/raw/`：手工 CSV/JSON、公开适配器原始输入和 fixture。
- `data/normalized/`：SQLite MVP 数据库。
- `data/output/`：渲染后的中文 Markdown。
- `src/vc_research/models/`：公司、融资事件、投资人、来源、Claim、对标、融资历史和 QA 模型。
- `src/vc_research/ingest.py`：候选导入与幂等去重。
- `src/vc_research/qa.py`：确定性红线规则。
- `src/vc_research/rendering.py`：中文备忘录渲染。

## 设计取舍

为避免在无凭证环境中伪造 API，当前仅实现 fixture 和手工 CSV/JSON 适配器。未来接入 SEC、Companies House 等官方 API 时，应新增 adapter，并保持 Source 元数据、content hash 和访问边界记录。
