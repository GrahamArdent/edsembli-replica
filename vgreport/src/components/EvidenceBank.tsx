import { useState, useEffect } from "react";
import { Plus, X, Search } from "lucide-react";
import { dbListEvidence, dbAddEvidence, dbDeleteEvidence } from "../services/db";
import type { EvidenceSnippet } from "../types/evidence";
import { useAppStore } from "../store/useAppStore";

export function EvidenceBank() {
  const selectedStudentId = useAppStore((s) => s.selectedStudentId);
  const students = useAppStore((s) => s.students);
  const selectedStudent = students.find(s => s.id === selectedStudentId);
  const [evidence, setEvidence] = useState<EvidenceSnippet[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [newText, setNewText] = useState("");
  const [newTags, setNewTags] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEvidence();
  }, [selectedStudent]);

  async function loadEvidence() {
    if (!selectedStudent) return;
    try {
      const items = await dbListEvidence(selectedStudent.id);
      setEvidence(items);
    } catch (error) {
      console.error("Failed to load evidence:", error);
    }
  }

  async function handleAdd() {
    if (!selectedStudent || !newText.trim()) return;
    setLoading(true);
    try {
      const tags = newTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      await dbAddEvidence(selectedStudent.id, newText.trim(), tags);
      setNewText("");
      setNewTags("");
      await loadEvidence();
    } catch (error) {
      console.error("Failed to add evidence:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await dbDeleteEvidence(id);
      await loadEvidence();
    } catch (error) {
      console.error("Failed to delete evidence:", error);
    }
  }

  function handleInsert(text: string) {
    // Dispatch custom event for SectionEditor to listen to
    window.dispatchEvent(
      new CustomEvent("insert-evidence", { detail: { text } })
    );
  }

  const filtered = evidence.filter((item) =>
    item.text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!selectedStudent) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        Select a student to view evidence snippets.
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Quick Add Form */}
      <div className="border-b p-3">
        <div className="mb-2 text-sm font-medium">Quick Add Evidence</div>
        <textarea
          className="mb-2 w-full rounded border p-2 text-sm"
          placeholder="Observation text..."
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
          rows={2}
        />
        <input
          className="mb-2 w-full rounded border p-2 text-sm"
          placeholder="Tags (comma-separated)"
          value={newTags}
          onChange={(e) => setNewTags(e.target.value)}
        />
        <button
          className="flex items-center gap-1 rounded bg-primary px-3 py-1 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          onClick={handleAdd}
          disabled={loading || !newText.trim()}
        >
          <Plus size={14} />
          Add
        </button>
      </div>

      {/* Search */}
      <div className="border-b p-3">
        <div className="relative">
          <Search className="absolute left-2 top-2 text-muted-foreground" size={14} />
          <input
            className="w-full rounded border py-1 pl-8 pr-2 text-sm"
            placeholder="Search evidence..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Evidence List */}
      <div className="flex-1 overflow-y-auto p-3">
        {filtered.length === 0 ? (
          <div className="text-sm text-muted-foreground">No evidence snippets yet.</div>
        ) : (
          <div className="space-y-2">
            {filtered.map((item) => (
              <div
                key={item.id}
                className="group rounded border bg-card p-2 text-sm hover:bg-accent"
              >
                <div className="mb-1 flex items-start justify-between gap-2">
                  <div className="flex-1">{item.text}</div>
                  <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    <button
                      className="rounded bg-primary px-2 py-0.5 text-xs text-primary-foreground hover:bg-primary/90"
                      onClick={() => handleInsert(item.text)}
                    >
                      Insert
                    </button>
                    <button
                      className="rounded bg-destructive px-1 py-0.5 text-destructive-foreground hover:bg-destructive/90"
                      onClick={() => handleDelete(item.id)}
                    >
                      <X size={12} />
                    </button>
                  </div>
                </div>
                {item.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {item.tags.map((tag, i) => (
                      <span
                        key={i}
                        className="rounded bg-muted px-1.5 py-0.5 text-xs text-muted-foreground"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
