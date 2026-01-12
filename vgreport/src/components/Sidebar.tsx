import { useAppStore } from '../store/useAppStore';
import { Pencil, Trash2 } from 'lucide-react';
import { cn } from '../lib/utils'; // Assuming this exists from shadcn init
import { useMemo, useState } from 'react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { FRAMES, SECTIONS } from '../constants';

export function Sidebar() {
  const {
    students,
    selectedStudentId,
    setSelectedStudentId,
    addStudent,
    updateStudent,
    deleteStudent,
    drafts,
  } = useAppStore();
  const [open, setOpen] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  const [editOpen, setEditOpen] = useState(false);
  const [editStudentId, setEditStudentId] = useState<string | null>(null);
  const [editFirstName, setEditFirstName] = useState('');
  const [editLastName, setEditLastName] = useState('');

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteStudentId, setDeleteStudentId] = useState<string | null>(null);

  const canCreate = useMemo(() => firstName.trim().length > 0 && lastName.trim().length > 0, [firstName, lastName]);

  const onCreate = async () => {
    if (!canCreate) return;
    await addStudent({
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      pronouns: { subject: 'they', object: 'them', possessive: 'their' },
      needs: []
    });
    setFirstName('');
    setLastName('');
    setOpen(false);
  };

  const openEdit = (studentId: string) => {
    const student = students.find(s => s.id === studentId);
    if (!student) return;
    setEditStudentId(studentId);
    setEditFirstName(student.firstName);
    setEditLastName(student.lastName);
    setEditOpen(true);
  };

  const onEditSave = async () => {
    if (!editStudentId) return;
    const fn = editFirstName.trim();
    const ln = editLastName.trim();
    if (!fn || !ln) return;
    await updateStudent(editStudentId, { firstName: fn, lastName: ln });
    setEditOpen(false);
    setEditStudentId(null);
  };

  const openDelete = (studentId: string) => {
    setDeleteStudentId(studentId);
    setDeleteOpen(true);
  };

  const onConfirmDelete = async () => {
    if (!deleteStudentId) return;
    await deleteStudent(deleteStudentId);
    setDeleteOpen(false);
    setDeleteStudentId(null);
  };

  const computeFrameCompletion = (studentId: string, frameId: string) => {
    const studentDraft = drafts[studentId];
    const frameComments = (studentDraft?.comments as any)?.[frameId] || {};
    return SECTIONS.every(s => {
      const rendered = frameComments?.[s.id]?.rendered;
      return typeof rendered === 'string' && rendered.trim().length > 0;
    });
  };

  return (
    <div className="w-64 border-r border-border bg-muted h-screen flex flex-col">
      <div className="p-4 border-b border-border bg-background">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <span className="bg-blue-600 text-white p-1 rounded">VG</span> Report
        </h1>
        <p className="text-xs text-muted-foreground mt-1">Kindergarten CoL Writer</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 py-2">
          Classroom ({students.length})
        </div>

        {students.map((student) => {
          const isSelected = selectedStudentId === student.id;
          const completedFrames = FRAMES.reduce((acc, f) => acc + (computeFrameCompletion(student.id, f.id) ? 1 : 0), 0);
          return (
            <button
              key={student.id}
              onClick={() => setSelectedStudentId(student.id)}
              className={cn(
                "w-full text-left px-3 py-2 rounded-md flex items-center gap-3 transition-colors",
                isSelected
                  ? "bg-blue-100 text-blue-900 ring-1 ring-blue-200"
                  : "hover:bg-accent text-foreground"
              )}
            >
              <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                isSelected ? "bg-blue-600 text-white" : "bg-gray-300 text-gray-600"
              )}>
                {student.firstName[0]}{student.lastName[0]}
              </div>

              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">
                  {student.firstName} {student.lastName}
                </div>
                <div className="text-xs text-muted-foreground flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1">
                    {FRAMES.map((f) => {
                      const complete = computeFrameCompletion(student.id, f.id);
                      return (
                        <span
                          key={f.id}
                          className={cn(
                            "inline-block w-2.5 h-2.5 rounded-full ring-1 ring-gray-300",
                            complete ? "bg-green-500 ring-green-600" : "bg-gray-200"
                          )}
                          title={f.label}
                        />
                      );
                    })}
                  </div>
                  <span className="text-muted-foreground">{completedFrames}/4 Frames</span>
                </div>
              </div>

              <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => openEdit(student.id)}
                  aria-label="Edit student"
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-red-700 hover:text-red-800"
                  onClick={() => openDelete(student.id)}
                  aria-label="Delete student"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </button>
          );
        })}
      </div>

      <div className="p-4 border-t border-border bg-background">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="w-full" variant="default">Add Student</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Student</DialogTitle>
            </DialogHeader>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">First name</label>
                <input
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  placeholder="e.g. Francis"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Last name</label>
                <input
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  placeholder="e.g. Underwood"
                />
              </div>
              <p className="text-xs text-gray-500">Pronouns and needs can be edited later.</p>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button disabled={!canCreate} onClick={onCreate}>Create</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Edit Student */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Student</DialogTitle>
          </DialogHeader>

          <div className="space-y-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-700">First name</label>
              <input
                value={editFirstName}
                onChange={(e) => setEditFirstName(e.target.value)}
                className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-700">Last name</label>
              <input
                value={editLastName}
                onChange={(e) => setEditLastName(e.target.value)}
                className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button onClick={onEditSave} disabled={!editStudentId || !editFirstName.trim() || !editLastName.trim()}>
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Student */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Student</DialogTitle>
          </DialogHeader>

          <div className="text-sm text-gray-700">
            This will remove the student and their drafts from this device.
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>Cancel</Button>
            <Button variant="destructive" onClick={onConfirmDelete} disabled={!deleteStudentId}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
