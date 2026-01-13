import { describe, expect, it } from 'vitest';
import { normalizeDraftMeta } from './roleApproval';

describe('normalizeDraftMeta', () => {
  it('defaults teacher drafts to approved', () => {
    const meta = normalizeDraftMeta('teacher', undefined, undefined);
    expect(meta).toEqual({ author: 'teacher', status: 'approved' });
  });

  it('defaults ece drafts to draft', () => {
    const meta = normalizeDraftMeta('ece', undefined, undefined);
    expect(meta).toEqual({ author: 'ece', status: 'draft' });
  });

  it('preserves existing ECE author when teacher edits', () => {
    const meta = normalizeDraftMeta('teacher', { author: 'ece', status: 'draft' }, undefined);
    expect(meta).toEqual({ author: 'ece', status: 'draft' });
  });

  it('allows status override without changing author', () => {
    const meta = normalizeDraftMeta('teacher', { author: 'ece', status: 'draft' }, { status: 'approved' });
    expect(meta).toEqual({ author: 'ece', status: 'approved' });
  });
});
