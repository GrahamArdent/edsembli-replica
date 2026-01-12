// vgreport/src/constants.ts
import { FrameId, SectionId } from './types';

export const FRAMES: { id: FrameId; canonicalId: string; label: string; color: string }[] = [
  { id: 'belonging_and_contributing', canonicalId: 'frame.belonging', label: 'Belonging & Contributing', color: 'bg-red-100 text-red-900' },
  { id: 'self_regulation_and_well_being', canonicalId: 'frame.self_regulation', label: 'Self-Reg & Well-Being', color: 'bg-amber-100 text-amber-900' },
  { id: 'demonstrating_literacy_and_mathematics_behaviors', canonicalId: 'frame.literacy_math', label: 'Literacy & Math', color: 'bg-blue-100 text-blue-900' },
  { id: 'problem_solving_and_innovating', canonicalId: 'frame.problem_solving', label: 'Problem Solving', color: 'bg-green-100 text-green-900' },
];

export const SECTIONS: { id: SectionId; label: string }[] = [
  { id: 'key_learning', label: 'Key Learning' },
  { id: 'growth_in_learning', label: 'Growth in Learning' },
  { id: 'next_steps_in_learning', label: 'Next Steps' },
];
