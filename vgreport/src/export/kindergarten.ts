import type { FrameId, ReportDraft, ReportPeriod, SectionId, Student } from '../types';
import { FRAMES, SECTIONS } from '../constants';
import { isBoxExportReady } from '../store/rosterStatus';

export type Kindergarten12BoxCsvRow = {
  student_local_id: string;
  student_last_name: string;
  student_first_name: string;
  report_period_id: string;
  boxes: Record<string, string>; // columnName -> text
};

const UTF8_BOM = '\ufeff';

function normalizeNewlinesToCrlf(text: string): string {
  return text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').replace(/\n/g, '\r\n');
}

function csvQuoteAlways(value: unknown): string {
  const s = String(value ?? '');
  // Always quote; escape quotes per RFC4180.
  return `"${s.replace(/"/g, '""')}"`;
}

function frameSlugFromCanonicalId(canonicalId: string): string {
  // canonicalId is like "frame.belonging"
  const parts = canonicalId.split('.');
  return parts.length >= 2 ? parts[1] : canonicalId;
}

function sectionSlugFromVgSectionId(sectionId: string): string {
  if (sectionId === 'key_learning') return 'key_learning';
  if (sectionId === 'growth_in_learning') return 'growth';
  if (sectionId === 'next_steps_in_learning') return 'next_steps';
  return sectionId;
}

export function kindergarten12BoxCsvHeader(): string[] {
  const base = ['student_local_id', 'student_last_name', 'student_first_name', 'report_period_id'];
  const boxCols: string[] = [];

  for (const frame of FRAMES) {
    const frameSlug = frameSlugFromCanonicalId(frame.canonicalId);
    for (const section of SECTIONS) {
      const sectionSlug = sectionSlugFromVgSectionId(section.id);
      boxCols.push(`${frameSlug}_${sectionSlug}`);
    }
  }

  return [...base, ...boxCols];
}

export function buildKindergarten12BoxCsvRow(
  student: Student,
  draft: ReportDraft | undefined,
  period: ReportPeriod
): Kindergarten12BoxCsvRow {
  const boxes: Record<string, string> = {};

  for (const frame of FRAMES) {
    const frameSlug = frameSlugFromCanonicalId(frame.canonicalId);
    for (const section of SECTIONS) {
      const sectionSlug = sectionSlugFromVgSectionId(section.id);
      const col = `${frameSlug}_${sectionSlug}`;

      const comment = (draft?.comments as any)?.[frame.id]?.[section.id];
      const ready = isBoxExportReady(comment);
      const rendered = ready ? String(comment?.rendered ?? '').trim() : '';
      boxes[col] = normalizeNewlinesToCrlf(rendered);
    }
  }

  return {
    student_local_id: student.id,
    student_last_name: student.lastName,
    student_first_name: student.firstName,
    report_period_id: period,
    boxes,
  };
}

export function buildClipboardPerBox(
  draft: ReportDraft | undefined,
  frameId: FrameId,
  sectionId: SectionId
): { text: string; exportReady: boolean } {
  const comment = (draft?.comments as any)?.[frameId]?.[sectionId];
  const exportReady = isBoxExportReady(comment);
  const rendered = exportReady ? String(comment?.rendered ?? '').trim() : '';
  return { text: normalizeNewlinesToCrlf(rendered), exportReady };
}

export function buildKindergarten12BoxCsv(
  students: Student[],
  draftsByStudentId: Record<string, ReportDraft>,
  period: ReportPeriod
): string {
  const header = kindergarten12BoxCsvHeader();

  const sorted = [...students].sort((a, b) => {
    const al = (a.lastName ?? '').localeCompare(b.lastName ?? '', undefined, { sensitivity: 'base' });
    if (al !== 0) return al;
    const af = (a.firstName ?? '').localeCompare(b.firstName ?? '', undefined, { sensitivity: 'base' });
    if (af !== 0) return af;
    return (a.id ?? '').localeCompare(b.id ?? '');
  });

  const lines: string[] = [];
  lines.push(header.map(csvQuoteAlways).join(','));

  for (const student of sorted) {
    const row = buildKindergarten12BoxCsvRow(student, draftsByStudentId[student.id], period);
    const values: string[] = [
      row.student_local_id,
      row.student_last_name,
      row.student_first_name,
      row.report_period_id,
      ...header.slice(4).map((col) => row.boxes[col] ?? ''),
    ];
    lines.push(values.map(csvQuoteAlways).join(','));
  }

  return UTF8_BOM + lines.join('\r\n');
}

export function buildClipboardPerBoxAll(
  draft: ReportDraft | undefined
): { text: string; missing: string[] } {
  const missing: string[] = [];
  const parts: string[] = [];

  for (const frame of FRAMES) {
    for (const section of SECTIONS) {
      const { text: rendered, exportReady } = buildClipboardPerBox(
        draft,
        frame.id as FrameId,
        section.id as SectionId
      );

      const heading = `${frame.label} — ${section.label}`;
      parts.push(heading);
      if (!exportReady || !rendered) {
        missing.push(heading);
        parts.push('');
      } else {
        parts.push(rendered);
      }
      parts.push('');
    }
  }

  const full = parts.join('\r\n');
  return { text: full, missing };
}
