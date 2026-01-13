import type { Tier1ValidationConfig } from "../types";

export type ValidationSeverity = "info" | "warning" | "error";

export type Tier1IssueCode =
  | "too_short"
  | "too_long"
  | "too_many_line_breaks"
  | "too_few_sentences";

export type Tier1Issue = {
  severity: ValidationSeverity;
  code: Tier1IssueCode;
  message: string;
};

export function countSentences(text: string): number {
  const t = String(text ?? "").trim();
  if (!t) return 0;

  const normalized = t.replace(/\s+/g, " ");
  const matches = normalized.match(/[^.!?]+[.!?]+/g);
  let count = matches ? matches.length : 0;

  const lastChar = normalized[normalized.length - 1];
  if (!/[.!?]/.test(lastChar)) {
    // Treat a trailing fragment as a sentence.
    count += 1;
  }

  return count;
}

export function analyzeTier1(text: string, config: Tier1ValidationConfig): Tier1Issue[] {
  const t = String(text ?? "").trim();
  if (!t) return [];

  const issues: Tier1Issue[] = [];
  const charCount = t.length;

  if (charCount < config.minChars) {
    issues.push({
      severity: "warning",
      code: "too_short",
      message: `Text is short (${charCount} chars). Target ≥ ${config.minChars}.`,
    });
  }

  if (charCount > config.maxChars) {
    issues.push({
      severity: "warning",
      code: "too_long",
      message: `Text is long (${charCount} chars). Target ≤ ${config.maxChars}.`,
    });
  }

  const lineBreakCount = (t.match(/\r?\n/g) ?? []).length;
  if (lineBreakCount > config.maxLineBreaks) {
    issues.push({
      severity: "info",
      code: "too_many_line_breaks",
      message: `Contains ${lineBreakCount} line breaks. Target ≤ ${config.maxLineBreaks}.`,
    });
  }

  const sentenceCount = countSentences(t);
  if (sentenceCount > 0 && sentenceCount < config.minSentences) {
    issues.push({
      severity: "info",
      code: "too_few_sentences",
      message: `Only ${sentenceCount} sentence${sentenceCount === 1 ? "" : "s"}. Target ≥ ${config.minSentences}.`,
    });
  }

  return issues;
}
