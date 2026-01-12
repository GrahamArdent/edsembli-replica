import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import { Student, FrameId, ReportPeriod, ReportDraft, CommentDraft, SectionId, Template } from '../types';
import { dbDeleteStudent, dbGetSetting, dbInit, dbListDrafts, dbListStudents, dbSetSetting, dbUpsertDraft, dbUpsertStudent, type DraftRow } from '../services/db';

interface AppState {
  // App Init
  isHydrated: boolean;
  hydrateFromDb: () => Promise<void>;

  // Roster
  students: Student[];
  addStudent: (student: Omit<Student, 'id'>) => Promise<void>;
  updateStudent: (id: string, updates: Partial<Student>) => Promise<void>;
  deleteStudent: (id: string) => Promise<void>;

  // Selection State
  selectedStudentId: string | null;
  selectedFrameId: FrameId;
  setSelectedStudentId: (id: string | null) => void;
  setSelectedFrameId: (id: FrameId) => void;

  // Writing State
  currentPeriod: ReportPeriod;
  setCurrentPeriod: (period: ReportPeriod) => Promise<void>;

  boardId: string;
  setBoardId: (boardId: string) => Promise<void>;

  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => Promise<void>;

  hasOnboarded: boolean;
  completeOnboarding: () => Promise<void>;
  templates: Template[];
  setTemplates: (templates: Template[]) => void;
  drafts: Record<string, ReportDraft>; // studentId -> Draft
  updateComment: (studentId: string, frameId: FrameId, sectionId: SectionId, comment: CommentDraft) => void;

  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
  lastSavedAt: number | null;
  lastSaveError: string | null;

  flushPendingSaves: () => Promise<void>;
}

// Mock Data for Initial Dev
const MOCK_STUDENTS: Student[] = [
  { id: '1', firstName: 'Francis', lastName: 'Underwood', pronouns: { subject: 'he', object: 'him', possessive: 'his' }, needs: [] },
  { id: '2', firstName: 'Maria', lastName: 'Santos', pronouns: { subject: 'she', object: 'her', possessive: 'her' }, needs: ['ELL'] },
  { id: '3', firstName: 'James', lastName: 'Holden', pronouns: { subject: 'they', object: 'them', possessive: 'their' }, needs: ['IEP'] },
];

const saveTimers = new Map<string, { timer: number; row: DraftRow }>();

function emptyDraft(studentId: string, period: ReportPeriod): ReportDraft {
  return {
    studentId,
    period,
    comments: {
      belonging_and_contributing: {},
      self_regulation_and_well_being: {},
      demonstrating_literacy_and_mathematics_behaviors: {},
      problem_solving_and_innovating: {}
    } as any
  };
}

function draftKey(row: DraftRow): string {
  return `${row.studentId}:${row.reportPeriodId}:${row.frame}:${row.section}`;
}

function toDraftRow(
  studentId: string,
  period: ReportPeriod,
  frameId: FrameId,
  sectionId: SectionId,
  comment: CommentDraft
): DraftRow {
  return {
    studentId,
    reportPeriodId: period,
    frame: frameId,
    section: sectionId,
    templateId: comment.templateId,
    slotValues: comment.slots ?? {},
    renderedText: comment.rendered
  };
}

export const useAppStore = create<AppState>((set) => ({
  isHydrated: false,
  students: [],
  selectedStudentId: null,
  selectedFrameId: 'belonging_and_contributing',
  currentPeriod: 'february',
  boardId: 'tcdsb',
  theme: 'system',
  hasOnboarded: false,
  templates: [],
  drafts: {},

  saveStatus: 'idle',
  lastSavedAt: null,
  lastSaveError: null,

  flushPendingSaves: async () => {
    const pending = Array.from(saveTimers.values());
    for (const entry of pending) {
      window.clearTimeout(entry.timer);
    }
    saveTimers.clear();

    if (pending.length === 0) return;
    useAppStore.setState({ saveStatus: 'saving', lastSaveError: null });
    try {
      await Promise.all(pending.map(p => dbUpsertDraft(p.row)));
      useAppStore.setState({ saveStatus: 'saved', lastSavedAt: Date.now(), lastSaveError: null });
    } catch (e: any) {
      useAppStore.setState({ saveStatus: 'error', lastSaveError: e?.message || String(e) });
    }
  },

  setTemplates: (templates) => set({ templates }),

  hydrateFromDb: async () => {
    await dbInit();

    const savedBoardId = await dbGetSetting<string>('boardId');
    const savedTheme = await dbGetSetting<'light' | 'dark' | 'system'>('theme');
    const savedPeriod = await dbGetSetting<ReportPeriod>('currentPeriod');
    const savedHasOnboarded = await dbGetSetting<boolean>('hasOnboarded');

    let students = await dbListStudents();
    if (students.length === 0) {
      // Seed initial demo data on first run.
      await Promise.all(MOCK_STUDENTS.map(s => dbUpsertStudent(s)));
      students = await dbListStudents();
    }

    const period: ReportPeriod = savedPeriod ?? 'february';
    const rows = await dbListDrafts(period);

    const draftsByStudent: Record<string, ReportDraft> = {};
    for (const student of students) {
      draftsByStudent[student.id] = emptyDraft(student.id, period);
    }

    for (const row of rows) {
      const studentDraft = draftsByStudent[row.studentId] ?? emptyDraft(row.studentId, period);
      draftsByStudent[row.studentId] = studentDraft;

      const frame = row.frame as FrameId;
      const section = row.section as SectionId;
      const slots = (row.slotValues ?? {}) as Record<string, string>;

      studentDraft.comments[frame] = studentDraft.comments[frame] || ({} as any);
      studentDraft.comments[frame][section] = {
        templateId: row.templateId,
        slots,
        rendered: row.renderedText
      };
    }

    set({
      isHydrated: true,
      students,
      selectedStudentId: students[0]?.id ?? null,
      currentPeriod: period,
      boardId: savedBoardId ?? 'tcdsb',
      theme: savedTheme ?? 'system',
      hasOnboarded: savedHasOnboarded ?? false,
      drafts: draftsByStudent
    });
  },

  setCurrentPeriod: async (period) => {
    set({ currentPeriod: period });
    await dbSetSetting('currentPeriod', period);
  },

  setBoardId: async (boardId) => {
    set({ boardId });
    await dbSetSetting('boardId', boardId);
  },

  setTheme: async (theme) => {
    set({ theme });
    await dbSetSetting('theme', theme);
  },

  completeOnboarding: async () => {
    set({ hasOnboarded: true });
    await dbSetSetting('hasOnboarded', true);
  },

  addStudent: async (student) => {
    const newStudent: Student = { ...student, id: uuidv4() };
    set((state) => ({
      students: [...state.students, newStudent],
      drafts: {
        ...state.drafts,
        [newStudent.id]: emptyDraft(newStudent.id, state.currentPeriod)
      }
    }));
    await dbUpsertStudent(newStudent);
  },

  updateStudent: async (id, updates) => {
    let updated: Student | null = null;
    set((state) => {
      const students = state.students.map(s => {
        if (s.id !== id) return s;
        updated = { ...s, ...updates };
        return updated;
      });
      return { students };
    });

    if (updated) {
      await dbUpsertStudent(updated);
    }
  },

  deleteStudent: async (id) => {
    set((state) => {
      const remaining = state.students.filter(s => s.id !== id);
      const nextSelected = state.selectedStudentId === id ? (remaining[0]?.id ?? null) : state.selectedStudentId;
      const nextDrafts = { ...state.drafts };
      delete nextDrafts[id];
      return {
        students: remaining,
        selectedStudentId: nextSelected,
        drafts: nextDrafts,
      };
    });
    await dbDeleteStudent(id);
  },

  setSelectedStudentId: (id) => set({ selectedStudentId: id }),
  setSelectedFrameId: (id) => set({ selectedFrameId: id }),

  updateComment: (studentId, frameId, sectionId, comment) => {
    set((state) => {
      const existingDraft = state.drafts[studentId] || emptyDraft(studentId, state.currentPeriod);
      const frameComments = { ...(existingDraft.comments[frameId] || {}) };
      frameComments[sectionId] = comment;

      return {
        saveStatus: 'saving',
        lastSaveError: null,
        drafts: {
          ...state.drafts,
          [studentId]: {
            ...existingDraft,
            comments: {
              ...existingDraft.comments,
              [frameId]: frameComments
            }
          }
        }
      };
    });

    // Debounced autosave for this single draft row.
    const state = useAppStore.getState();
    const row = toDraftRow(studentId, state.currentPeriod, frameId, sectionId, comment);
    const key = draftKey(row);

    const existingTimer = saveTimers.get(key);
    if (existingTimer) {
      window.clearTimeout(existingTimer.timer);
    }

    const timer = window.setTimeout(async () => {
      try {
        await dbUpsertDraft(row);
        useAppStore.setState({ saveStatus: 'saved', lastSavedAt: Date.now(), lastSaveError: null });
      } catch (e: any) {
        useAppStore.setState({ saveStatus: 'error', lastSaveError: e?.message || String(e) });
      } finally {
        saveTimers.delete(key);
      }
    }, 650);
    saveTimers.set(key, { timer, row });
  }
}));
