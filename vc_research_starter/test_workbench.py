from __future__ import annotations

from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from vc_research.cli import app
from vc_research.config import ROOT
from vc_research.fixtures import load_fixture_case, seed_fixtures
from vc_research.ingest import import_candidates
from vc_research.normalize import event_key, normalize_company_name
from vc_research.publishing import (
    PublishingInput,
    append_publish_record,
    run_publishing_pipeline,
    transition_publish_status,
)
from vc_research.qa import validate_case
from vc_research.rendering import render_daily_memo
from vc_research.scoring import classify_comparable, score_candidate
from vc_research.storage import SQLiteStore


def make_store(tmp_path: Path) -> SQLiteStore:
    store = SQLiteStore(tmp_path / "test.sqlite")
    store.init_db()
    return store


def test_idempotent_candidate_import_and_event_dedupe(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    fixture = ROOT / "data" / "raw" / "fixture_candidates.csv"
    first = import_candidates(fixture, store)
    second = import_candidates(fixture, store)
    assert first == {"created": 1, "updated": 1, "total": 2}
    assert second == {"created": 0, "updated": 2, "total": 2}
    assert len(store.list_candidates()) == 1


def test_company_alias_normalization_and_event_key() -> None:
    assert normalize_company_name("Nebula Ledger Labs Inc.") == "nebula ledger labs"
    assert normalize_company_name("Nebula Ledger Labs") == "nebula ledger labs"
    key_a = event_key("Nebula Ledger Labs Inc.", date(2026, 6, 22), "Seed", "5000000")
    assert key_a.startswith("event_")


def test_candidate_scoring(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    import_candidates(ROOT / "data" / "raw" / "fixture_candidates.csv", store)
    candidate = store.list_candidates()[0]
    assert score_candidate(candidate) >= 30


def test_claim_source_and_confidence_rules() -> None:
    case = load_fixture_case(ROOT / "data" / "raw" / "case_conflict.fixture.json")
    report = validate_case(case)
    assert not report.passed
    assert {"critical_fact_below_b", "unresolved_critical_source_conflict"} <= {
        finding.rule_id for finding in report.findings
    }


def test_comparable_scoring_and_redline() -> None:
    case = load_fixture_case(ROOT / "data" / "raw" / "case_low_comparable.fixture.json")
    comparable = case.china_comparables[0]
    assert classify_comparable(comparable.scores) == "reference"
    report = validate_case(case)
    assert not report.passed
    assert any(finding.rule_id == "direct_comparable_score_below_75" for finding in report.findings)


def test_markdown_rendering(tmp_path: Path) -> None:
    case = load_fixture_case(ROOT / "data" / "raw" / "case_pass.fixture.json")
    report = validate_case(case)
    assert report.passed
    path = render_daily_memo(case, report, tmp_path)
    rendered = path.read_text(encoding="utf-8")
    assert "研究截止：2026-06-22" in rendered
    assert "## 来源" in rendered


def test_end_to_end_smoke(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    case_ids = seed_fixtures(ROOT / "data" / "raw", store)
    assert {"case_pass", "case_conflict", "case_low_comparable"} == set(case_ids)
    case = store.get_case("case_pass")
    report = validate_case(case)
    path = render_daily_memo(case, report, tmp_path)
    assert report.passed
    assert path.exists()


def test_cli_smoke(tmp_path: Path) -> None:
    runner = CliRunner()
    db = tmp_path / "cli.sqlite"
    result = runner.invoke(app, ["init-db", "--db", str(db)])
    assert result.exit_code == 0
    result = runner.invoke(app, ["seed-fixture-cases", "--db", str(db)])
    assert result.exit_code == 0
    result = runner.invoke(app, ["validate", "--case-id", "case_pass", "--db", str(db)])
    assert result.exit_code == 0


def test_publishing_pipeline_outputs_wechat_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "vc_case_final.md"
    source.write_text(
        "# Sample Case\n\n## Thesis\n\n**AI infra** adoption.\n\n"
        "| Metric | Value |\n| --- | --- |\n| ARR | TBD |\n",
        encoding="utf-8",
    )
    artifacts = run_publishing_pipeline(
        source,
        tmp_path / "publish",
        PublishingInput(
            case_id="case_sample",
            company_name="SampleAI",
            industry="AI infrastructure",
            core_thesis="workflow automation drives expansion",
        ),
    )

    rendered = artifacts.wechat_html.read_text(encoding="utf-8")
    assert "<h1" in rendered
    assert "<table" in rendered
    assert "SampleAI" in artifacts.cover_prompt.read_text(encoding="utf-8")
    assert "```mermaid" in artifacts.diagrams.read_text(encoding="utf-8")


def test_publish_status_requires_manual_approval(tmp_path: Path) -> None:
    source = tmp_path / "vc_case_final.md"
    source.write_text("# Case\n", encoding="utf-8")
    artifacts = run_publishing_pipeline(
        source,
        tmp_path / "publish",
        PublishingInput(
            case_id="case_sample",
            company_name="SampleAI",
            industry="AI infrastructure",
            core_thesis="workflow automation drives expansion",
        ),
    )

    assert transition_publish_status(artifacts.status, "qa_passed", manual_approval=False) == "qa_passed"
    try:
        transition_publish_status(artifacts.status, "approved", manual_approval=False)
    except ValueError as error:
        assert "manual approval" in str(error)
    else:
        raise AssertionError("approved status must require manual approval")
    assert transition_publish_status(artifacts.status, "approved", manual_approval=True) == "approved"


def test_publish_record_jsonl(tmp_path: Path) -> None:
    record = tmp_path / "records.jsonl"
    append_publish_record(
        record,
        case_id="case_sample",
        article_title="Sample Case",
        publish_date=date(2026, 6, 23),
        article_id_or_url="https://example.com/article",
    )

    content = record.read_text(encoding="utf-8")
    assert "Sample Case" in content
    assert "case_sample" in content
