import type { CommentDraft, DraftStatus, UserRole } from '../types';

export function defaultStatusForRole(role: UserRole): DraftStatus {
  return role === 'teacher' ? 'approved' : 'draft';
}

export function normalizeDraftMeta(
  currentRole: UserRole,
  existing: Pick<CommentDraft, 'author' | 'status'> | undefined,
  next: Pick<CommentDraft, 'author' | 'status'> | undefined
): { author: UserRole; status: DraftStatus } {
  const author = (next?.author ?? existing?.author ?? currentRole) as UserRole;
  const status = (next?.status ?? existing?.status ?? defaultStatusForRole(author)) as DraftStatus;
  return { author, status };
}
