import { useAppStore } from '../store/useAppStore';
import { FRAMES, SECTIONS } from '../constants';
import { cn } from '../lib/utils';
import { SectionEditor } from './SectionEditor';

export function Workspace() {
  const {
    selectedStudentId,
    students,
    selectedFrameId,
    setSelectedFrameId
  } = useAppStore();

  const student = students.find(s => s.id === selectedStudentId);
  const currentFrame = FRAMES.find(f => f.id === selectedFrameId) || FRAMES[0];

  if (!student) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 text-gray-400">
        Select a student to begin writing
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-white">
      {/* Header */}
      <div className="h-16 border-b border-gray-200 flex items-center px-6 justify-between flex-shrink-0">
        <div>
          <h2 className="text-lg font-bold text-gray-900">
            {student.firstName} {student.lastName}
          </h2>
          <div className="flex gap-2 text-xs text-gray-500">
            <span className="bg-gray-100 px-2 py-0.5 rounded">
              Needs: {student.needs.length > 0 ? student.needs.join(', ') : 'None'}
            </span>
            <span className="bg-gray-100 px-2 py-0.5 rounded">
              Pronouns: {student.pronouns.subject}/{student.pronouns.object}
            </span>
          </div>
        </div>
      </div>

      {/* Frame Tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50 overflow-x-auto flex-shrink-0">
        {FRAMES.map((frame) => (
          <button
            key={frame.id}
            onClick={() => setSelectedFrameId(frame.id)}
            className={cn(
              "px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
              selectedFrameId === frame.id
                ? "border-blue-600 text-blue-700 bg-white"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            )}
          >
            {frame.label}
          </button>
        ))}
      </div>

      {/* Writing Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8 pb-20">
        {SECTIONS.map((section) => (
          <SectionEditor
            key={section.id}
            section={section}
            frameCanonicalId={currentFrame.canonicalId}
            student={student}
          />
        ))}

        <div className="h-20" /> {/* Bottom spacer */}
      </div>
    </div>
  );
}
