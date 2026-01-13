import { useMemo } from 'react';
import type { ReportDraft, ReportPeriod, Student } from '../types';
import { FRAMES, SECTIONS } from '../constants';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { buildClipboardPerBox, buildClipboardPerBoxAll, buildKindergarten12BoxCsv } from '../export/kindergarten';
import { useAppStore } from '../store/useAppStore';

export type ExportPresetId = 'clipboard' | 'csv_student' | 'csv_class' | 'pdf_student';

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

async function writeClipboard(text: string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // ignore; clipboard can be restricted in some WebView contexts
  }
}

export function ExportCenter({
  open,
  onOpenChange,
  student,
  draft,
  students,
  draftsByStudentId,
  currentPeriod,
  onPrintStudent,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  student: Student;
  draft: ReportDraft | undefined;
  students: Student[];
  draftsByStudentId: Record<string, ReportDraft>;
  currentPeriod: ReportPeriod;
  onPrintStudent: () => void;
}) {
  const presetId = useAppStore((s) => s.exportPresetId);
  const setPresetId = useAppStore((s) => s.setExportPresetId);

  const boxes = useMemo(() => {
    return FRAMES.flatMap((frame) =>
      SECTIONS.map((section) => {
        const { text, exportReady } = buildClipboardPerBox(draft, frame.id as any, section.id as any);
        return {
          key: `${frame.id}:${section.id}`,
          heading: `${frame.label} — ${section.label}`,
          text,
          exportReady,
          frameColor: frame.color,
        };
      })
    );
  }, [draft]);

  const missing = useMemo(() => boxes.filter((b) => !b.exportReady).map((b) => b.heading), [boxes]);

  const clipboardAll = useMemo(() => buildClipboardPerBoxAll(draft), [draft]);
  const classCsv = useMemo(
    () => buildKindergarten12BoxCsv(students, draftsByStudentId, currentPeriod),
    [students, draftsByStudentId, currentPeriod]
  );

  const exportStudentCsv = () => {
    const csv = buildKindergarten12BoxCsv([student], { [student.id]: draft as any }, currentPeriod);
    const filename = `vgreport-${currentPeriod}-${student.lastName}_${student.firstName}-12box.csv`;
    downloadTextFile(filename, csv, 'text/csv;charset=utf-8');
  };

  const exportClassCsv = () => {
    const filename = `vgreport-${currentPeriod}-class-12box.csv`;
    downloadTextFile(filename, classCsv, 'text/csv;charset=utf-8');
  };

  const selectPreset = (id: ExportPresetId) => {
    void setPresetId(id);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[760px]">
        <DialogHeader>
          <DialogTitle>Export Center</DialogTitle>
          <DialogDescription>
            Kindergarten golden exports: clipboard-per-box and 12-box CSV. Export gating applies (approved + non-empty + no blocking render errors).
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-wrap gap-2">
          <Button size="sm" variant={presetId === 'clipboard' ? 'default' : 'outline'} onClick={() => selectPreset('clipboard')}>
            Clipboard
          </Button>
          <Button size="sm" variant={presetId === 'csv_student' ? 'default' : 'outline'} onClick={() => selectPreset('csv_student')}>
            CSV (Student)
          </Button>
          <Button size="sm" variant={presetId === 'csv_class' ? 'default' : 'outline'} onClick={() => selectPreset('csv_class')}>
            CSV (Class)
          </Button>
          <Button size="sm" variant={presetId === 'pdf_student' ? 'default' : 'outline'} onClick={() => selectPreset('pdf_student')}>
            Print/PDF
          </Button>
        </div>

        {presetId === 'clipboard' && (
          <div className="space-y-4">
            <div className="rounded-md border border-border bg-muted/30 p-3">
              <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Clipboard-per-box</div>
              <div className="text-sm mt-1">Copy individual boxes as plain text (CRLF newlines). No headings/metadata.</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3">
                {boxes.map((b) => (
                  <div key={b.key} className={`rounded border border-border p-2 ${b.frameColor}`}>
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-[11px] font-medium truncate" title={b.heading}>
                        {b.heading}
                      </div>
                      <Button size="sm" variant="outline" onClick={() => void writeClipboard(b.text)} disabled={!b.exportReady}>
                        Copy
                      </Button>
                    </div>
                    {!b.exportReady && <div className="text-[11px] text-amber-700 mt-1">Not export-ready (blank/unapproved/invalid).</div>}
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-md border border-border bg-muted/30 p-3">
              <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Copy all (optional)</div>
              <div className="text-sm mt-1">Copies all 12 boxes with headings for sequential pasting.</div>
              {missing.length > 0 && (
                <div className="text-xs text-amber-700 mt-2">{missing.length} boxes are not export-ready and will be blank.</div>
              )}
              <div className="flex gap-2 mt-3">
                <Button size="sm" variant="default" onClick={() => void writeClipboard(clipboardAll.text)}>
                  Copy all 12 boxes
                </Button>
              </div>
            </div>
          </div>
        )}

        {presetId === 'csv_student' && (
          <div className="rounded-md border border-border bg-muted/30 p-3">
            <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">12-box CSV (Student)</div>
            <div className="text-sm mt-1">UTF-8 BOM + CRLF + stable column order + always-quoted fields.</div>
            <div className="flex gap-2 mt-3">
              <Button size="sm" variant="outline" onClick={exportStudentCsv} disabled={!draft}>
                Download
              </Button>
            </div>
          </div>
        )}

        {presetId === 'csv_class' && (
          <div className="rounded-md border border-border bg-muted/30 p-3">
            <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">12-box CSV (Class)</div>
            <div className="text-sm mt-1">UTF-8 BOM + CRLF + stable column order + always-quoted fields.</div>
            <div className="flex gap-2 mt-3">
              <Button size="sm" variant="outline" onClick={exportClassCsv} disabled={students.length === 0}>
                Download
              </Button>
            </div>
          </div>
        )}

        {presetId === 'pdf_student' && (
          <div className="rounded-md border border-border bg-muted/30 p-3">
            <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Print / PDF</div>
            <div className="text-sm mt-1">Opens a print-friendly window for the current student.</div>
            <div className="flex gap-2 mt-3">
              <Button size="sm" variant="outline" onClick={onPrintStudent} disabled={!draft}>
                Print/PDF
              </Button>
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
