import { useState } from 'react';
import { Upload, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { useAppStore } from '../store/useAppStore';
import { parseRosterCsv, generateImportPreview, type ImportPreview } from '../import/parseRosterCsv';

interface RosterImportModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function RosterImportModal({ open, onOpenChange }: RosterImportModalProps) {
  const students = useAppStore((s) => s.students);
  const addStudent = useAppStore((s) => s.addStudent);
  const updateStudent = useAppStore((s) => s.updateStudent);

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [importing, setImporting] = useState(false);
  const [importComplete, setImportComplete] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setPreview(null);
    setParseErrors([]);
    setImportComplete(false);

    try {
      const text = await selectedFile.text();
      const parseResult = parseRosterCsv(text);

      if (parseResult.errors.length > 0) {
        setParseErrors(parseResult.errors);
        return;
      }

      const importPreview = generateImportPreview(parseResult.rows, students);
      setPreview(importPreview);
    } catch (error) {
      setParseErrors([`Failed to read file: ${error}`]);
    }
  };

  const handleImport = async () => {
    if (!preview) return;

    setImporting(true);
    try {
      // Add new students
      for (const student of preview.toAdd) {
        await addStudent({
          firstName: student.firstName,
          lastName: student.lastName,
          preferredName: student.preferredName,
          pronouns: student.pronouns,
          needs: student.needs,
        });
      }

      // Update existing students
      for (const student of preview.toUpdate) {
        await updateStudent(student.id, {
          firstName: student.firstName,
          lastName: student.lastName,
          preferredName: student.preferredName,
          pronouns: student.pronouns,
          needs: student.needs,
        });
      }

      setImportComplete(true);
    } catch (error) {
      setParseErrors([`Import failed: ${error}`]);
    } finally {
      setImporting(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setPreview(null);
    setParseErrors([]);
    setImportComplete(false);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Import Roster from CSV</DialogTitle>
          <DialogDescription>
            Upload a CSV file with student roster data. Required columns: first_name, last_name.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* File picker */}
          <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="csv-upload"
              disabled={importing || importComplete}
            />
            <label
              htmlFor="csv-upload"
              className={`flex flex-col items-center gap-2 cursor-pointer ${
                importing || importComplete ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <Upload size={32} className="text-muted-foreground" />
              <div className="text-sm font-medium">
                {file ? file.name : 'Choose CSV file'}
              </div>
              <div className="text-xs text-muted-foreground">
                or drag and drop
              </div>
            </label>
          </div>

          {/* Parse errors */}
          {parseErrors.length > 0 && (
            <div className="rounded-md border border-destructive bg-destructive/10 p-3">
              <div className="flex items-start gap-2">
                <AlertCircle size={16} className="text-destructive mt-0.5" />
                <div className="flex-1 space-y-1">
                  <div className="text-sm font-medium text-destructive">
                    Parse Errors ({parseErrors.length})
                  </div>
                  <div className="text-xs space-y-0.5 max-h-32 overflow-y-auto">
                    {parseErrors.map((err, i) => (
                      <div key={i}>{err}</div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Import preview */}
          {preview && !importComplete && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-md border border-border bg-green-50 p-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-green-700" />
                    <div className="text-sm font-medium text-green-900">
                      {preview.toAdd.length} to add
                    </div>
                  </div>
                </div>
                <div className="rounded-md border border-border bg-blue-50 p-3">
                  <div className="flex items-center gap-2">
                    <Info size={16} className="text-blue-700" />
                    <div className="text-sm font-medium text-blue-900">
                      {preview.toUpdate.length} to update
                    </div>
                  </div>
                </div>
              </div>

              {/* Warnings */}
              {preview.warnings.length > 0 && (
                <div className="rounded-md border border-amber-200 bg-amber-50 p-3">
                  <div className="flex items-start gap-2">
                    <AlertCircle size={16} className="text-amber-700 mt-0.5" />
                    <div className="flex-1 space-y-1">
                      <div className="text-sm font-medium text-amber-900">
                        Warnings ({preview.warnings.length})
                      </div>
                      <div className="text-xs text-amber-800 space-y-0.5 max-h-24 overflow-y-auto">
                        {preview.warnings.slice(0, 5).map((warn, i) => (
                          <div key={i}>{warn}</div>
                        ))}
                        {preview.warnings.length > 5 && (
                          <div className="text-amber-600">
                            ...and {preview.warnings.length - 5} more
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Preview list */}
              <div className="rounded-md border border-border max-h-48 overflow-y-auto">
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-3 py-2 border-b bg-muted">
                  Preview ({preview.toAdd.length + preview.toUpdate.length} total)
                </div>
                <div className="divide-y">
                  {preview.toAdd.slice(0, 10).map((student, i) => (
                    <div key={i} className="px-3 py-2 text-sm flex items-center gap-2">
                      <span className="text-green-600 text-xs">NEW</span>
                      <span>
                        {student.firstName} {student.lastName}
                      </span>
                      {student.preferredName && (
                        <span className="text-muted-foreground text-xs">
                          ({student.preferredName})
                        </span>
                      )}
                    </div>
                  ))}
                  {preview.toUpdate.slice(0, 10).map((student, i) => (
                    <div key={i} className="px-3 py-2 text-sm flex items-center gap-2">
                      <span className="text-blue-600 text-xs">UPDATE</span>
                      <span>
                        {student.firstName} {student.lastName}
                      </span>
                    </div>
                  ))}
                  {preview.toAdd.length + preview.toUpdate.length > 10 && (
                    <div className="px-3 py-2 text-xs text-muted-foreground">
                      ...and {preview.toAdd.length + preview.toUpdate.length - 10} more
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Import complete */}
          {importComplete && (
            <div className="rounded-md border border-green-200 bg-green-50 p-4 text-center">
              <CheckCircle size={24} className="text-green-600 mx-auto mb-2" />
              <div className="text-sm font-medium text-green-900">
                Import complete!
              </div>
              <div className="text-xs text-green-700 mt-1">
                {preview?.toAdd.length || 0} students added, {preview?.toUpdate.length || 0} updated
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          {!importComplete ? (
            <>
              <Button variant="outline" onClick={handleClose} disabled={importing}>
                Cancel
              </Button>
              <Button
                onClick={handleImport}
                disabled={!preview || preview.toAdd.length + preview.toUpdate.length === 0 || importing}
              >
                {importing ? 'Importing...' : 'Confirm Import'}
              </Button>
            </>
          ) : (
            <Button onClick={handleClose}>Close</Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
