import { describe, expect, it } from "vitest";

import { compactGroup, NEXT_STATUS, PIPELINE_GROUPS } from "@/lib/pipeline";

describe("content lifecycle contract", () => {
  it("covers every one of the fifteen backend states exactly once", () => {
    const statuses = Object.values(PIPELINE_GROUPS).flat();

    expect(statuses).toHaveLength(15);
    expect(new Set(statuses).size).toBe(15);
  });

  it("keeps publish readiness inside review until the gated publish transition", () => {
    expect(compactGroup("ready_to_publish")).toBe("review");
    expect(NEXT_STATUS.ready_to_publish).toBe("published");
  });

  it("maps learning and repurposing back into the published operations lane", () => {
    expect(compactGroup("analytics_review")).toBe("published");
    expect(compactGroup("repurpose")).toBe("published");
  });
});
