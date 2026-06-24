from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseModel):
    db_path: Path = ROOT / "data" / "normalized" / "vc_research.sqlite"
    output_dir: Path = ROOT / "data" / "output"
    template_dir: Path = ROOT / "templates"
    as_of_date: str | None = None


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML must be a mapping: {path}")
    return loaded


def load_settings() -> Settings:
    project = load_yaml(ROOT / "config" / "project.yaml")
    output = project.get("output", {})
    return Settings(
        db_path=Path(os.getenv("VC_RESEARCH_DB", ROOT / "data" / "normalized" / "vc_research.sqlite")),
        output_dir=Path(os.getenv("VC_RESEARCH_OUTPUT_DIR", ROOT / "data" / "output")),
        as_of_date=output.get("as_of_date"),
    )
