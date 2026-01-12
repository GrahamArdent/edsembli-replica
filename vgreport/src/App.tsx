import { Sidebar } from "./components/Sidebar";
import { Workspace } from "./components/Workspace";
import { Preview } from "./components/Preview";
import { useEffect, useRef, useState } from "react";
import { sidecar } from "./services/sidecar";
import { useAppStore } from "./store/useAppStore";
import { SettingsModal } from "./components/SettingsModal";
import { OnboardingWizard } from "./components/OnboardingWizard";

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
  const [logs, setLogs] = useState<string[]>([]);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const didInit = useRef(false);

  const addLog = (msg: string) => setLogs(prev => [...prev, msg]);

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

        const response = await sidecar.call('list_templates');
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
    const onKeyDown = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();
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
  }, [flushPendingSaves]);

  return (
    <div className="flex w-full h-screen bg-background text-foreground overflow-hidden font-sans relative">
      <SettingsModal open={settingsOpen} onOpenChange={setSettingsOpen} />
      <OnboardingWizard />
      <div className="absolute bottom-0 right-0 p-4 bg-black/90 text-white text-xs max-w-2xl max-h-96 overflow-auto z-50 border-t-2 border-l-2 border-red-500 font-mono shadow-2xl">
        <div className="font-bold mb-2 border-b border-gray-600 pb-1">DEBUG LOGS (Scrollable) — {UI_BUILD_STAMP}</div>
        {logs.map((L, i) => <div key={i} className="whitespace-pre-wrap mb-1 border-b border-gray-800 pb-1">{L}</div>)}
      </div>
      <Sidebar />
      <Workspace />
      <Preview />
    </div>
  );
}

export default App;
