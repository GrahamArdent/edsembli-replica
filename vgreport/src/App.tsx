import { Sidebar } from "./components/Sidebar";
import { Workspace } from "./components/Workspace";
import { Preview } from "./components/Preview";
import { EvidenceBank } from "./components/EvidenceBank";
import { useEffect, useRef, useState } from "react";
import { sidecar, type ListTemplatesResponse } from "./services/sidecar";
import { useAppStore } from "./store/useAppStore";
import { SettingsModal } from "./components/SettingsModal";
import { OnboardingWizard } from "./components/OnboardingWizard";
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "./components/ui/command";
import { ChevronLeft, ChevronRight } from "lucide-react";

const UI_BUILD_STAMP = "ui-build-2026-01-12T09:05:00Z";

function App() {
  console.log("App Component Rendering...");
  const setTemplates = useAppStore(state => state.setTemplates);
  const hydrateFromDb = useAppStore(state => state.hydrateFromDb);
  const isHydrated = useAppStore(state => state.isHydrated);
  const theme = useAppStore(state => state.theme);
  const flushPendingSaves = useAppStore(state => state.flushPendingSaves);
  const undo = useAppStore(state => state.undo);
  const redo = useAppStore(state => state.redo);
  const students = useAppStore(state => state.students);
  const setSelectedStudentId = useAppStore(state => state.setSelectedStudentId);
  const [logs, setLogs] = useState<string[]>([]);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [evidenceBankOpen, setEvidenceBankOpen] = useState(false);
  const didInit = useRef(false);

  const addLog = (msg: string) =>
    setLogs((prev) => {
      const next = [...prev, msg];
      const MAX = 400;
      return next.length > MAX ? next.slice(next.length - MAX) : next;
    });

  useEffect(() => {
    // React StrictMode runs effects twice in dev; guard to avoid double init/log spam.
    if (didInit.current) return;
    didInit.current = true;

    const offLog = sidecar.onLog(addLog);

    addLog(`UI build: ${UI_BUILD_STAMP} (mode: ${import.meta.env.MODE})`);
    addLog("App mounted, initializing sidecar...");
    (async () => {
      try {
        addLog("Hydrating local SQLite state...");
        await hydrateFromDb();
        addLog("SQLite hydrated.");

        await sidecar.init();
        addLog("Sidecar initialized.");

        try {
          const dbg = await sidecar.call('debug_info');
          addLog(`engine debug_info: ${JSON.stringify(dbg)}`);
        } catch (e: any) {
          addLog(`engine debug_info failed: ${e?.message || JSON.stringify(e)}`);
        }

        const response = await sidecar.call<ListTemplatesResponse>('list_templates');
        try {
          const keys = response && typeof response === 'object' ? Object.keys(response) : [];
          addLog(`list_templates response keys: ${keys.join(', ') || '(none)'}`);
          addLog(`list_templates response preview: ${JSON.stringify(response).slice(0, 300)}`);
        } catch {
          // ignore debug logging errors
        }
        addLog(`Loaded ${response?.templates?.length || 0} templates.`);
        if (response && Array.isArray(response.templates)) {
          setTemplates(response.templates);
        }
      } catch (e: any) {
        console.error("Failed to init sidecar:", e);
        addLog(`Error: ${e?.message || JSON.stringify(e)}`);
      }
    })();

    return () => {
      offLog?.();
    };
  }, [setTemplates, hydrateFromDb]);

  useEffect(() => {
    if (!isHydrated) return;

    const root = document.documentElement;
    const media = window.matchMedia?.("(prefers-color-scheme: dark)");
    const apply = () => {
      const shouldDark = theme === "dark" || (theme === "system" && !!media?.matches);
      root.classList.toggle("dark", shouldDark);
    };

    apply();
    media?.addEventListener?.("change", apply);
    return () => media?.removeEventListener?.("change", apply);
  }, [isHydrated, theme]);

  useEffect(() => {
    const isEditableTarget = (target: EventTarget | null): boolean => {
      const el = target as HTMLElement | null;
      if (!el) return false;
      const tag = (el.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return true;
      if ((el as any).isContentEditable) return true;
      return false;
    };

    const onKeyDown = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();

      if ((e.ctrlKey || e.metaKey) && key === 'k') {
        // Quick search should not steal focus while typing.
        if (isEditableTarget(e.target)) return;
        e.preventDefault();
        setSearchOpen(true);
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        void flushPendingSaves();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === ",") {
        e.preventDefault();
        setSettingsOpen(true);
      }

      if (e.ctrlKey || e.metaKey) {
        // Ctrl+Z / Cmd+Z => undo
        if (key === 'z' && !e.shiftKey) {
          e.preventDefault();
          undo();
        }
        // Ctrl+Y / Cmd+Shift+Z => redo
        if (key === 'y' || (key === 'z' && e.shiftKey)) {
          e.preventDefault();
          redo();
        }
      }
    };
    const onOpenSettings = () => setSettingsOpen(true);
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("open-settings", onOpenSettings);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("open-settings", onOpenSettings);
    };
  }, [flushPendingSaves, undo, redo]);

  return (
    <div className="flex w-full h-screen bg-background text-foreground overflow-hidden font-sans relative">
      <SettingsModal open={settingsOpen} onOpenChange={setSettingsOpen} debugLogs={logs} />
      <CommandDialog open={searchOpen} onOpenChange={setSearchOpen}>
        <CommandInput placeholder="Search students…" autoFocus />
        <CommandList>
          <CommandEmpty>No students found.</CommandEmpty>
          <CommandGroup heading={`Students (${students.length})`}>
            {students.map((s) => (
              <CommandItem
                key={s.id}
                value={`${s.firstName} ${s.lastName} ${s.preferredName ?? ''}`.trim()}
                onSelect={() => {
                  setSelectedStudentId(s.id);
                  setSearchOpen(false);
                }}
              >
                <div className="flex flex-col">
                  <div className="text-sm">{s.firstName} {s.lastName}</div>
                  {s.preferredName ? (
                    <div className="text-xs text-muted-foreground">Preferred: {s.preferredName}</div>
                  ) : null}
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </CommandDialog>
      <OnboardingWizard />
      <Sidebar />
      <Workspace />

      {/* Evidence Bank Toggle */}
      <div className="fixed right-0 top-1/2 z-50 -translate-y-1/2">
        <button
          onClick={() => setEvidenceBankOpen(!evidenceBankOpen)}
          className="rounded-l-md border border-r-0 bg-background p-2 shadow-md hover:bg-accent"
          title="Evidence Bank"
        >
          {evidenceBankOpen ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Evidence Bank Panel */}
      {evidenceBankOpen && (
        <div className="fixed right-0 top-0 z-40 h-screen w-80 border-l bg-background shadow-xl">
          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between border-b p-3">
              <h2 className="text-sm font-semibold">Evidence Bank</h2>
              <button
                onClick={() => setEvidenceBankOpen(false)}
                className="rounded p-1 hover:bg-accent"
              >
                <ChevronRight size={16} />
              </button>
            </div>
            <EvidenceBank />
          </div>
        </div>
      )}
      <Preview />
    </div>
  );
}

export default App;
