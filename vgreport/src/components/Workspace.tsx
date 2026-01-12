import { useAppStore } from '../store/useAppStore';
import { FRAMES, SECTIONS } from '../constants';
import { cn } from '../lib/utils';
import { SectionEditor } from './SectionEditor';
import { Button } from './ui/button';
import { Redo2, Undo2 } from 'lucide-react';

export function Workspace() {
  const {
    selectedStudentId,
    students,
    selectedFrameId,
    setSelectedFrameId,
    saveStatus,
    lastSavedAt,
    lastSaveError,
    undo,
    redo,
    undoStack,
    redoStack,
  } = useAppStore();

  const student = students.find(s => s.id === selectedStudentId);
  const currentFrame = FRAMES.find(f => f.id === selectedFrameId) || FRAMES[0];

  if (!student) {
    return (
      <div className="flex-1 flex items-center justify-center bg-muted text-muted-foreground">
        Select a student to begin writing
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-background">
      {/* Header */}
      <div className="h-16 border-b border-border flex items-center px-6 justify-between flex-shrink-0">
        <div>
          <h2 className="text-lg font-bold text-foreground">
            {student.firstName} {student.lastName}
          </h2>
          <div className="flex gap-2 text-xs text-muted-foreground">
            <span className="bg-muted px-2 py-0.5 rounded">
              Needs: {student.needs.length > 0 ? student.needs.join(', ') : 'None'}
            </span>
            <span className="bg-muted px-2 py-0.5 rounded">
              Pronouns: {student.pronouns.subject}/{student.pronouns.object}
            </span>
          </div>
        </div>

        <div className="text-xs text-gray-500 flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.dispatchEvent(new Event('open-settings'))}
          >
            Settings
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => undo()}
            disabled={undoStack.length === 0}
            title={undoStack.length === 0 ? 'Nothing to undo' : 'Undo (Ctrl+Z)'}
          >
            <Undo2 className="h-4 w-4 mr-1" /> Undo
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => redo()}
            disabled={redoStack.length === 0}
            title={redoStack.length === 0 ? 'Nothing to redo' : 'Redo (Ctrl+Y)'}
          >
            <Redo2 className="h-4 w-4 mr-1" /> Redo
          </Button>
          {saveStatus === 'saving' && <span className="text-blue-700">Saving…</span>}
          {saveStatus === 'saved' && <span className="text-green-700">Saved</span>}
          {saveStatus === 'error' && <span className="text-red-700">Save failed</span>}
          {lastSavedAt && saveStatus !== 'saving' && (
            <span className="text-gray-400">{new Date(lastSavedAt).toLocaleTimeString()}</span>
          )}
          {saveStatus === 'error' && lastSaveError && (
            <span className="text-red-500 max-w-[260px] truncate" title={lastSaveError}>{lastSaveError}</span>
          )}
        </div>
      </div>

      {/* Frame Tabs */}
      <div className="flex border-b border-border bg-muted overflow-x-auto flex-shrink-0">
        {FRAMES.map((frame) => (
          <button
            key={frame.id}
            onClick={() => setSelectedFrameId(frame.id)}
            className={cn(
              "px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
              selectedFrameId === frame.id
                ? "border-blue-600 text-blue-700 bg-background"
                : "border-transparent text-muted-foreground hover:text-foreground hover:bg-background/60"
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
            frameId={selectedFrameId}
            frameCanonicalId={currentFrame.canonicalId}
            student={student}
          />
        ))}

        <div className="h-20" /> {/* Bottom spacer */}
      </div>
    </div>
  );
}
