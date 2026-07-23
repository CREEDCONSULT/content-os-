from __future__ import annotations

from app.db.models import PipelineStatus

PIPELINE_GROUPS: dict[str, tuple[PipelineStatus, ...]] = {
    "ideation": (
        PipelineStatus.IDEA,
        PipelineStatus.RESEARCH,
        PipelineStatus.BRIEF,
    ),
    "scripting": (
        PipelineStatus.SCRIPT,
        PipelineStatus.REVIEW,
        PipelineStatus.APPROVED,
    ),
    "production": (
        PipelineStatus.READY_TO_SHOOT,
        PipelineStatus.SHOT,
        PipelineStatus.EDITING,
    ),
    "review": (
        PipelineStatus.REVIEW_EDIT,
        PipelineStatus.READY_TO_PUBLISH,
    ),
    "published": (
        PipelineStatus.PUBLISHED,
        PipelineStatus.ANALYTICS_REVIEW,
        PipelineStatus.REPURPOSE,
        PipelineStatus.ARCHIVED,
    ),
}

ALLOWED_TRANSITIONS: dict[PipelineStatus, set[PipelineStatus]] = {
    PipelineStatus.IDEA: {PipelineStatus.RESEARCH, PipelineStatus.ARCHIVED},
    PipelineStatus.RESEARCH: {PipelineStatus.BRIEF, PipelineStatus.IDEA, PipelineStatus.ARCHIVED},
    PipelineStatus.BRIEF: {PipelineStatus.SCRIPT, PipelineStatus.RESEARCH, PipelineStatus.ARCHIVED},
    PipelineStatus.SCRIPT: {PipelineStatus.REVIEW, PipelineStatus.BRIEF, PipelineStatus.ARCHIVED},
    PipelineStatus.REVIEW: {
        PipelineStatus.APPROVED,
        PipelineStatus.SCRIPT,
        PipelineStatus.ARCHIVED,
    },
    PipelineStatus.APPROVED: {PipelineStatus.READY_TO_SHOOT, PipelineStatus.SCRIPT},
    PipelineStatus.READY_TO_SHOOT: {PipelineStatus.SHOT, PipelineStatus.APPROVED},
    PipelineStatus.SHOT: {PipelineStatus.EDITING, PipelineStatus.READY_TO_SHOOT},
    PipelineStatus.EDITING: {PipelineStatus.REVIEW_EDIT, PipelineStatus.SHOT},
    PipelineStatus.REVIEW_EDIT: {PipelineStatus.READY_TO_PUBLISH, PipelineStatus.EDITING},
    PipelineStatus.READY_TO_PUBLISH: {PipelineStatus.PUBLISHED, PipelineStatus.REVIEW_EDIT},
    PipelineStatus.PUBLISHED: {PipelineStatus.ANALYTICS_REVIEW},
    PipelineStatus.ANALYTICS_REVIEW: {PipelineStatus.REPURPOSE, PipelineStatus.ARCHIVED},
    PipelineStatus.REPURPOSE: {PipelineStatus.IDEA, PipelineStatus.ARCHIVED},
    PipelineStatus.ARCHIVED: set(),
}


def compact_group(status: PipelineStatus) -> str:
    for name, statuses in PIPELINE_GROUPS.items():
        if status in statuses:
            return name
    return "ideation"
