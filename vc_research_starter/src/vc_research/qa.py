from __future__ import annotations

from vc_research.models import CaseRecord, QAFinding, QAReport


CRITICAL_TOPICS = {"amount", "round", "investors", "announcement_date", "company"}


def validate_case(case: CaseRecord, rendered_markdown: str | None = None) -> QAReport:
    findings: list[QAFinding] = []

    for claim in case.claims:
        if claim.claim_type not in {"F", "S", "H"}:
            findings.append(
                QAFinding(
                    rule_id="fact_signal_hypothesis_not_separated",
                    severity="redline",
                    message="Claim missing F/S/H type.",
                    entity_id=claim.claim_id,
                    suggested_fix="Set claim_type to F, S, or H.",
                )
            )
        if claim.claim_type == "F" and not claim.source_ids:
            findings.append(
                QAFinding(
                    rule_id="critical_claim_missing_source",
                    severity="redline",
                    message="Fact claim has no source.",
                    entity_id=claim.claim_id,
                    suggested_fix="Bind at least one source_id.",
                )
            )
        if claim.topic in CRITICAL_TOPICS and claim.confidence not in {"A", "B"}:
            findings.append(
                QAFinding(
                    rule_id="critical_fact_below_b",
                    severity="redline",
                    message="Critical transaction fact is below B confidence.",
                    entity_id=claim.claim_id,
                    suggested_fix="Add Tier-1 evidence or two independent Tier-2 sources.",
                )
            )
        if claim.conflict_status in {"possible", "confirmed"}:
            findings.append(
                QAFinding(
                    rule_id="unresolved_critical_source_conflict",
                    severity="redline",
                    message="Source conflict is unresolved.",
                    entity_id=claim.claim_id,
                    suggested_fix="Preserve both sources and mark conflict resolved only after review.",
                )
            )

    if case.deal.amount_original is not None and not case.deal.currency_original:
        findings.append(
            QAFinding(
                rule_id="amount_missing_original_currency",
                severity="redline",
                message="Deal amount exists but original currency is missing.",
                entity_id=case.deal.event_id,
                suggested_fix="Store the original ISO currency or leave amount undisclosed.",
            )
        )

    if case.deal.cumulative_funding is not None and case.deal.amount_original == case.deal.cumulative_funding:
        findings.append(
            QAFinding(
                rule_id="round_amount_cumulative_valuation_confusion",
                severity="warning",
                message="Round amount equals cumulative funding; confirm they are not mixed.",
                entity_id=case.deal.event_id,
                suggested_fix="Separate round amount, cumulative funding, and valuation evidence.",
            )
        )

    for comparable in case.china_comparables:
        if comparable.comparison_type == "direct" and comparable.total_score < 75:
            findings.append(
                QAFinding(
                    rule_id="direct_comparable_score_below_75",
                    severity="redline",
                    message="Direct China comparable score is below 75.",
                    entity_id=comparable.comparable_id,
                    suggested_fix="Downgrade to adjacent/reference or improve six-dimension evidence.",
                )
            )

    if case.status == "ready_to_publish" and not case.human_approved:
        findings.append(
            QAFinding(
                rule_id="no_human_approval",
                severity="redline",
                message="Case cannot be ready_to_publish without human approval.",
                entity_id=case.case_id,
                suggested_fix="Set human_approved only after manual review.",
            )
        )

    if rendered_markdown is not None:
        if "研究截止" not in rendered_markdown or "## 来源" not in rendered_markdown:
            findings.append(
                QAFinding(
                    rule_id="render_missing_as_of_or_sources",
                    severity="redline",
                    message="Rendered report lacks as_of_date or source list.",
                    entity_id=case.case_id,
                    suggested_fix="Render with the daily memo template.",
                )
            )

    redlines = [finding for finding in findings if finding.severity == "redline"]
    score = 100 - min(100, len(redlines) * 25 + len(findings) * 3)
    return QAReport(case_id=case.case_id, passed=not redlines and score >= 85, score=score, findings=findings)
