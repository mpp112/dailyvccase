from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal


PublishStatus = Literal["draft", "qa_passed", "approved", "published"]

STATUS_ORDER: tuple[PublishStatus, ...] = ("draft", "qa_passed", "approved", "published")
_ALLOWED_TRANSITIONS: dict[PublishStatus, set[PublishStatus]] = {
    "draft": {"qa_passed"},
    "qa_passed": {"approved"},
    "approved": {"published"},
    "published": set(),
}


@dataclass(frozen=True)
class PublishingInput:
    case_id: str
    company_name: str
    industry: str
    core_thesis: str
    title: str | None = None


@dataclass(frozen=True)
class PublishingArtifacts:
    wechat_html: Path
    cover_prompt: Path
    diagrams: Path
    status: Path


def markdown_to_wechat_html(markdown: str) -> str:
    """Render conservative HTML compatible with md-to-wechat and doocs/md import."""
    lines = markdown.splitlines()
    blocks: list[str] = []
    paragraph: list[str] = []
    table: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(item.strip() for item in paragraph if item.strip())
            if text:
                blocks.append(f'<p style="margin: 0 0 1em; line-height: 1.8;">{_inline(text)}</p>')
            paragraph.clear()

    def flush_table() -> None:
        if table:
            blocks.append(_render_table(table))
            table.clear()

    for raw_line in lines:
        line = raw_line.rstrip()
        if _is_table_line(line):
            flush_paragraph()
            table.append(line)
            continue

        flush_table()
        if not line.strip():
            flush_paragraph()
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            level = min(len(heading.group(1)), 4)
            text = _inline(heading.group(2).strip())
            margin = "1.2em 0 0.6em" if level <= 2 else "1em 0 0.5em"
            blocks.append(
                f'<h{level} style="margin: {margin}; line-height: 1.35; font-weight: 700;">'
                f"{text}</h{level}>"
            )
            continue
        paragraph.append(line)

    flush_paragraph()
    flush_table()
    body = "\n".join(blocks)
    return (
        '<section class="vc-case-wechat" style="font-size: 16px; color: #1f2933;">\n'
        f"{body}\n"
        "</section>\n"
    )


def build_cover_prompt(input_data: PublishingInput) -> str:
    return (
        "微信公众号封面图，16:9 横版，高级商业研究报告风格，"
        f"主题公司：{input_data.company_name}，行业：{input_data.industry}，"
        f"核心投资逻辑：{input_data.core_thesis}。"
        "画面应体现清晰的产业场景、资本市场理性、科技感但不过度炫光，"
        "留出左侧标题安全区，无水印，无真实商标冒用，无小字。"
    )


def build_diagrams(input_data: PublishingInput) -> str:
    company = _mermaid_text(input_data.company_name)
    industry = _mermaid_text(input_data.industry)
    thesis = _mermaid_text(input_data.core_thesis)
    return f"""# Diagrams

## 投资逻辑图

```mermaid
flowchart TD
    A["{industry} 结构性变化"] --> B["{company} 切入点"]
    B --> C["产品/技术优势"]
    B --> D["商业化路径"]
    C --> E["{thesis}"]
    D --> E
    E --> F["投资判断"]
```

## 公司对标结构图

```mermaid
flowchart LR
    A["{company}"] --> B["海外同类公司"]
    A --> C["中国可比公司"]
    B --> D["产品形态"]
    B --> E["客户/渠道"]
    C --> D
    C --> E
    D --> F["可比性评分"]
    E --> F
```

## 融资时间线图

```mermaid
timeline
    title {company} 融资时间线
    待补充日期 : 早期融资/产品验证
    待补充日期 : 本轮融资
    待补充日期 : 后续里程碑
```
"""


def run_publishing_pipeline(input_path: Path, output_dir: Path, input_data: PublishingInput) -> PublishingArtifacts:
    markdown = input_path.read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)

    wechat_html = output_dir / "wechat_ready.html"
    cover_prompt = output_dir / "cover_prompt.txt"
    diagrams = output_dir / "diagrams.md"
    status = output_dir / "publish_status.json"

    wechat_html.write_text(markdown_to_wechat_html(markdown), encoding="utf-8")
    cover_prompt.write_text(build_cover_prompt(input_data), encoding="utf-8")
    diagrams.write_text(build_diagrams(input_data), encoding="utf-8")
    write_publish_status(status, input_data.case_id, "draft")
    return PublishingArtifacts(wechat_html, cover_prompt, diagrams, status)


def write_publish_status(path: Path, case_id: str, status: PublishStatus) -> None:
    payload = {
        "case_id": case_id,
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "manual_approval_required": status != "published",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def transition_publish_status(path: Path, next_status: PublishStatus, *, manual_approval: bool) -> PublishStatus:
    current = read_publish_status(path)
    current_status = current["status"]
    if next_status == "approved" and not manual_approval:
        raise ValueError("manual approval is required before approved")
    if next_status == "published" and not manual_approval:
        raise ValueError("manual approval is required before published")
    if next_status not in _ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(f"invalid status transition: {current_status} -> {next_status}")
    write_publish_status(path, current["case_id"], next_status)
    return next_status


def read_publish_status(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    status = payload.get("status")
    case_id = payload.get("case_id")
    if status not in STATUS_ORDER:
        raise ValueError(f"invalid publish status: {status}")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("publish status missing case_id")
    return {"case_id": case_id, "status": status}


def append_publish_record(
    path: Path,
    *,
    case_id: str,
    article_title: str,
    publish_date: date,
    article_id_or_url: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "case_id": case_id,
        "article_title": article_title,
        "publish_date": publish_date.isoformat(),
        "article_id_or_url": article_id_or_url,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _inline(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def _render_table(lines: list[str]) -> str:
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in lines
        if not re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line)
    ]
    rendered_rows = []
    for index, row in enumerate(rows):
        tag = "th" if index == 0 else "td"
        cells = "".join(
            f'<{tag} style="border: 1px solid #d9e2ec; padding: 8px; text-align: left;">'
            f"{_inline(cell)}</{tag}>"
            for cell in row
        )
        rendered_rows.append(f"<tr>{cells}</tr>")
    return (
        '<table style="border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 14px;">'
        f"{''.join(rendered_rows)}</table>"
    )


def _mermaid_text(text: str) -> str:
    return text.replace('"', "'").replace("\n", " ").strip()
