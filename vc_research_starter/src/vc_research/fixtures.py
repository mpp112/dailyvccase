from __future__ import annotations

from pathlib import Path

from vc_research.models import CaseRecord
from vc_research.storage import SQLiteStore


def load_fixture_case(path: Path) -> CaseRecord:
    return CaseRecord.model_validate_json(path.read_text(encoding="utf-8"))


def seed_fixtures(fixtures_dir: Path, store: SQLiteStore) -> list[str]:
    case_ids: list[str] = []
    for path in sorted(fixtures_dir.glob("case_*.fixture.json")):
        case = load_fixture_case(path)
        store.save_case(case)
        case_ids.append(case.case_id)
    return case_ids
