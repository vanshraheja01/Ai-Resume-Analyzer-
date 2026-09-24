import { describe, expect, it } from "vitest";
import { cn, formatDate, scoreColor, scoreBarColor, APPLICATION_STATUS_LABELS } from "./utils";

describe("cn", () => {
  it("joins truthy class names with spaces", () => {
    expect(cn("a", "b", "c")).toBe("a b c");
  });

  it("filters out falsy values", () => {
    expect(cn("a", false, null, undefined, "b")).toBe("a b");
  });
});

describe("formatDate", () => {
  it("returns a dash for null/undefined", () => {
    expect(formatDate(null)).toBe("-");
    expect(formatDate(undefined)).toBe("-");
  });

  it("formats an ISO date string", () => {
    const result = formatDate("2026-01-15T00:00:00Z");
    expect(result).toMatch(/2026/);
    expect(result).toMatch(/Jan/);
  });
});

describe("scoreColor / scoreBarColor", () => {
  it("uses the high-score color at and above 80", () => {
    expect(scoreColor(80)).toContain("emerald");
    expect(scoreBarColor(100)).toContain("emerald");
  });

  it("uses the mid-score color between 60 and 79", () => {
    expect(scoreColor(60)).toContain("amber");
    expect(scoreBarColor(79)).toContain("amber");
  });

  it("uses the low-score color below 60", () => {
    expect(scoreColor(59)).toContain("red");
    expect(scoreBarColor(0)).toContain("red");
  });
});

describe("APPLICATION_STATUS_LABELS", () => {
  it("has a human-readable label for every status the backend can send", () => {
    const backendStatuses = ["saved", "applied", "interview", "technical_round", "offer", "rejected", "withdrawn"];
    for (const status of backendStatuses) {
      expect(APPLICATION_STATUS_LABELS[status]).toBeTruthy();
    }
  });
});
