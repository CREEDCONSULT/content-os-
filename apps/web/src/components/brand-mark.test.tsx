import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BrandMark } from "@/components/brand-mark";

describe("BrandMark", () => {
  it("renders the Builder Intelligence identity", () => {
    render(<BrandMark />);

    expect(screen.getByTestId("brand-mark")).toBeInTheDocument();
    expect(screen.getByText("BrandOS")).toBeInTheDocument();
    expect(screen.getByText("Builder Intelligence")).toBeInTheDocument();
  });

  it("supports a compact icon-only form", () => {
    render(<BrandMark compact />);

    expect(screen.getByTestId("brand-mark")).toBeInTheDocument();
    expect(screen.queryByText("Builder Intelligence")).not.toBeInTheDocument();
  });
});
