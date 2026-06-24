from __future__ import annotations

import hashlib
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field, field_validator


CaseStatus = Literal[
    "discovered",
    "shortlisted",
    "researching",
    "evidence_complete",
    "qa_failed",
    "qa_passed",
    "ready_to_publish",
    "published",
    "monitoring",
]
ClaimType = Literal["F", "S", "H"]
Confidence = Literal["A", "B", "C", "D"]
ConflictStatus = Literal["none", "possible", "confirmed", "resolved"]
ReviewStatus = Literal["unreviewed", "accepted", "rejected", "needs_more_evidence"]
ComparisonType = Literal["direct", "adjacent", "reference"]


def stable_id(prefix: str, *parts: object) -> str:
    normalized = "|".join(str(part).strip().lower() for part in parts if part is not None)
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Company(BaseModel):
    model_config = ConfigDict(extra="allow")

    company_id: str
    brand_name: str
    country: str
    legal_name: str | None = None
    aliases: list[str] = Field(default_factory=list)
    headquarters: str | None = None
    founded_date: date | None = None
    website: HttpUrl | None = None
    product_summary: str | None = None
    customer_type: str | None = None
    business_model: str | None = None
    deployment_model: str | None = None
    sector_tags: list[str] = Field(default_factory=list)


class Investor(BaseModel):
    investor_id: str
    brand_name: str
    legal_entity_name: str | None = None
    manager_name: str | None = None
    investor_type: str = "Other"
    country: str | None = None
    website: HttpUrl | None = None
    portfolio_matches: list[str] = Field(default_factory=list)
    first_entry_round: str | None = None
    follow_on_status: str | None = None


class FinancingEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_id: str
    company_id: str
    announcement_date: date
    round_label_raw: str
    round_normalized: str | None = None
    transaction_date: date | None = None
    amount_original: float | None = None
    currency_original: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    amount_usd: float | None = None
    amount_cny: float | None = None
    fx_rate_date: date | None = None
    valuation: float | None = None
    valuation_status: Literal["official", "media_estimate", "undisclosed", "not_applicable"] = "undisclosed"
    cumulative_funding: float | None = None
    lead_investors: list[str] = Field(default_factory=list)
    other_investors: list[str] = Field(default_factory=list)
    fund_use: list[str] = Field(default_factory=list)


class Source(BaseModel):
    source_id: str
    url: HttpUrl
    publisher: str
    title: str
    accessed_at: datetime = Field(default_factory=now_utc)
    tier: int = Field(ge=1, le=4)
    language: str = "en"
    content_type: str = "manual_fixture"
    published_at: datetime | None = None
    content_hash: str | None = None
    archive_path: str | None = None
    access_notes: str | None = None


class Claim(BaseModel):
    claim_id: str
    case_id: str
    statement: str
    claim_type: ClaimType
    topic: str
    confidence: Confidence
    source_ids: list[str] = Field(default_factory=list)
    quoted_excerpt: str | None = None
    location_hint: str | None = None
    conflict_status: ConflictStatus = "none"
    review_status: ReviewStatus = "accepted"
    reviewer: str | None = None

    @field_validator("source_ids")
    @classmethod
    def facts_need_sources(cls, value: list[str], info: object) -> list[str]:
        return value


class ComparableScores(BaseModel):
    customer: float = Field(ge=0, le=20)
    pain: float = Field(ge=0, le=25)
    product: float = Field(ge=0, le=20)
    business_model: float = Field(ge=0, le=15)
    go_to_market: float = Field(ge=0, le=10)
    stage: float = Field(ge=0, le=10)

    @computed_field
    @property
    def total(self) -> float:
        return (
            self.customer
            + self.pain
            + self.product
            + self.business_model
            + self.go_to_market
            + self.stage
        )


class Comparable(BaseModel):
    comparable_id: str
    foreign_company_id: str
    china_company: Company
    scores: ComparableScores
    comparison_type: ComparisonType
    why_comparable: str
    why_not_comparable: str

    @computed_field
    @property
    def total_score(self) -> float:
        return self.scores.total


class FinancingHistoryRecord(BaseModel):
    history_id: str
    company_id: str
    announcement_date: date | None = None
    round_raw: str
    round_normalized: str | None = None
    amount_raw: str | None = None
    currency: str | None = None
    lead_investors: list[str] = Field(default_factory=list)
    other_investors: list[str] = Field(default_factory=list)
    legal_investment_entity: str | None = None
    brand_or_manager: str | None = None
    confidence: Confidence = "C"
    source_ids: list[str] = Field(default_factory=list)
    conflict_notes: str | None = None


class Candidate(BaseModel):
    candidate_id: str
    discovered_at: datetime
    company_name: str
    country: str
    sector: str
    round_raw: str
    announcement_date: date
    source_url: HttpUrl
    source_tier: int = Field(ge=1, le=4)
    amount_raw: str | None = None
    currency: str | None = None
    lead_investors: list[str] = Field(default_factory=list)
    score: float = 0
    status: str = "discovered"
    notes: str | None = None


class QAFinding(BaseModel):
    rule_id: str
    severity: Literal["info", "warning", "error", "redline"]
    message: str
    entity_id: str | None = None
    suggested_fix: str | None = None


class QAReport(BaseModel):
    case_id: str
    passed: bool
    score: int
    findings: list[QAFinding] = Field(default_factory=list)


class CaseRecord(BaseModel):
    case_id: str
    as_of_date: date
    status: CaseStatus = "researching"
    foreign_company: Company
    deal: FinancingEvent
    sources: list[Source] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    china_comparables: list[Comparable] = Field(default_factory=list)
    financing_history: list[FinancingHistoryRecord] = Field(default_factory=list)
    investors: list[Investor] = Field(default_factory=list)
    human_approved: bool = False
    headline_thesis: str = "虚构样例，仅用于工作台测试"
