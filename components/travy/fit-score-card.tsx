import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { NeoProgress } from "@/components/ui/neo-progress";

export function FitScoreCard({ score = 87 }: { score?: number }) {
  return (
    <NeoCard tone="yellow" strong>
      <div className="flex items-start justify-between gap-4">
        <div>
          <NeoCardTitle>Plan Fit Score</NeoCardTitle>
          <p className="mt-1 text-sm font-bold">
            Budget Fit + Mood Match + Distance Fit + Group Match + Time Fit - Fatigue Penalty
          </p>
        </div>
        <NeoBadge tone="ink">Formula</NeoBadge>
      </div>
      <div className="mt-5 font-mono text-6xl font-black">{score}/100</div>
      <NeoProgress className="mt-4" value={score} tone="mint" label="Overall plan fit" />
      <p className="mt-4 text-sm font-bold">
        Travy scores the plan using distance, budget, time, group preference match,
        weather, safety, food nearby, and travel fatigue.
      </p>
    </NeoCard>
  );
}
