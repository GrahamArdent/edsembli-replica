import { useMemo } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { useAppStore } from "../store/useAppStore";
import type { ReportPeriod, UserRole } from "../types";

const BOARDS = [
  { id: "tcdsb", label: "TCDSB" },
  { id: "ncdsb", label: "NCDSB" },
];

const PERIODS: { id: ReportPeriod; label: string }[] = [
  { id: "initial", label: "Initial Observations" },
  { id: "february", label: "February" },
  { id: "june", label: "June" },
];

export function SettingsModal({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const boardId = useAppStore(s => s.boardId);
  const setBoardId = useAppStore(s => s.setBoardId);
  const theme = useAppStore(s => s.theme);
  const setTheme = useAppStore(s => s.setTheme);
  const currentPeriod = useAppStore(s => s.currentPeriod);
  const setCurrentPeriod = useAppStore(s => s.setCurrentPeriod);

  const currentRole = useAppStore(s => s.currentRole);
  const setCurrentRole = useAppStore(s => s.setCurrentRole);

  const tier1Validation = useAppStore(s => s.tier1Validation);
  const setTier1Validation = useAppStore(s => s.setTier1Validation);

  const boardLabel = useMemo(() => BOARDS.find(b => b.id === boardId)?.label ?? boardId, [boardId]);

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
              <option value="teacher">Teacher</option>
              <option value="ece">ECE</option>
            </select>
            <div className="text-[11px] text-muted-foreground">
              Role affects draft authoring and approval status.
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
