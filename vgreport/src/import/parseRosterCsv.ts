import Papa from 'papaparse';
import type { RosterCsvRow } from './rosterCsvSchema';
import type { Student } from '../types';

export interface ParsedRosterResult {
  rows: RosterCsvRow[];
  errors: string[];
  warnings: string[];
}

export interface ImportPreview {
  toAdd: Student[];
  toUpdate: Student[];
  errors: string[];
  warnings: string[];
}

/**
 * Parse CSV text into validated RosterCsvRow objects.
 * Handles UTF-8 BOM, CRLF, quoted fields.
 */
export function parseRosterCsv(csvText: string): ParsedRosterResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const rows: RosterCsvRow[] = [];

  // Remove UTF-8 BOM if present
  const cleanText = csvText.replace(/^\uFEFF/, '');

  const parseResult = Papa.parse<Record<string, string>>(cleanText, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header: string) => header.trim().toLowerCase(),
  });

  if (parseResult.errors.length > 0) {
    parseResult.errors.forEach((err) => {
      errors.push(`Row ${err.row ?? '?'}: ${err.message}`);
    });
  }

  // Validate headers
  const headers = parseResult.meta.fields || [];
  const missingRequired = ['first_name', 'last_name'].filter(
    (h) => !headers.includes(h)
  );
  if (missingRequired.length > 0) {
    errors.push(`Missing required columns: ${missingRequired.join(', ')}`);
    return { rows: [], errors, warnings };
  }

  // Validate and transform rows
  parseResult.data.forEach((rawRow, index) => {
    const rowNum = index + 2; // +1 for header, +1 for 1-based indexing
    const rowErrors: string[] = [];

    const firstName = rawRow['first_name']?.trim();
    const lastName = rawRow['last_name']?.trim();

    if (!firstName) {
      rowErrors.push(`Row ${rowNum}: Missing first_name`);
    }
    if (!lastName) {
      rowErrors.push(`Row ${rowNum}: Missing last_name`);
    }

    if (rowErrors.length > 0) {
      errors.push(...rowErrors);
      return; // Skip this row
    }

    const row: RosterCsvRow = {
      first_name: firstName,
      last_name: lastName,
    };

    // Optional fields
    if (rawRow['student_local_id']?.trim()) {
      row.student_local_id = rawRow['student_local_id'].trim();
    }
    if (rawRow['preferred_name']?.trim()) {
      row.preferred_name = rawRow['preferred_name'].trim();
    }

    // Pronouns (with validation)
    const subjPronoun = rawRow['pronouns_subject']?.trim().toLowerCase();
    const objPronoun = rawRow['pronouns_object']?.trim().toLowerCase();
    const possPronoun = rawRow['pronouns_possessive']?.trim().toLowerCase();

    if (subjPronoun || objPronoun || possPronoun) {
      // If any pronoun is provided, use them; otherwise defaults will apply
      row.pronouns_subject = subjPronoun || 'they';
      row.pronouns_object = objPronoun || 'them';
      row.pronouns_possessive = possPronoun || 'their';
    }

    // Needs (semicolon-separated)
    if (rawRow['needs']?.trim()) {
      row.needs = rawRow['needs'].trim();
    }

    rows.push(row);
  });

  return { rows, errors, warnings };
}

/**
 * Generate import preview by comparing CSV rows with existing students.
 * Duplicate detection by student_local_id or (first_name + last_name).
 */
export function generateImportPreview(
  csvRows: RosterCsvRow[],
  existingStudents: Student[]
): ImportPreview {
  const toAdd: Student[] = [];
  const toUpdate: Student[] = [];
  const errors: string[] = [];
  const warnings: string[] = [];

  // Build lookup map by name
  const byName = new Map<string, Student>();

  existingStudents.forEach((student) => {
    const nameKey = `${student.firstName.toLowerCase()}|${student.lastName.toLowerCase()}`;
    byName.set(nameKey, student);
    // Note: Student type doesn't have student_local_id, so we can't use it for matching
  });

  csvRows.forEach((row, index) => {
    const rowNum = index + 1;
    const nameKey = `${row.first_name.toLowerCase()}|${row.last_name.toLowerCase()}`;

    // Check for duplicate
    const existingByName = byName.get(nameKey);

    if (existingByName) {
      // Update existing student
      const updatedStudent: Student = {
        ...existingByName,
        firstName: row.first_name,
        lastName: row.last_name,
        preferredName: row.preferred_name || existingByName.preferredName,
        pronouns: {
          subject: row.pronouns_subject || existingByName.pronouns.subject,
          object: row.pronouns_object || existingByName.pronouns.object,
          possessive: row.pronouns_possessive || existingByName.pronouns.possessive,
        },
        needs: row.needs
          ? row.needs.split(';').map((n) => n.trim()).filter(Boolean)
          : existingByName.needs,
      };
      toUpdate.push(updatedStudent);
      warnings.push(
        `Row ${rowNum}: Student "${row.first_name} ${row.last_name}" already exists, will update`
      );
    } else {
      // New student
      const newStudent: Omit<Student, 'id'> = {
        firstName: row.first_name,
        lastName: row.last_name,
        preferredName: row.preferred_name,
        pronouns: {
          subject: row.pronouns_subject || 'they',
          object: row.pronouns_object || 'them',
          possessive: row.pronouns_possessive || 'their',
        },
        needs: row.needs
          ? row.needs.split(';').map((n) => n.trim()).filter(Boolean)
          : [],
      };
      toAdd.push(newStudent as Student); // Will get ID assigned by addStudent
    }
  });

  return { toAdd, toUpdate, errors, warnings };
}
