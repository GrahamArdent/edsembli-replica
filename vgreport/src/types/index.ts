export type ReportPeriod = 'initial' | 'february' | 'june';

export type UserRole = 'teacher' | 'ece';

export type RoleLabels = {
  teacher: string;
  ece: string;
};

export type DraftStatus = 'draft' | 'approved';

export type Tier1ValidationConfig = {
  minChars: number;
  maxChars: number;
  minSentences: number;
  maxLineBreaks: number;
};

export interface Student {
  id: string;
  firstName: string;
  lastName: string;
  preferredName?: string;
  pronouns: {
    subject: string; // he/she/they
    object: string;  // him/her/them
    possessive: string; // his/her/their
  };
  needs: string[]; // e.g. "ELL", "IEP"
}

export type FrameId = 'belonging_and_contributing' | 'self_regulation_and_well_being' | 'demonstrating_literacy_and_mathematics_behaviors' | 'problem_solving_and_innovating';

export type SectionId = 'key_learning' | 'growth_in_learning' | 'next_steps_in_learning';

export interface Template {
  id: string;
  frame: string; // e.g. "frame.belonging"
  section: string; // e.g. "key_learning"
  text: string;
  slots: string[];
  tone?: string;
  indicators?: string[];
}

export interface CommentDraft {
  templateId?: string;
  slots: Record<string, string>; // { "evidence": "...", "change": "..." }
  rendered?: string;
  author?: UserRole;
  status?: DraftStatus;
  validation?: {
    valid: boolean;
    errors?: string[];
    warnings?: string[];
  };
}

export interface ReportDraft {
  studentId: string;
  period: ReportPeriod;
  comments: Record<FrameId, Record<SectionId, CommentDraft>>;
}
