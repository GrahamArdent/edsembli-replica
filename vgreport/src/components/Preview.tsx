import { useAppStore } from '../store/useAppStore';
import { FRAMES } from '../constants';
import { Button } from './ui/button';

function csvEscape(value: unknown): string {
  const s = String(value ?? '');
  const needsQuotes = /[",\n\r]/.test(s);
  const escaped = s.replace(/"/g, '""');
  return needsQuotes ? `"${escaped}"` : escaped;
}

function downloadTextFile(filename: string, content: string, mime = 'text/plain;charset=utf-8'): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function openPrintWindow(title: string, bodyText: string): void {
  const w = window.open('', '_blank');
  if (!w) return;

  const safeText = bodyText
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  w.document.open();
  w.document.write(`<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>${title}</title>
  <style>
    body { font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif; margin: 24px; color: #111; }
    h1 { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; font-size: 18px; margin: 0 0 12px; }
    pre { white-space: pre-wrap; line-height: 1.35; font-size: 12.5px; }
    @media print { body { margin: 16mm; } }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <pre>${safeText}</pre>
  <script>
    window.onload = () => {
      try { window.print(); } catch (e) {}
    };
  </script>
</body>
</html>`);
  w.document.close();
}

export function Preview() {
  const selectedStudentId = useAppStore(state => state.selectedStudentId);
  const student = useAppStore(state => state.students.find(s => s.id === selectedStudentId));
  const students = useAppStore(state => state.students);
  const selectedFrameId = useAppStore(state => state.selectedFrameId);
  const draft = useAppStore(state => (selectedStudentId ? state.drafts[selectedStudentId] : undefined));
  const drafts = useAppStore(state => state.drafts);
  const currentPeriod = useAppStore(state => state.currentPeriod);

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

  const exportStudentCsv = () => {
    if (!student || !selectedStudentId) return;

    const header = ['student_id', 'first_name', 'last_name', 'period', 'frame', 'key_learning', 'growth_in_learning', 'next_steps_in_learning', 'combined'];
    const lines: string[] = [header.join(',')];

    for (const frame of FRAMES) {
      const frameComments = drafts?.[selectedStudentId]?.comments?.[frame.id] || ({} as any);
      const kl = frameComments['key_learning']?.rendered || '';
      const gr = frameComments['growth_in_learning']?.rendered || '';
      const ns = frameComments['next_steps_in_learning']?.rendered || '';
      const combo = [kl, gr, ns].filter(Boolean).join('\n\n');
      lines.push([
        selectedStudentId,
        student.firstName,
        student.lastName,
        currentPeriod,
        frame.id,
        kl,
        gr,
        ns,
        combo,
      ].map(csvEscape).join(','));
    }

    const filename = `vgreport-${currentPeriod}-${student.lastName}_${student.firstName}.csv`;
    downloadTextFile(filename, lines.join('\r\n'), 'text/csv;charset=utf-8');
  };

  const exportClassCsv = () => {
    const header = ['student_id', 'first_name', 'last_name', 'period', 'frame', 'key_learning', 'growth_in_learning', 'next_steps_in_learning', 'combined'];
    const lines: string[] = [header.join(',')];

    for (const s of students) {
      for (const frame of FRAMES) {
        const frameComments = drafts?.[s.id]?.comments?.[frame.id] || ({} as any);
        const kl = frameComments['key_learning']?.rendered || '';
        const gr = frameComments['growth_in_learning']?.rendered || '';
        const ns = frameComments['next_steps_in_learning']?.rendered || '';
        const combo = [kl, gr, ns].filter(Boolean).join('\n\n');

        // Skip fully-empty frames to keep exports tidy.
        if (!kl && !gr && !ns) continue;

        lines.push([
          s.id,
          s.firstName,
          s.lastName,
          currentPeriod,
          frame.id,
          kl,
          gr,
          ns,
          combo,
        ].map(csvEscape).join(','));
      }
    }

    const filename = `vgreport-${currentPeriod}-class.csv`;
    downloadTextFile(filename, lines.join('\r\n'), 'text/csv;charset=utf-8');
  };

  const exportStudentPdf = () => {
    if (!student) return;
    const title = `VGReport — ${student.firstName} ${student.lastName} — ${currentPeriod}`;
    const allFrames = FRAMES.map((f) => {
      const frameComments = draft?.comments?.[f.id] || ({} as any);
      const kl = frameComments['key_learning']?.rendered || '';
      const gr = frameComments['growth_in_learning']?.rendered || '';
      const ns = frameComments['next_steps_in_learning']?.rendered || '';
      const combo = [kl, gr, ns].filter(Boolean).join('\n\n');
      return `== ${f.label} ==\n\n${combo || '(no text yet)'}\n`;
    }).join('\n');

    openPrintWindow(title, allFrames);
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
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={onCopy} disabled={!combined}>Copy</Button>
            <Button size="sm" variant="outline" onClick={exportStudentCsv} disabled={!draft}>CSV (Student)</Button>
            <Button size="sm" variant="outline" onClick={exportClassCsv} disabled={students.length === 0}>CSV (Class)</Button>
            <Button size="sm" variant="outline" onClick={exportStudentPdf} disabled={!draft}>Print/PDF</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
