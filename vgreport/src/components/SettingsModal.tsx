import { useMemo } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { useAppStore } from "../store/useAppStore";
import type { ReportPeriod, UserRole } from "../types";
import { loadBoardConfig } from "../configs/boardConfig";

const BOARDS = [
  { id: "tcdsb", label: "TCDSB" },
  { id: "ncdsb", label: "NCDSB" },
];

const PERIODS: { id: ReportPeriod; label: string }[] = [
  { id: "initial", label: "Initial Observations" },
  { id: "february", label: "February" },
  { id: "june", label: "June" },
];

export function SettingsModal({
  open,
  onOpenChange,
  debugLogs,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  debugLogs: string[];
}) {
  const boardId = useAppStore(s => s.boardId);
  const setBoardId = useAppStore(s => s.setBoardId);
  const theme = useAppStore(s => s.theme);
  const setTheme = useAppStore(s => s.setTheme);
  const currentPeriod = useAppStore(s => s.currentPeriod);
  const setCurrentPeriod = useAppStore(s => s.setCurrentPeriod);

  const currentRole = useAppStore(s => s.currentRole);
  const setCurrentRole = useAppStore(s => s.setCurrentRole);

  const roleLabels = useAppStore(s => s.roleLabels);
  const setRoleLabels = useAppStore(s => s.setRoleLabels);

  const tier1Validation = useAppStore(s => s.tier1Validation);
  const setTier1Validation = useAppStore(s => s.setTier1Validation);

  const showDebugLogs = useAppStore(s => s.showDebugLogs);
  const setShowDebugLogs = useAppStore(s => s.setShowDebugLogs);

  const boardLabel = useMemo(() => {
    const config = loadBoardConfig(boardId);
    return config ? `${config.board_abbrev} (${config.char_limits.per_section_min}-${config.char_limits.per_section_max} chars)` : boardId;
  }, [boardId]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Configure board, reporting period, and theme.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-1">
            <div className="text-xs font-medium text-foreground">Current Role</div>
            <select
              className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
              value={currentRole}
              onChange={(e) => void setCurrentRole(e.target.value as UserRole)}
            >
              <option value="teacher">{roleLabels.teacher}</option>
              <option value="ece">{roleLabels.ece}</option>
            </select>
            <div className="text-[11px] text-muted-foreground">
              Role affects draft authoring and approval status.
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium text-foreground">Role Labels</div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[11px] text-muted-foreground">Teacher label</label>
                <input
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  value={roleLabels.teacher}
                  onChange={(e) => void setRoleLabels({ teacher: e.target.value })}
                />
              </div>
              <div className="space-y-1">
                <label className="text-[11px] text-muted-foreground">ECE label</label>
                <input
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  value={roleLabels.ece}
                  onChange={(e) => void setRoleLabels({ ece: e.target.value })}
                />
              </div>
            </div>
            <div className="text-[11px] text-muted-foreground">
              Changes wording only; permissions stay the same.
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-medium text-foreground">School Board</div>
            <select
              className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
              value={boardId}
              onChange={(e) => void setBoardId(e.target.value)}
            >
              {BOARDS.map(b => (
                <option key={b.id} value={b.id}>
                  {b.label}
                </option>
              ))}
            </select>
            <div className="text-[11px] text-muted-foreground">Current: {boardLabel}</div>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-medium text-foreground">Reporting Period</div>
            <select
              className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
              value={currentPeriod}
              onChange={(e) => void setCurrentPeriod(e.target.value as ReportPeriod)}
            >
              {PERIODS.map(p => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-medium text-foreground">Theme</div>
            <select
              className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
              value={theme}
              onChange={(e) => void setTheme(e.target.value as any)}
            >
              <option value="system">System</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium text-foreground">Validation (Tier 1 Heuristics)</div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[11px] text-muted-foreground">Min characters per box</label>
                <input
                  type="number"
                  inputMode="numeric"
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  value={tier1Validation.minChars}
                  min={0}
                  onChange={(e) => void setTier1Validation({ minChars: Number(e.target.value) })}
                />
              </div>
              <div className="space-y-1">
                <label className="text-[11px] text-muted-foreground">Max characters per box</label>
                <input
                  type="number"
                  inputMode="numeric"
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  value={tier1Validation.maxChars}
                  min={0}
                  onChange={(e) => void setTier1Validation({ maxChars: Number(e.target.value) })}
                />
              </div>
              <div className="space-y-1">
                <label className="text-[11px] text-muted-foreground">Min sentences (soft target)</label>
                <input
                  type="number"
                  inputMode="numeric"
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  value={tier1Validation.minSentences}
                  min={1}
                  onChange={(e) => void setTier1Validation({ minSentences: Number(e.target.value) })}
                />
              </div>
              <div className="space-y-1">
                <label className="text-[11px] text-muted-foreground">Max line breaks</label>
                <input
                  type="number"
                  inputMode="numeric"
                  className="w-full border border-border rounded-md px-3 py-2 text-sm bg-background"
                  value={tier1Validation.maxLineBreaks}
                  min={0}
                  onChange={(e) => void setTier1Validation({ maxLineBreaks: Number(e.target.value) })}
                />
              </div>
            </div>
            <div className="text-[11px] text-muted-foreground">
              These checks never block export; they’re intended to approximate “box fit” until we have real layout measurement.
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-xs font-medium text-foreground">Diagnostics</div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={showDebugLogs}
                onChange={(e) => void setShowDebugLogs(e.target.checked)}
              />
              Show debug logs
            </label>
            <div className="text-[11px] text-muted-foreground">
              Off by default. When enabled, debug logs are shown in this Settings dialog.
            </div>

            {showDebugLogs ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="text-[11px] text-muted-foreground">Debug logs (scrollable)</div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const text = (debugLogs ?? []).join("\n");
                      void navigator.clipboard?.writeText(text);
                    }}
                  >
                    Copy
                  </Button>
                </div>
                <div className="border border-border rounded-md bg-black/90 text-white font-mono text-xs p-2 max-h-64 overflow-auto">
                    {(debugLogs ?? []).length === 0 ? (
                    <div className="text-gray-300">(no logs yet)</div>
                  ) : (
                      (debugLogs ?? []).map((L, i) => (
                      <div key={i} className="whitespace-pre-wrap mb-1 border-b border-gray-800 pb-1">
                        {L}
                      </div>
                    ))
                  )}
                </div>
              </div>
            ) : null}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
