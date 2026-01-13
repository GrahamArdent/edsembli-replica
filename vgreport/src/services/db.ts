import { invoke } from "@tauri-apps/api/core";
import type { DraftStatus, ReportPeriod, Student, UserRole } from "../types";

export interface DraftRow {
  studentId: string;
  reportPeriodId: string;
  frame: string;
  section: string;
  templateId?: string;
  slotValues: Record<string, unknown>;
  renderedText?: string;
  author?: UserRole;
  status?: DraftStatus;
}

export async function dbInit(): Promise<{ path: string }> {
  const path = await invoke<string>("db_init");
  return { path };
}

export async function dbListStudents(): Promise<Student[]> {
  return await invoke<Student[]>("db_list_students");
}

export async function dbUpsertStudent(student: Student): Promise<void> {
  await invoke<void>("db_upsert_student", { student });
}

export async function dbDeleteStudent(studentId: string): Promise<void> {
  await invoke<void>("db_delete_student", { studentId });
}

export async function dbListDrafts(period: ReportPeriod): Promise<DraftRow[]> {
  return await invoke<DraftRow[]>("db_list_drafts", { reportPeriodId: period });
}

export async function dbUpsertDraft(draft: DraftRow): Promise<void> {
  await invoke<void>("db_upsert_draft", { draft });
}

export async function dbGetSetting<T = unknown>(key: string): Promise<T | null> {
  const value = await invoke<T | null>("db_get_setting", { key });
  return value;
}

export async function dbSetSetting(key: string, value: unknown): Promise<void> {
  await invoke<void>("db_set_setting", { key, value });
}
