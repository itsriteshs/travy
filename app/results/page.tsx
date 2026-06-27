"use client";

import { useEffect, useState } from "react";
import { BrainCircuit, Coins, Route } from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoButton } from "@/components/ui/neo-button";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { NeoProgress } from "@/components/ui/neo-progress";
import { FitScoreCard } from "@/components/travy/fit-score-card";
import { GuardianRouteCard } from "@/components/travy/guardian-route-card";
import { ItineraryTimeline } from "@/components/travy/itinerary-timeline";
import { budgetBreakdown, defaultRequestState, itineraryStops } from "@/lib/travy/demo-data";
import { getDemoRequest, getRouteHighlight } from "@/lib/travy/storage";
import type { DemoRequestState } from "@/lib/travy/types";

export default function ResultsPage() {
  const [request, setRequest] = useState<DemoRequestState>(defaultRequestState);
  const [highlight, setHighlight] = useState(false);

  useEffect(() => {
    setRequest(getDemoRequest());
    setHighlight(getRouteHighlight());
  }, []);

  const budgetPercent = (budgetBreakdown.estimatedTotal / budgetBreakdown.budgetPerPerson) * 100;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <NeoCard tone="yellow" strong className="mb-8">
        <div className="grid gap-5 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <NeoBadge tone="mint">Generated plan</NeoBadge>
            <h1 className="mt-3 text-4xl font-black leading-none md:text-6xl">
              Your 5-hour Delhi Hangout Plan
            </h1>
            <div className="mt-4 flex flex-wrap gap-2">
              <NeoBadge tone="default">{request.groupSize} friends</NeoBadge>
              <NeoBadge tone="mint">₹{request.budgetPerPerson}/person</NeoBadge>
              <NeoBadge tone="blue">{request.timeWindow}</NeoBadge>
              <NeoBadge tone="pink">{request.mood.join(" + ")}</NeoBadge>
              <NeoBadge tone="orange">{request.energy} energy</NeoBadge>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <NeoBadge tone="mint">Budget-safe</NeoBadge>
            <NeoBadge tone="pink">Group-balanced</NeoBadge>
            <NeoBadge tone="orange">Low fatigue</NeoBadge>
            <NeoBadge tone="blue">Guardian route available</NeoBadge>
          </div>
        </div>
      </NeoCard>

      <div className="grid gap-6 lg:grid-cols-[1fr_370px]">
        <section>
          <div className="mb-4 flex items-center gap-2">
            <Route className="h-7 w-7" aria-hidden />
            <h2 className="text-3xl font-black">Main Itinerary Timeline</h2>
          </div>
          <ItineraryTimeline stops={itineraryStops} />
        </section>

        <aside className="space-y-6">
          <NeoCard tone="paper" strong>
            <div className="mb-4 flex items-center gap-2">
              <Coins className="h-6 w-6" aria-hidden />
              <NeoCardTitle>Budget Breakdown</NeoCardTitle>
            </div>
            <NeoProgress value={budgetPercent} tone="mint" label={`₹${budgetBreakdown.estimatedTotal} of ₹${budgetBreakdown.budgetPerPerson}`} />
            <div className="mt-4 space-y-2">
              {[
                ["Budget per person", `₹${budgetBreakdown.budgetPerPerson}`],
                ["Food", `₹${budgetBreakdown.food}`],
                ["Travel", `₹${budgetBreakdown.travel}`],
                ["Shopping buffer", `₹${budgetBreakdown.shoppingBuffer}`],
                ["Misc", `₹${budgetBreakdown.misc}`],
                ["Estimated total", `₹${budgetBreakdown.estimatedTotal}/person`],
                ["Budget left", `₹${budgetBreakdown.budgetLeft}/person`]
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between border-b-2 border-black py-2 font-bold">
                  <span>{label}</span>
                  <span className="font-mono font-black">{value}</span>
                </div>
              ))}
            </div>
          </NeoCard>
          <FitScoreCard />
          <GuardianRouteCard highlight={highlight} />
        </aside>
      </div>

      <NeoCard tone="lavender" strong className="mt-8">
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <NeoCardTitle className="flex items-center gap-2">
              <BrainCircuit className="h-6 w-6" aria-hidden />
              AI Usage Summary
            </NeoCardTitle>
            <div className="mt-4 rounded-neo border-2 border-black bg-white p-4">
              <div className="text-xs font-black uppercase">AI used only for</div>
              <ul className="mt-2 list-inside list-disc font-bold leading-7">
                <li>Understanding the user request</li>
                <li>Explaining the final plan</li>
              </ul>
            </div>
          </div>
          <div className="rounded-neo border-2 border-black bg-travySunwash p-4">
            <div className="text-xs font-black uppercase">Local/API logic used for</div>
            <ul className="mt-2 list-inside list-disc font-bold leading-7">
              <li>Budget calculation</li>
              <li>Place scoring</li>
              <li>Route comfort scoring</li>
              <li>Prompt injection filtering</li>
            </ul>
          </div>
        </div>
        <NeoButton href="/ai-router" className="mt-5" variant="accent">
          View AI Routing Trace
        </NeoButton>
      </NeoCard>
    </div>
  );
}
