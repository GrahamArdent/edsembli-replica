import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import { Student, FrameId, ReportPeriod, ReportDraft, CommentDraft, SectionId, Template } from '../types';

interface AppState {
  // Roster
  students: Student[];
  addStudent: (student: Omit<Student, 'id'>) => void;
  updateStudent: (id: string, updates: Partial<Student>) => void;
  deleteStudent: (id: string) => void;

  // Selection State
  selectedStudentId: string | null;
  selectedFrameId: FrameId;
  setSelectedStudentId: (id: string | null) => void;
  setSelectedFrameId: (id: FrameId) => void;

  // Writing State
  currentPeriod: ReportPeriod;
  templates: Template[];
  setTemplates: (templates: Template[]) => void;
  drafts: Record<string, ReportDraft>; // studentId -> Draft
  updateComment: (studentId: string, frameId: FrameId, sectionId: SectionId, comment: CommentDraft) => void;
}

// Mock Data for Initial Dev
const MOCK_STUDENTS: Student[] = [
  { id: '1', firstName: 'Francis', lastName: 'Underwood', pronouns: { subject: 'he', object: 'him', possessive: 'his' }, needs: [] },
  { id: '2', firstName: 'Maria', lastName: 'Santos', pronouns: { subject: 'she', object: 'her', possessive: 'her' }, needs: ['ELL'] },
  { id: '3', firstName: 'James', lastName: 'Holden', pronouns: { subject: 'they', object: 'them', possessive: 'their' }, needs: ['IEP'] },
];

export const useAppStore = create<AppState>((set) => ({
  students: MOCK_STUDENTS,
  selectedStudentId: '1', // Default to first
  selectedFrameId: 'belonging_and_contributing',
  currentPeriod: 'february',
  templates: [],
  drafts: {},

  setTemplates: (templates) => set({ templates }),

  addStudent: (student) => set((state) => ({
    students: [...state.students, { ...student, id: uuidv4() }]
  })),

  updateStudent: (id, updates) => set((state) => ({
    students: state.students.map(s => s.id === id ? { ...s, ...updates } : s)
  })),

  deleteStudent: (id) => set((state) => ({
    students: state.students.filter(s => s.id !== id)
  })),

  setSelectedStudentId: (id) => set({ selectedStudentId: id }),
  setSelectedFrameId: (id) => set({ selectedFrameId: id }),

  updateComment: (studentId, frameId, sectionId, comment) => set((state) => {
    const existingDraft = state.drafts[studentId] || {
      studentId,
      period: state.currentPeriod,
      comments: {
        belonging_and_contributing: {},
        self_regulation_and_well_being: {},
        demonstrating_literacy_and_mathematics_behaviors: {},
        problem_solving_and_innovating: {} // Initialize if needed
      } as any
    };

    // Deep merge or update logic
    const frameComments = existingDraft.comments[frameId] || {};
    frameComments[sectionId] = comment;

    return {
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
  })
}));
