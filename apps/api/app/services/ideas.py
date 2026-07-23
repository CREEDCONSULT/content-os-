from __future__ import annotations

from app.db.models import Idea
from app.schemas.contracts import IdeaScores

SCORE_FIELDS = (
    "brand_fit_score",
    "audience_value_score",
    "proof_score",
    "timeliness_score",
    "originality_score",
    "feasibility_score",
    "strategic_importance_score",
)


def calculate_priority(scores: IdeaScores) -> float:
    values = [getattr(scores, field) for field in SCORE_FIELDS]
    return round(sum(values) / len(values), 1)


def apply_scores(idea: Idea, scores: IdeaScores) -> Idea:
    for field in SCORE_FIELDS:
        setattr(idea, field, getattr(scores, field))
    idea.total_priority_score = calculate_priority(scores)
    return idea
