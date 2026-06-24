from __future__ import annotations

from datetime import date

from vc_research.models import CaseRecord


def weekly_review_rows(cases: list[CaseRecord], week: str) -> list[dict[str, str]]:
    return [
        {
            "week": week,
            "case_id": case.case_id,
            "company": case.foreign_company.brand_name,
            "status": case.status,
            "as_of_date": case.as_of_date.isoformat(),
            "generated_at": date.today().isoformat(),
        }
        for case in cases
    ]
