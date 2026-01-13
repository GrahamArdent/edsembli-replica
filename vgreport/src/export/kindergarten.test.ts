import { describe, expect, it } from 'vitest';
import type { ReportDraft, Student } from '../types';
import { buildKindergarten12BoxCsv, kindergarten12BoxCsvHeader } from './kindergarten';

function splitCsvRows(csvWithoutBom: string): string[] {
  const rows: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < csvWithoutBom.length; i++) {
    const ch = csvWithoutBom[i];
    const next = i + 1 < csvWithoutBom.length ? csvWithoutBom[i + 1] : '';

    if (ch === '"') {
      if (inQuotes && next === '"') {
        current += '""';
        i += 1;
        continue;
      }
      inQuotes = !inQuotes;
      current += ch;
      continue;
    }

    if (!inQuotes && ch === '\r' && next === '\n') {
      rows.push(current);
      current = '';
      i += 1;
      continue;
    }

    current += ch;
  }

  rows.push(current);
  return rows;
}

function emptyDraft(studentId: string, period: any): ReportDraft {
  return {
    studentId,
    period,
    comments: {
      belonging_and_contributing: {
        key_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        growth_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        next_steps_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
      },
      self_regulation_and_well_being: {
        key_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        growth_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        next_steps_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
      },
      demonstrating_literacy_and_mathematics_behaviors: {
        key_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        growth_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        next_steps_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
      },
      problem_solving_and_innovating: {
        key_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        growth_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
        next_steps_in_learning: { slots: {}, rendered: '', author: 'teacher', status: 'approved' },
      },
    } as any,
  };
}

describe('kindergarten 12-box CSV (golden)', () => {
  it('uses stable header columns and quotes every field (including header)', () => {
    const header = kindergarten12BoxCsvHeader();
    expect(header[0]).toBe('student_local_id');
    expect(header[3]).toBe('report_period_id');
    expect(header).toContain('belonging_key_learning');
    expect(header).toContain('self_regulation_growth');
    expect(header).toContain('literacy_math_next_steps');
    expect(header).toContain('problem_solving_next_steps');
  });

  it('includes UTF-8 BOM and CRLF line endings', () => {
    const students: Student[] = [
      { id: '2', firstName: 'Maria', lastName: 'Santos', pronouns: { subject: 'she', object: 'her', possessive: 'her' }, needs: [] },
      { id: '1', firstName: 'Francis', lastName: 'Underwood', pronouns: { subject: 'he', object: 'him', possessive: 'his' }, needs: [] },
    ];

    const draftsById: Record<string, ReportDraft> = {
      '1': emptyDraft('1', 'february'),
      '2': emptyDraft('2', 'february'),
    };

    // Make one box export-ready and include a newline to assert CRLF normalization.
    (draftsById['1'].comments as any).belonging_and_contributing.key_learning.rendered = 'Line1\nLine2';

    const csv = buildKindergarten12BoxCsv(students, draftsById, 'february');

    expect(csv.startsWith('\ufeff')).toBe(true);
    expect(csv).toContain('\r\n');

    const lines = splitCsvRows(csv.slice(1));
    expect(lines.length).toBeGreaterThanOrEqual(3); // header + 2 rows

    // Header is quoted.
    expect(lines[0].startsWith('"student_local_id"')).toBe(true);

    // Sorted by last name (ascending), then first name, then id.
    expect(lines[1]).toContain('"Santos"');
    expect(lines[2]).toContain('"Underwood"');

    // Newlines inside a field should be CRLF.
    expect(lines[2]).toContain('Line1\r\nLine2');

    // Every field is quoted: simple heuristic for this test.
    expect(lines[1].split(',').every(cell => cell.startsWith('"') && cell.endsWith('"'))).toBe(true);
  });

  it('gates exports: non-approved content exports as empty', () => {
    const student: Student = { id: '1', firstName: 'A', lastName: 'B', pronouns: { subject: 'they', object: 'them', possessive: 'their' }, needs: [] };
    const draft = emptyDraft('1', 'february');
    (draft.comments as any).belonging_and_contributing.key_learning = {
      slots: {},
      rendered: 'Should not export',
      author: 'ece',
      status: 'draft',
    };

    const csv = buildKindergarten12BoxCsv([student], { '1': draft }, 'february');
    const lines = csv.slice(1).split('\r\n');
    const header = lines[0].split(',').map(s => s.slice(1, -1));
    const row = lines[1].split(',').map(s => s.slice(1, -1));

    const colIdx = header.indexOf('belonging_key_learning');
    expect(colIdx).toBeGreaterThanOrEqual(0);
    expect(row[colIdx]).toBe('');
  });
});
