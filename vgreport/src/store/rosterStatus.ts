import type { CommentDraft, FrameId, ReportDraft, SectionId } from "../types";
import { FRAMES, SECTIONS } from "../constants";

export type RosterFilter = "all" | "incomplete" | "needs_review";

export function isBoxExportReady(comment: CommentDraft | undefined): boolean {
  const rendered = (comment?.rendered ?? "").trim();
  if (!rendered) return false;
  if (comment?.validation && comment.validation.valid === false) return false;
  const status = comment?.status ?? (comment?.author === "ece" ? "draft" : "approved");
  return status === "approved";
}

export function studentBoxCounts(draft: ReportDraft | undefined): { ready: number; total: number } {
  if (!draft) return { ready: 0, total: FRAMES.length * SECTIONS.length };

  let ready = 0;
  let total = 0;
  for (const frame of FRAMES) {
    for (const section of SECTIONS) {
      total += 1;
      const comment = (draft.comments?.[frame.id as FrameId] as any)?.[section.id as SectionId] as CommentDraft | undefined;
      if (isBoxExportReady(comment)) ready += 1;
    }
  }
  return { ready, total };
}

export function studentNeedsReview(draft: ReportDraft | undefined): boolean {
  if (!draft) return false;
  for (const frame of FRAMES) {
    for (const section of SECTIONS) {
      const comment = (draft.comments?.[frame.id as FrameId] as any)?.[section.id as SectionId] as CommentDraft | undefined;
      if (!comment) continue;
      if ((comment.author ?? "teacher") === "ece" && (comment.status ?? "draft") !== "approved") {
        return true;
      }
    }
  }
  return false;
}
