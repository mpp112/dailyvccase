from __future__ import annotations

from typing import Literal

from vc_research.models import Candidate, ComparableScores


def score_candidate(candidate: Candidate) -> float:
    score = 0.0
    score += 5 if candidate.source_tier == 1 else 4 if candidate.source_tier == 2 else 2
    score += 5 if candidate.amount_raw and candidate.currency else 2
    score += 5 if candidate.lead_investors else 2
    score += 5 if candidate.sector.lower() in {"ai applications", "robotics"} else 3
    score += 5 if candidate.round_raw.lower() in {"seed", "series a", "series b", "pre-seed"} else 3
    score += 5 if candidate.country in {"United States", "Europe", "Israel", "Singapore"} else 3
    score += 5 if candidate.source_url else 0
    return score


def classify_comparable(scores: ComparableScores) -> Literal["direct", "adjacent", "reference"]:
    if scores.total >= 75:
        return "direct"
    if scores.total >= 55:
        return "adjacent"
    return "reference"
