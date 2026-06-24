# 运行手册

## 安装

```bash
python -m pip install -e ".[dev]"
```

## 每日最小流程

```bash
vc-research init-db
vc-research import-candidates data/raw/fixture_candidates.csv
vc-research score-candidates
vc-research seed-fixture-cases
vc-research validate --case-id case_pass
vc-research render --case-id case_pass
vc-research weekly-review --week 2026-W26
```

## 质量检查

```bash
python -m ruff format .
python -m ruff check .
python -m mypy src/vc_research
python -m pytest
```
