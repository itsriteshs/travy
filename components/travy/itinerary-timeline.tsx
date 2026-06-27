import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { NeoProgress } from "@/components/ui/neo-progress";
import type { ItineraryStop } from "@/lib/travy/types";

export function ItineraryTimeline({ stops }: { stops: ItineraryStop[] }) {
  return (
    <div className="space-y-4">
      {stops.map((stop, index) => (
        <NeoCard key={stop.place} tone="paper" strong={index === 0}>
          <div className="flex flex-col gap-4 md:flex-row md:items-start">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-neo border-2 border-black bg-travyYellow font-mono text-2xl font-black shadow-neoSm">
              {index + 1}
            </div>
            <div className="min-w-0 flex-1">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <NeoBadge tone="blue">{stop.time}</NeoBadge>
                <NeoBadge tone="mint">{stop.estimatedCost}</NeoBadge>
                <NeoBadge tone="yellow">Fit {stop.fitScore}/100</NeoBadge>
              </div>
              <NeoCardTitle>{stop.place}</NeoCardTitle>
              <p className="mt-2 text-sm font-bold leading-6 text-zinc-700">{stop.whySelected}</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <NeoProgress value={stop.breakdown.budgetFit} tone="mint" label={`Budget fit ${stop.breakdown.budgetFit}`} />
                <NeoProgress value={stop.breakdown.moodFit} tone="pink" label={`Mood fit ${stop.breakdown.moodFit}`} />
                <NeoProgress value={stop.breakdown.groupFit} tone="lavender" label={`Group fit ${stop.breakdown.groupFit}`} />
                <NeoProgress value={stop.breakdown.distanceFit} tone="blue" label={`Distance fit ${stop.breakdown.distanceFit}`} />
              </div>
              <NeoBadge className="mt-4" tone={stop.breakdown.fatigueScore === "Low" ? "mint" : "orange"}>
                Fatigue: {stop.breakdown.fatigueScore}
              </NeoBadge>
            </div>
          </div>
        </NeoCard>
      ))}
    </div>
  );
}
