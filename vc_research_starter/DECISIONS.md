# 决策记录

- 使用 SQLite 作为 MVP 主存储，记录候选和完整 case JSON，后续可迁移到关系化表。
- 无真实凭证时只提供手工 CSV/JSON 与 fixture，不伪造任何 API 成功结果。
- fixture 全部使用 `fixture.local` 和明确的 `FICTIONAL FIXTURE` 标记。
- QA 先覆盖验收红线中可确定性执行的规则，人工研究质量评分保留为后续扩展。
- 当前沙箱无法稳定创建 `docs/` 与 `fixtures/` 目录，因此文档暂在根路径，fixture 放在已有 `data/raw/`。
