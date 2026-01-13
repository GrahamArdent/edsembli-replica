// CSV schema for roster import
// Aligns with Student type from ../types.ts

export interface RosterCsvRow {
  // Core identifiers
  student_local_id?: string;  // Optional unique identifier from SIS
  first_name: string;          // Required
  last_name: string;           // Required
  preferred_name?: string;

  // Pronouns (optional, defaults to they/them/their)
  pronouns_subject?: string;   // e.g., "he", "she", "they"
  pronouns_object?: string;    // e.g., "him", "her", "them"
  pronouns_possessive?: string; // e.g., "his", "her", "their"

  // Needs (optional, semicolon-separated)
  // Examples: "IEP", "ELL", "IEP;ELL"
  needs?: string;
}

export const CSV_REQUIRED_HEADERS = ['first_name', 'last_name'];

export const CSV_OPTIONAL_HEADERS = [
  'student_local_id',
  'preferred_name',
  'pronouns_subject',
  'pronouns_object',
  'pronouns_possessive',
  'needs',
];

export const CSV_ALL_HEADERS = [...CSV_REQUIRED_HEADERS, ...CSV_OPTIONAL_HEADERS];
