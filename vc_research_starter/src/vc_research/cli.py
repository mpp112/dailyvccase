from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from vc_research.config import ROOT, load_settings
from vc_research.fixtures import seed_fixtures
from vc_research.ingest import import_candidates
from vc_research.publishing import (
    PublishingInput,
    append_publish_record,
    run_publishing_pipeline,
    transition_publish_status,
)
from vc_research.qa import validate_case
from vc_research.rendering import render_daily_memo
from vc_research.scoring import score_candidate
from vc_research.storage import SQLiteStore

app = typer.Typer(help="VC case research workbench MVP.")


def _store(db: Path | None = None) -> SQLiteStore:
    settings = load_settings()
    store = SQLiteStore(db or settings.db_path)
    store.init_db()
    return store


@app.command()
def init_db(db: Annotated[Path | None, typer.Option()] = None) -> None:
    _store(db)
    typer.echo("initialized")


@app.command()
def import_candidates_cmd(
    path: Annotated[Path, typer.Argument(help="CSV or JSON candidate file")],
    db: Annotated[Path | None, typer.Option()] = None,
) -> None:
    result = import_candidates(path, _store(db))
    typer.echo(json.dumps(result, ensure_ascii=False))


@app.command(name="import-candidates")
def import_candidates_alias(
    path: Annotated[Path, typer.Argument(help="CSV or JSON candidate file")],
    db: Annotated[Path | None, typer.Option()] = None,
) -> None:
    import_candidates_cmd(path, db)


@app.command()
def list_candidates(db: Annotated[Path | None, typer.Option()] = None) -> None:
    rows = [candidate.model_dump(mode="json") for candidate in _store(db).list_candidates()]
    typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))


@app.command()
def score_candidates(db: Annotated[Path | None, typer.Option()] = None) -> None:
    rows = []
    for candidate in _store(db).list_candidates():
        candidate.score = score_candidate(candidate)
        rows.append({"candidate_id": candidate.candidate_id, "score": candidate.score})
    typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))


@app.command()
def seed_fixture_cases(db: Annotated[Path | None, typer.Option()] = None) -> None:
    case_ids = seed_fixtures(ROOT / "data" / "raw", _store(db))
    typer.echo(json.dumps({"seeded": case_ids}, ensure_ascii=False))


@app.command()
def validate(
    case_id: Annotated[str, typer.Option()],
    db: Annotated[Path | None, typer.Option()] = None,
) -> None:
    case = _store(db).get_case(case_id)
    report = validate_case(case)
    typer.echo(report.model_dump_json(indent=2))
    if not report.passed:
        raise typer.Exit(2)


@app.command()
def render(
    case_id: Annotated[str, typer.Option()],
    db: Annotated[Path | None, typer.Option()] = None,
) -> None:
    settings = load_settings()
    case = _store(db).get_case(case_id)
    report = validate_case(case)
    path = render_daily_memo(case, report, settings.output_dir)
    rendered = path.read_text(encoding="utf-8")
    final_report = validate_case(case, rendered)
    typer.echo(json.dumps({"path": str(path), "qa_passed": final_report.passed}, ensure_ascii=False))
    if not final_report.passed:
        raise typer.Exit(2)


@app.command()
def weekly_review(
    week: Annotated[str, typer.Option()],
    db: Annotated[Path | None, typer.Option()] = None,
) -> None:
    from vc_research.monitoring import weekly_review_rows

    typer.echo(json.dumps(weekly_review_rows(_store(db).list_cases(), week), ensure_ascii=False, indent=2))


@app.command(name="publish-wechat")
def publish_wechat(
    input_path: Annotated[Path, typer.Argument(help="Path to vc_case_final.md")],
    case_id: Annotated[str, typer.Option()],
    company_name: Annotated[str, typer.Option()],
    industry: Annotated[str, typer.Option()],
    core_thesis: Annotated[str, typer.Option()],
    output_dir: Annotated[Path | None, typer.Option()] = None,
    title: Annotated[str | None, typer.Option()] = None,
) -> None:
    settings = load_settings()
    target_dir = output_dir or settings.output_dir / "publishing" / case_id
    artifacts = run_publishing_pipeline(
        input_path,
        target_dir,
        PublishingInput(
            case_id=case_id,
            company_name=company_name,
            industry=industry,
            core_thesis=core_thesis,
            title=title,
        ),
    )
    typer.echo(
        json.dumps(
            {
                "wechat_ready_html": str(artifacts.wechat_html),
                "cover_prompt": str(artifacts.cover_prompt),
                "diagrams": str(artifacts.diagrams),
                "status": str(artifacts.status),
                "manual_approval_required": True,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@app.command(name="publish-status")
def publish_status(
    status_path: Annotated[Path, typer.Argument(help="Path to publish_status.json")],
    next_status: Annotated[str, typer.Option()],
    manual_approval: Annotated[bool, typer.Option()] = False,
) -> None:
    status = transition_publish_status(
        status_path,
        next_status,  # type: ignore[arg-type]
        manual_approval=manual_approval,
    )
    typer.echo(json.dumps({"status": status}, ensure_ascii=False))


@app.command(name="publish-record")
def publish_record(
    case_id: Annotated[str, typer.Option()],
    article_title: Annotated[str, typer.Option()],
    publish_date: Annotated[date, typer.Option()],
    article_id_or_url: Annotated[str, typer.Option()],
    record_path: Annotated[Path | None, typer.Option()] = None,
) -> None:
    settings = load_settings()
    target = record_path or settings.output_dir / "publishing_records.jsonl"
    append_publish_record(
        target,
        case_id=case_id,
        article_title=article_title,
        publish_date=publish_date,
        article_id_or_url=article_id_or_url,
    )
    typer.echo(json.dumps({"record_path": str(target)}, ensure_ascii=False))


if __name__ == "__main__":
    app()
