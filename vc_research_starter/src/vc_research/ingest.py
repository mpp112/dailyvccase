from __future__ import annotations

import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from vc_research.models import Candidate
from vc_research.models.core import stable_id
from vc_research.normalize import event_key, split_names
from vc_research.storage import SQLiteStore


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, list):
            raise ValueError("candidate JSON must be a list")
        return [dict(item) for item in loaded]
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_to_candidate(row: dict[str, Any]) -> Candidate:
    announcement = date.fromisoformat(str(row["announcement_date"]))
    discovered_raw = row.get("discovered_at")
    discovered = (
        datetime.fromisoformat(str(discovered_raw).replace("Z", "+00:00"))
        if discovered_raw
        else datetime.now(timezone.utc)
    )
    if discovered.tzinfo is None:
        discovered = discovered.replace(tzinfo=timezone.utc)
    company = str(row["company_name"])
    return Candidate(
        candidate_id=str(row.get("candidate_id") or stable_id("cand", company, announcement, row["round_raw"])),
        discovered_at=discovered,
        company_name=company,
        country=str(row["country"]),
        sector=str(row.get("sector") or "Unknown"),
        round_raw=str(row["round_raw"]),
        amount_raw=row.get("amount_raw") or None,
        currency=row.get("currency") or None,
        lead_investors=split_names(row.get("lead_investors")),
        announcement_date=announcement,
        source_url=str(row["source_url"]),
        source_tier=int(row.get("source_tier") or 2),
        score=float(row.get("score") or 0),
        status=str(row.get("status") or "discovered"),
        notes=row.get("notes") or None,
    )


def import_candidates(path: Path, store: SQLiteStore) -> dict[str, int]:
    created = 0
    updated = 0
    rows = _load_rows(path)
    for row in rows:
        candidate = row_to_candidate(row)
        key = event_key(
            candidate.company_name,
            candidate.announcement_date,
            candidate.round_raw,
            candidate.amount_raw,
        )
        if store.upsert_candidate(candidate, key):
            created += 1
        else:
            updated += 1
    return {"created": created, "updated": updated, "total": len(rows)}
