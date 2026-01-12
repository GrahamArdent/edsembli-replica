import { useAppStore } from '../store/useAppStore';
import { FRAMES } from '../constants';
import { Button } from './ui/button';

export function Preview() {
  const selectedStudentId = useAppStore(state => state.selectedStudentId);
  const student = useAppStore(state => state.students.find(s => s.id === selectedStudentId));
  const selectedFrameId = useAppStore(state => state.selectedFrameId);
  const draft = useAppStore(state => (selectedStudentId ? state.drafts[selectedStudentId] : undefined));

  if (!student) return null;

  const currentFrameLabel = FRAMES.find(f => f.id === selectedFrameId)?.label;

  const frameComments = draft?.comments?.[selectedFrameId] || ({} as any);
  const keyLearning = frameComments['key_learning']?.rendered || '';
  const growth = frameComments['growth_in_learning']?.rendered || '';
  const nextSteps = frameComments['next_steps_in_learning']?.rendered || '';
  const combined = [keyLearning, growth, nextSteps].filter(Boolean).join('\n\n');
  const charCount = combined.length;

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(combined);
    } catch {
      // ignore; clipboard can be restricted in some WebView contexts
    }
  };

  return (
    <div className="w-80 border-l border-border bg-muted flex flex-col h-screen hidden lg:flex">
      <div className="p-4 border-b border-border bg-background">
        <h3 className="text-sm font-bold uppercase">Live Preview</h3>
        <p className="text-xs text-muted-foreground mt-1">
          {currentFrameLabel}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="bg-background border border-border shadow-sm p-4 rounded-md min-h-[500px]">
          <div className="prose prose-sm font-serif">
            <h4 className="text-blue-700 border-b border-blue-200/40 pb-1 mb-2">
              {currentFrameLabel}
            </h4>

            <p className="text-foreground leading-relaxed mb-4">
              {keyLearning ? keyLearning : <span className="text-muted-foreground italic">[Key Learning will appear here]</span>}
            </p>

            <p className="text-foreground leading-relaxed mb-4">
              {growth ? growth : <span className="text-muted-foreground italic">[Growth will appear here]</span>}
            </p>

            <p className="text-foreground leading-relaxed">
              {nextSteps ? nextSteps : <span className="text-muted-foreground italic">[Next Steps will appear here]</span>}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div>Character Count: {charCount} / 1500</div>
          <Button size="sm" variant="outline" onClick={onCopy} disabled={!combined}>Copy</Button>
        </div>
      </div>
    </div>
  );
}
