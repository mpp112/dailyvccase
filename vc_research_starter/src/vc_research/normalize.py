from __future__ import annotations

import re
from datetime import date

from vc_research.models.core import stable_id


LEGAL_SUFFIXES = {
    "inc",
    "inc.",
    "ltd",
    "ltd.",
    "limited",
    "corp",
    "corp.",
    "corporation",
    "co",
    "co.",
    "company",
}


def normalize_company_name(name: str) -> str:
    value = re.sub(r"\s+", " ", name.strip().lower())
    value = re.sub(r"[，,。.;；:：()（）]", " ", value)
    return " ".join(part for part in value.split() if part not in LEGAL_SUFFIXES)


def split_names(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in re.split(r"[;；|,，]", value) if part.strip()]


def event_key(company_name: str, announcement_date: date, round_raw: str, amount_raw: str | None) -> str:
    return stable_id(
        "event",
        normalize_company_name(company_name),
        announcement_date.isoformat(),
        round_raw,
        amount_raw or "undisclosed",
    )
