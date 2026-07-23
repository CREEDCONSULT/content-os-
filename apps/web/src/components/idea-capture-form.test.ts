import { describe, expect, it } from "vitest";

import { ideaCaptureSchema } from "@/components/idea-capture-form";

describe("ideaCaptureSchema", () => {
  it("rejects a context-free capture", () => {
    const result = ideaCaptureSchema.safeParse({
      title: "AI",
      raw_input: "",
      audience: "Builders",
      platform_fit: [],
    });

    expect(result.success).toBe(false);
  });

  it("normalizes a valid governed idea payload", () => {
    const result = ideaCaptureSchema.safeParse({
      title: "  The system behind consistent proof  ",
      raw_input: "  Show the actual weekly workflow and its artifacts.  ",
      pillar: "Build",
      audience: "Emerging Builder",
      platform_fit: ["LinkedIn", "Instagram"],
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.title).toBe("The system behind consistent proof");
      expect(result.data.raw_input).toContain("weekly workflow");
    }
  });
});
