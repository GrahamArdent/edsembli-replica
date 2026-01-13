import { describe, expect, it } from "vitest";
import { analyzeTier1, countSentences } from "./tier1";

const DEFAULTS = {
  minChars: 100,
  maxChars: 600,
  minSentences: 2,
  maxLineBreaks: 2,
};

describe("countSentences", () => {
  it("returns 0 for empty", () => {
    expect(countSentences(" ")).toBe(0);
  });

  it("counts punctuation-terminated sentences", () => {
    expect(countSentences("A. B! C?")).toBe(3);
  });

  it("counts a trailing fragment as a sentence", () => {
    expect(countSentences("A. trailing")).toBe(2);
  });
});

describe("analyzeTier1", () => {
  it("returns no issues for empty text", () => {
    expect(analyzeTier1("", DEFAULTS)).toEqual([]);
  });

  it("warns when too short", () => {
    const issues = analyzeTier1("Short sentence.", { ...DEFAULTS, minChars: 50 });
    expect(issues.some(i => i.code === "too_short")).toBe(true);
  });

  it("warns when too long", () => {
    const text = "x".repeat(21);
    const issues = analyzeTier1(text, { ...DEFAULTS, maxChars: 20 });
    expect(issues.some(i => i.code === "too_long")).toBe(true);
  });

  it("flags too few sentences", () => {
    const issues = analyzeTier1("One.", { ...DEFAULTS, minSentences: 2, minChars: 0 });
    expect(issues.some(i => i.code === "too_few_sentences")).toBe(true);
  });
});
