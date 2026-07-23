import type { PipelineGroup, PipelineStatus } from "@/lib/contracts";

export const PIPELINE_GROUPS: Record<PipelineGroup, PipelineStatus[]> = {
  ideation: ["idea", "research", "brief"],
  scripting: ["script", "review", "approved"],
  production: ["ready_to_shoot", "shot", "editing"],
  review: ["review_edit", "ready_to_publish"],
  published: ["published", "analytics_review", "repurpose", "archived"],
};

export const PIPELINE_LABELS: Record<PipelineStatus, string> = {
  idea: "Idea",
  research: "Research",
  brief: "Brief",
  script: "Script",
  review: "Script review",
  approved: "Approved",
  ready_to_shoot: "Ready to shoot",
  shot: "Shot",
  editing: "Editing",
  review_edit: "Edit review",
  ready_to_publish: "Ready to publish",
  published: "Published",
  analytics_review: "Analytics review",
  repurpose: "Repurpose",
  archived: "Archived",
};

export const NEXT_STATUS: Partial<Record<PipelineStatus, PipelineStatus>> = {
  idea: "research",
  research: "brief",
  brief: "script",
  script: "review",
  review: "approved",
  approved: "ready_to_shoot",
  ready_to_shoot: "shot",
  shot: "editing",
  editing: "review_edit",
  review_edit: "ready_to_publish",
  ready_to_publish: "published",
  published: "analytics_review",
  analytics_review: "repurpose",
  repurpose: "archived",
};

export function compactGroup(status: PipelineStatus): PipelineGroup {
  const match = (Object.entries(PIPELINE_GROUPS) as [PipelineGroup, PipelineStatus[]][]).find(
    ([, statuses]) => statuses.includes(status),
  );
  return match?.[0] ?? "ideation";
}
