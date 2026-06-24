from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from pydantic import TypeAdapter

from vc_research.models import Candidate, CaseRecord


class SQLiteStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS candidates "
                "(candidate_id TEXT PRIMARY KEY, event_key TEXT UNIQUE NOT NULL, payload TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS cases "
                "(case_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )

    def upsert_candidate(self, candidate: Candidate, key: str) -> bool:
        with self.connect() as conn:
            existing = conn.execute("SELECT candidate_id FROM candidates WHERE event_key=?", (key,)).fetchone()
            conn.execute(
                "INSERT INTO candidates(candidate_id,event_key,payload) VALUES(?,?,?) "
                "ON CONFLICT(event_key) DO UPDATE SET payload=excluded.payload",
                (candidate.candidate_id, key, candidate.model_dump_json()),
            )
        return existing is None

    def list_candidates(self) -> list[Candidate]:
        adapter = TypeAdapter(Candidate)
        with self.connect() as conn:
            rows = conn.execute("SELECT payload FROM candidates ORDER BY candidate_id").fetchall()
        return [adapter.validate_python(json.loads(row["payload"])) for row in rows]

    def save_case(self, case: CaseRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO cases(case_id,payload) VALUES(?,?) "
                "ON CONFLICT(case_id) DO UPDATE SET payload=excluded.payload",
                (case.case_id, case.model_dump_json()),
            )

    def get_case(self, case_id: str) -> CaseRecord:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM cases WHERE case_id=?", (case_id,)).fetchone()
        if row is None:
            raise KeyError(f"case not found: {case_id}")
        return CaseRecord.model_validate_json(row["payload"])

    def list_cases(self) -> list[CaseRecord]:
        with self.connect() as conn:
            rows = conn.execute("SELECT payload FROM cases ORDER BY case_id").fetchall()
        return [CaseRecord.model_validate_json(row["payload"]) for row in rows]
