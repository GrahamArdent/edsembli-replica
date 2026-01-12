import { useMemo, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { useAppStore } from "../store/useAppStore";
import type { ReportPeriod } from "../types";

const BOARDS = [
  { id: "tcdsb", label: "TCDSB" },
  { id: "ncdsb", label: "NCDSB" },
];

const PERIODS: { id: ReportPeriod; label: string }[] = [
  { id: "initial", label: "Initial Observations" },
  { id: "february", label: "February" },
  { id: "june", label: "June" },
];

type Step = 0 | 1 | 2 | 3;

export function OnboardingWizard() {
  const isHydrated = useAppStore(s => s.isHydrated);
  const hasOnboarded = useAppStore(s => s.hasOnboarded);
  const completeOnboarding = useAppStore(s => s.completeOnboarding);
  const boardId = useAppStore(s => s.boardId);
  const setBoardId = useAppStore(s => s.setBoardId);
  const currentPeriod = useAppStore(s => s.currentPeriod);
  const setCurrentPeriod = useAppStore(s => s.setCurrentPeriod);

  const [step, setStep] = useState<Step>(0);

  const title = useMemo(() => {
    switch (step) {
      case 0:
        return "Welcome";
      case 1:
        return "Board Selection";
      case 2:
        return "Roster";
      case 3:
        return "Reporting Period";
      default:
        return "Welcome";
    }
  }, [step]);

  const canNext = useMemo(() => {
    if (step === 1) return !!boardId;
    if (step === 3) return !!currentPeriod;
    return true;
  }, [step, boardId, currentPeriod]);

  const next = async () => {
    if (!canNext) return;
    if (step < 3) {
      setStep((step + 1) as Step);
      return;
    }
    await completeOnboarding();
  };

  const back = () => {
    if (step > 0) setStep((step - 1) as Step);
  };

  if (!isHydrated || hasOnboarded) return null;

  return (
    <Dialog open={!hasOnboarded} onOpenChange={() => {}}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Onboarding — {title}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {step === 0 && (
            <div className="space-y-2">
              <div className="text-sm text-foreground">
                Let’s set up your classroom so you can start writing Communication of Learning comments.
              </div>
              <div className="text-xs text-muted-foreground">
                This wizard configures board + reporting period. You can change them anytime in Settings.
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-2">
              <div className="text-sm text-foreground">Which school board are you part of?</div>
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
            </div>
          )}

          {step === 2 && (
            <div className="space-y-2">
              <div className="text-sm text-foreground">Roster import</div>
              <div className="text-sm text-muted-foreground">
                CSV import is coming next. For now, use <span className="font-medium">Add Student</span> in the sidebar.
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-2">
              <div className="text-sm text-foreground">Which report are you working on?</div>
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

              <div className="text-xs text-muted-foreground">You’re ready to start writing!</div>
            </div>
          )}
        </div>

        <DialogFooter className="flex items-center justify-between">
          <Button variant="outline" onClick={back} disabled={step === 0}>
            Back
          </Button>
          <Button onClick={() => void next()} disabled={!canNext}>
            {step === 3 ? "Done" : "Next"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
