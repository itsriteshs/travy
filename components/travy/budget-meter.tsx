import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { NeoProgress } from "@/components/ui/neo-progress";
import { getBudgetStatus } from "@/lib/travy/demo-logic";
import type { BudgetState } from "@/lib/travy/types";

export function BudgetMeter({ budget }: { budget: BudgetState }) {
  const usedPercent = (budget.usedBudgetUsd / budget.totalBudgetUsd) * 100;
  const remainingPercent = (budget.remainingBudgetUsd / budget.totalBudgetUsd) * 100;
  const status = getBudgetStatus(budget);
  const tone =
    budget.remainingBudgetUsd < 0.05
      ? "danger"
      : budget.remainingBudgetUsd < 0.2
        ? "orange"
        : "mint";

  return (
    <NeoCard tone="paper" strong>
      <div className="flex flex-col gap-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <NeoCardTitle>AI Budget Meter</NeoCardTitle>
            <p className="text-sm font-bold text-zinc-700">
              Runtime budget changes model behavior, not just decoration.
            </p>
          </div>
          <NeoBadge tone={tone}>{status}</NeoBadge>
        </div>
        <NeoProgress value={usedPercent} tone={tone} label={`${remainingPercent.toFixed(0)}% remaining`} />
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {[
            ["Total", `$${budget.totalBudgetUsd.toFixed(2)}`],
            ["Used", `$${budget.usedBudgetUsd.toFixed(2)}`],
            ["Remaining", `$${budget.remainingBudgetUsd.toFixed(2)}`],
            ["Request", `$${budget.currentRequestCostUsd.toFixed(3)}`]
          ].map(([label, value]) => (
            <div key={label} className="rounded-neo border-2 border-black bg-travySunwash p-3">
              <div className="text-xs font-black uppercase">{label}</div>
              <div className="font-mono text-2xl font-black">{value}</div>
            </div>
          ))}
        </div>
      </div>
    </NeoCard>
  );
}
