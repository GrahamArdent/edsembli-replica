import { describe, expect, it } from "vitest";
import type { ReportDraft } from "../types";
import { isBoxExportReady, studentBoxCounts, studentNeedsReview } from "./rosterStatus";

describe("isBoxExportReady", () => {
  it("false for empty", () => {
    expect(isBoxExportReady({ slots: {}, rendered: "" })).toBe(false);
  });

  it("true for teacher default approved", () => {
    expect(isBoxExportReady({ slots: {}, rendered: "Hello" })).toBe(true);
  });

  it("false for ECE draft", () => {
    expect(isBoxExportReady({ slots: {}, rendered: "Hello", author: "ece", status: "draft" })).toBe(false);
  });

  it("true for ECE approved", () => {
    expect(isBoxExportReady({ slots: {}, rendered: "Hello", author: "ece", status: "approved" })).toBe(true);
  });
});

describe("studentNeedsReview", () => {
  it("true if any ECE draft exists", () => {
    const draft: ReportDraft = {
      studentId: "s1",
      period: "february",
      comments: {
        belonging_and_contributing: {
          key_learning: { slots: {}, rendered: "Text", author: "ece", status: "draft" },
          growth_in_learning: { slots: {}, rendered: "" },
          next_steps_in_learning: { slots: {}, rendered: "" },
        },
        self_regulation_and_well_being: {} as any,
        demonstrating_literacy_and_mathematics_behaviors: {} as any,
        problem_solving_and_innovating: {} as any,
      } as any,
    };
    expect(studentNeedsReview(draft)).toBe(true);
  });
});

describe("studentBoxCounts", () => {
  it("counts ready boxes", () => {
    const draft: ReportDraft = {
      studentId: "s1",
      period: "february",
      comments: {
        belonging_and_contributing: {
          key_learning: { slots: {}, rendered: "Text" },
          growth_in_learning: { slots: {}, rendered: "" },
          next_steps_in_learning: { slots: {}, rendered: "" },
        },
        self_regulation_and_well_being: {} as any,
        demonstrating_literacy_and_mathematics_behaviors: {} as any,
        problem_solving_and_innovating: {} as any,
      } as any,
    };

    const counts = studentBoxCounts(draft);
    expect(counts.ready).toBe(1);
    expect(counts.total).toBe(12);
  });
});
