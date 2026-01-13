import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import { Student, FrameId, ReportPeriod, ReportDraft, CommentDraft, SectionId, Template, type UserRole, type DraftStatus, type Tier1ValidationConfig, type RoleLabels } from '../types';
import { dbDeleteStudent, dbGetSetting, dbInit, dbListDrafts, dbListStudents, dbSetSetting, dbUpsertDraft, dbUpsertStudent, type DraftRow } from '../services/db';
import { normalizeDraftMeta } from './roleApproval';
import { loadBoardConfig } from '../configs/boardConfig';

type HistoryEntry = {
  studentId: string;
  frameId: FrameId;
  sectionId: SectionId;
  before: CommentDraft;
  after: CommentDraft;
  ts: number;
};

function cloneCommentDraft(comment: CommentDraft): CommentDraft {
  return {
    templateId: comment.templateId,
    slots: { ...(comment.slots ?? {}) },
    rendered: comment.rendered,
    author: comment.author,
    status: comment.status,
    validation: comment.validation
      ? {
          valid: comment.validation.valid,
          errors: comment.validation.errors ? [...comment.validation.errors] : undefined,
          warnings: comment.validation.warnings ? [...comment.validation.warnings] : undefined,
        }
      : undefined,
  };
}

function sameTemplateAndSlots(a: CommentDraft | undefined, b: CommentDraft | undefined): boolean {
  const at = a?.templateId;
  const bt = b?.templateId;
  if (at !== bt) return false;

  const as = a?.slots ?? {};
  const bs = b?.slots ?? {};
  const aKeys = Object.keys(as);
  const bKeys = Object.keys(bs);
  if (aKeys.length !== bKeys.length) return false;
  for (const k of aKeys) {
    if (!(k in bs)) return false;
    if (String((as as any)[k] ?? '') !== String((bs as any)[k] ?? '')) return false;
  }
  return true;
}

const HISTORY_COALESCE_MS = 1000;
const HISTORY_MAX = 200;

let isApplyingHistory = false;

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

  currentRole: UserRole;
  setCurrentRole: (role: UserRole) => Promise<void>;

  roleLabels: RoleLabels;
  setRoleLabels: (patch: Partial<RoleLabels>) => Promise<void>;
  setDraftStatus: (studentId: string, frameId: FrameId, sectionId: SectionId, status: DraftStatus) => void;

  tier1Validation: Tier1ValidationConfig;
  setTier1Validation: (patch: Partial<Tier1ValidationConfig>) => Promise<void>;

  boardId: string;
  setBoardId: (boardId: string) => Promise<void>;

  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => Promise<void>;

  exportPresetId: 'clipboard' | 'csv_student' | 'csv_class' | 'pdf_student';
  setExportPresetId: (presetId: 'clipboard' | 'csv_student' | 'csv_class' | 'pdf_student') => Promise<void>;

  showDebugLogs: boolean;
  setShowDebugLogs: (show: boolean) => Promise<void>;

  hasOnboarded: boolean;
  completeOnboarding: () => Promise<void>;
  templates: Template[];
  setTemplates: (templates: Template[]) => void;
  drafts: Record<string, ReportDraft>; // studentId -> Draft
  updateComment: (studentId: string, frameId: FrameId, sectionId: SectionId, comment: CommentDraft) => void;

  undoStack: HistoryEntry[];
  redoStack: HistoryEntry[];
  undo: () => void;
  redo: () => void;

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

const DEFAULT_TIER1_VALIDATION: Tier1ValidationConfig = {
  minChars: 100,
  maxChars: 600,
  minSentences: 2,
  maxLineBreaks: 2,
};

const DEFAULT_ROLE_LABELS: RoleLabels = {
  teacher: 'Teacher',
  ece: 'ECE',
};

function coerceRoleLabels(value: unknown): RoleLabels {
  const v = (value && typeof value === 'object') ? (value as any) : {};
  const teacher = typeof v.teacher === 'string' ? v.teacher.trim() : '';
  const ece = typeof v.ece === 'string' ? v.ece.trim() : '';
  return {
    teacher: teacher || DEFAULT_ROLE_LABELS.teacher,
    ece: ece || DEFAULT_ROLE_LABELS.ece,
  };
}

function coerceTier1Validation(value: unknown): Tier1ValidationConfig {
  const v = (value && typeof value === 'object') ? (value as any) : {};
  const toInt = (x: unknown, fallback: number) => {
    const n = typeof x === 'number' ? x : Number(x);
    return Number.isFinite(n) ? Math.max(0, Math.trunc(n)) : fallback;
  };

  const next: Tier1ValidationConfig = {
    minChars: toInt(v.minChars, DEFAULT_TIER1_VALIDATION.minChars),
    maxChars: toInt(v.maxChars, DEFAULT_TIER1_VALIDATION.maxChars),
    minSentences: toInt(v.minSentences, DEFAULT_TIER1_VALIDATION.minSentences),
    maxLineBreaks: toInt(v.maxLineBreaks, DEFAULT_TIER1_VALIDATION.maxLineBreaks),
  };

  // Keep sane ordering without being overly clever.
  if (next.maxChars < next.minChars) {
    next.maxChars = next.minChars;
  }
  if (next.minSentences < 1) {
    next.minSentences = 1;
  }
  return next;
}

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
    renderedText: comment.rendered,
    author: comment.author,
    status: comment.status,
  };
}

export const useAppStore = create<AppState>((set) => ({
  isHydrated: false,
  students: [],
  selectedStudentId: null,
  selectedFrameId: 'belonging_and_contributing',
  currentPeriod: 'february',
  currentRole: 'teacher',
  roleLabels: DEFAULT_ROLE_LABELS,
  tier1Validation: DEFAULT_TIER1_VALIDATION,
  boardId: 'tcdsb',
  theme: 'system',
  exportPresetId: 'clipboard',
  showDebugLogs: false,
  hasOnboarded: false,
  templates: [],
  drafts: {},

  undoStack: [],
  redoStack: [],

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
    const savedRole = await dbGetSetting<UserRole>('currentRole');
    const savedRoleLabels = await dbGetSetting<RoleLabels>('roleLabels');
    const savedTier1Validation = await dbGetSetting<Tier1ValidationConfig>('tier1Validation');
    const savedExportPresetId = await dbGetSetting<AppState['exportPresetId']>('exportPresetId');
    const savedShowDebugLogs = await dbGetSetting<boolean>('showDebugLogs');

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
        rendered: row.renderedText,
        author: row.author ?? 'teacher',
        status: row.status ?? 'approved',
      };
    }

    const exportPresetId =
      savedExportPresetId === 'clipboard' ||
      savedExportPresetId === 'csv_student' ||
      savedExportPresetId === 'csv_class' ||
      savedExportPresetId === 'pdf_student'
        ? savedExportPresetId
        : 'clipboard';

    // Determine tier1Validation: use saved value, or load from board config
    const boardId = savedBoardId ?? 'tcdsb';
    let tier1Validation = coerceTier1Validation(savedTier1Validation ?? undefined);

    // If no saved validation, apply board config defaults
    if (!savedTier1Validation) {
      const config = loadBoardConfig(boardId);
      if (config) {
        tier1Validation = coerceTier1Validation({
          minChars: config.char_limits.per_section_min,
          maxChars: config.char_limits.per_section_max,
          minSentences: 2,
          maxLineBreaks: 2,
        });
      }
    }

    set({
      isHydrated: true,
      students,
      selectedStudentId: students[0]?.id ?? null,
      currentPeriod: period,
      currentRole: savedRole ?? 'teacher',
      roleLabels: coerceRoleLabels(savedRoleLabels ?? undefined),
      tier1Validation,
      boardId,
      theme: savedTheme ?? 'system',
      exportPresetId,
      showDebugLogs: savedShowDebugLogs ?? false,
      hasOnboarded: savedHasOnboarded ?? false,
      drafts: draftsByStudent,
      undoStack: [],
      redoStack: [],
    });
  },

  setShowDebugLogs: async (show) => {
    set({ showDebugLogs: show });
    await dbSetSetting('showDebugLogs', show);
  },

  setExportPresetId: async (presetId) => {
    set({ exportPresetId: presetId });
    await dbSetSetting('exportPresetId', presetId);
  },

  setCurrentPeriod: async (period) => {
    const { students } = useAppStore.getState();

    // Save the new period
    set({ currentPeriod: period });
    await dbSetSetting('currentPeriod', period);

    // Reload drafts for the new period
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
        rendered: row.renderedText,
        author: row.author ?? 'teacher',
        status: row.status ?? 'approved',
      };
    }

    // Clear undo/redo history when switching periods
    set({ drafts: draftsByStudent, undoStack: [], redoStack: [] });
  },

  setCurrentRole: async (role) => {
    set({ currentRole: role });
    await dbSetSetting('currentRole', role);
  },

  setRoleLabels: async (patch) => {
    set((state) => ({
      roleLabels: coerceRoleLabels({ ...state.roleLabels, ...patch }),
    }));
    await dbSetSetting('roleLabels', useAppStore.getState().roleLabels);
  },

  setTier1Validation: async (patch) => {
    set((state) => ({
      tier1Validation: coerceTier1Validation({ ...state.tier1Validation, ...patch }),
    }));
    await dbSetSetting('tier1Validation', useAppStore.getState().tier1Validation);
  },

  setDraftStatus: (studentId, frameId, sectionId, status) => {
    const snapshot = useAppStore.getState();
    const existingDraft = snapshot.drafts[studentId] || emptyDraft(studentId, snapshot.currentPeriod);
    const prev = existingDraft.comments?.[frameId]?.[sectionId] as CommentDraft | undefined;
    if (!prev) return;
    snapshot.updateComment(studentId, frameId, sectionId, { ...prev, status });
  },

  setBoardId: async (boardId) => {
    set({ boardId });
    await dbSetSetting('boardId', boardId);

    // Load board config and apply char limits
    const config = loadBoardConfig(boardId);
    if (config) {
      const newValidation = coerceTier1Validation({
        minChars: config.char_limits.per_section_min,
        maxChars: config.char_limits.per_section_max,
        minSentences: 2,
        maxLineBreaks: 2,
      });
      set({ tier1Validation: newValidation });
      await dbSetSetting('tier1Validation', newValidation);
    }
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
    const snapshot = useAppStore.getState();
    const prevDraft = snapshot.drafts[studentId] || emptyDraft(studentId, snapshot.currentPeriod);
    const prevFrameComments = (prevDraft.comments as any)?.[frameId] || {};
    const prevComment = (prevFrameComments as any)?.[sectionId] as CommentDraft | undefined;

    const meta = normalizeDraftMeta(snapshot.currentRole, prevComment, comment);
    const nextComment: CommentDraft = {
      ...(prevComment ?? { slots: {} }),
      ...comment,
      author: meta.author,
      status: meta.status,
    };

    const historyEntry: HistoryEntry | null =
      !isApplyingHistory && !sameTemplateAndSlots(prevComment, nextComment)
        ? {
            studentId,
            frameId,
            sectionId,
            before: cloneCommentDraft(prevComment ?? { slots: {} }),
            after: cloneCommentDraft(nextComment ?? { slots: {} }),
            ts: Date.now(),
          }
        : null;

    set((state) => {
      const existingDraft = state.drafts[studentId] || emptyDraft(studentId, state.currentPeriod);
      const frameComments = { ...(existingDraft.comments[frameId] || {}) };
      frameComments[sectionId] = nextComment;

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

    if (historyEntry) {
      set((state) => {
        const undoStack = state.undoStack.slice();
        const last = undoStack.length > 0 ? undoStack[undoStack.length - 1] : undefined;
        if (
          last &&
          last.studentId === historyEntry.studentId &&
          last.frameId === historyEntry.frameId &&
          last.sectionId === historyEntry.sectionId &&
          historyEntry.ts - last.ts <= HISTORY_COALESCE_MS
        ) {
          undoStack[undoStack.length - 1] = {
            ...last,
            after: historyEntry.after,
            ts: historyEntry.ts,
          };
        } else {
          undoStack.push(historyEntry);
          if (undoStack.length > HISTORY_MAX) {
            undoStack.splice(0, undoStack.length - HISTORY_MAX);
          }
        }

        return {
          undoStack,
          redoStack: [],
        };
      });
    }

    // Debounced autosave for this single draft row.
    const state = useAppStore.getState();
    const row = toDraftRow(studentId, state.currentPeriod, frameId, sectionId, nextComment);
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
  },

  undo: () => {
    const state = useAppStore.getState();
    const entry = state.undoStack[state.undoStack.length - 1];
    if (!entry) return;

    useAppStore.setState({
      undoStack: state.undoStack.slice(0, -1),
      redoStack: [...state.redoStack, entry],
    });

    try {
      isApplyingHistory = true;
      state.updateComment(entry.studentId, entry.frameId, entry.sectionId, entry.before);
    } finally {
      isApplyingHistory = false;
    }
  },

  redo: () => {
    const state = useAppStore.getState();
    const entry = state.redoStack[state.redoStack.length - 1];
    if (!entry) return;

    useAppStore.setState({
      redoStack: state.redoStack.slice(0, -1),
      undoStack: [...state.undoStack, entry],
    });

    try {
      isApplyingHistory = true;
      state.updateComment(entry.studentId, entry.frameId, entry.sectionId, entry.after);
    } finally {
      isApplyingHistory = false;
    }
  },
}));
