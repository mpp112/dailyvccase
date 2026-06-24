from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from vc_research.config import ROOT
from vc_research.models import CaseRecord, QAReport


def render_daily_memo(case: CaseRecord, qa_report: QAReport, output_dir: Path) -> Path:
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(default_for_string=False, default=False),
    )
    template = env.get_template("daily_memo.md")
    primary = case.china_comparables[0] if case.china_comparables else None
    source_list = "\n".join(
        f"- [{source.source_id}] {source.title} ({source.publisher}, Tier {source.tier}) {source.url}"
        for source in case.sources
    )
    evidence_by_topic = {
        topic: ", ".join(claim.claim_id for claim in case.claims if claim.topic == topic) or "待补充"
        for topic in ["company", "country", "round", "amount", "investors", "date"]
    }
    markdown = template.render(
        case_number=case.case_id,
        foreign_company=case.foreign_company,
        headline_thesis=case.headline_thesis,
        as_of_date=case.as_of_date.isoformat(),
        qa_status="通过" if qa_report.passed else "未通过",
        deal=case.deal,
        evidence=evidence_by_topic,
        primary_china_comparable={
            "name": primary.china_company.brand_name if primary else "暂无",
            "type": primary.comparison_type if primary else "reference",
            "score": primary.total_score if primary else 0,
        },
        source_list=source_list,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{case.case_id}.md"
    path.write_text(markdown, encoding="utf-8")
    return path
