"use client";

import { useEffect, useMemo, useState } from "react";
import { BrainCircuit, Coins, DatabaseZap, Route } from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoButton } from "@/components/ui/neo-button";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { NeoProgress } from "@/components/ui/neo-progress";
import { FitScoreCard } from "@/components/travy/fit-score-card";
import { GuardianRouteCard } from "@/components/travy/guardian-route-card";
import { ItineraryTimeline } from "@/components/travy/itinerary-timeline";
import { budgetBreakdown as defaultBudgetBreakdown, defaultRequestState, itineraryStops } from "@/lib/travy/demo-data";
import { guardianFromGeneration, planFitScore, stopsFromGeneration } from "@/lib/travy/backend-api";
import { getBackendError, getDemoRequest, getLatestAnalysis, getLatestGeneration, getRouteHighlight } from "@/lib/travy/storage";
import type { BackendAnalysis, BackendGeneration, DemoRequestState } from "@/lib/travy/types";

function inr(value: number | undefined) {
  return `₹${Math.round(value || 0)}`;
}

export default function ResultsPage() {
  const [request, setRequest] = useState<DemoRequestState>(defaultRequestState);
  const [highlight, setHighlight] = useState(false);
  const [analysis, setAnalysis] = useState<BackendAnalysis | null>(null);
  const [generation, setGeneration] = useState<BackendGeneration | null>(null);
  const [backendError, setBackendError] = useState("");

  useEffect(() => {
    setRequest(getDemoRequest());
    setHighlight(getRouteHighlight());
    setAnalysis(getLatestAnalysis());
    setGeneration(getLatestGeneration());
    setBackendError(getBackendError());
  }, []);

  const stops = useMemo(() => (generation?.status === "success" ? stopsFromGeneration(generation) : itineraryStops), [generation]);
  const guardian = useMemo(() => (generation?.status === "success" ? guardianFromGeneration(generation) : undefined), [generation]);
  const fitScore = useMemo(() => (generation?.status === "success" ? planFitScore(generation) : 87), [generation]);
  const backendBudget = generation?.budget_breakdown;
  const budgetPerPerson = backendBudget?.budget_per_person_inr || generation?.itinerary?.total_estimated_cost_per_person_inr || defaultBudgetBreakdown.budgetPerPerson;
  const estimatedTotal = backendBudget?.estimated_total || generation?.itinerary?.total_estimated_cost_per_person_inr || defaultBudgetBreakdown.estimatedTotal;
  const budgetLeft = backendBudget?.budget_left ?? Math.max(budgetPerPerson - estimatedTotal, 0);
  const budgetPercent = budgetPerPerson > 0 ? (estimatedTotal / budgetPerPerson) * 100 : 0;
  const title = generation?.itinerary?.title || "Generate a backend plan first";
  const summary = generation?.itinerary?.summary || "No backend generation is stored yet. Open Planner, analyze a request, then generate the plan.";

  if (!generation && !backendError) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16">
        <NeoCard tone="lavender" strong>
          <NeoBadge tone="orange">No backend result</NeoBadge>
          <h1 className="mt-3 text-5xl font-black leading-none">Generate a plan first.</h1>
          <p className="mt-4 text-lg font-bold leading-8">
            Results now read from the FastAPI generation response. Use the planner to create a request and store the latest itinerary.
          </p>
          <NeoButton href="/planner" className="mt-5" variant="accent">
            Open Planner
          </NeoButton>
        </NeoCard>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <NeoCard tone="yellow" strong className="mb-8">
        <div className="grid gap-5 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <NeoBadge tone={generation?.source?.fallback_used ? "orange" : "mint"}>
              {generation?.source?.generation_method || "Backend status"}
            </NeoBadge>
            <h1 className="mt-3 text-4xl font-black leading-none md:text-6xl">
              {title}
            </h1>
            <p className="mt-3 max-w-3xl font-bold leading-7">{summary}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <NeoBadge tone="default">{request.groupSize} traveler(s)</NeoBadge>
              <NeoBadge tone="mint">₹{request.budgetPerPerson}/person</NeoBadge>
              <NeoBadge tone="blue">{request.timeWindow}</NeoBadge>
              <NeoBadge tone="pink">{request.mood.join(" + ") || "backend moods"}</NeoBadge>
              <NeoBadge tone="orange">{request.energy} energy</NeoBadge>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <NeoBadge tone={generation?.validation?.passed ? "mint" : "orange"}>
              Validation {generation?.validation?.passed ? "passed" : "warnings"}
            </NeoBadge>
            <NeoBadge tone="pink">Group-aware UI</NeoBadge>
            <NeoBadge tone="blue">Guardian route available</NeoBadge>
          </div>
        </div>
      </NeoCard>

      {backendError && (
        <NeoCard tone="danger" strong className="mb-6">
          <NeoCardTitle>Backend Error</NeoCardTitle>
          <p className="mt-2 font-bold">{backendError}</p>
        </NeoCard>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_370px]">
        <section>
          <div className="mb-4 flex items-center gap-2">
            <Route className="h-7 w-7" aria-hidden />
            <h2 className="text-3xl font-black">Backend Itinerary Timeline</h2>
          </div>
          <ItineraryTimeline stops={stops} />
        </section>

        <aside className="space-y-6">
          <NeoCard tone="paper" strong>
            <div className="mb-4 flex items-center gap-2">
              <Coins className="h-6 w-6" aria-hidden />
              <NeoCardTitle>Budget Breakdown</NeoCardTitle>
            </div>
            <NeoProgress value={budgetPercent} tone="mint" label={`${inr(estimatedTotal)} of ${inr(budgetPerPerson)}`} />
            <div className="mt-4 space-y-2">
              {[
                ["Budget per person", inr(budgetPerPerson)],
                ["Estimated total", `${inr(estimatedTotal)}/person`],
                ["Budget left", `${inr(budgetLeft)}/person`],
                ["Budget status", String(generation?.itinerary?.budget_status || backendBudget?.budget_status || "demo")]
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between border-b-2 border-black py-2 font-bold">
                  <span>{label}</span>
                  <span className="font-mono font-black">{value}</span>
                </div>
              ))}
            </div>
          </NeoCard>
          <FitScoreCard score={fitScore} />
          <GuardianRouteCard highlight={highlight} route={guardian} />
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
              <div className="text-xs font-black uppercase">Backend route</div>
              <p className="mt-2 font-bold leading-7">
                {analysis?.route_decision.route || "No analysis stored"} using {analysis?.route_decision.model_tier || "unknown"}.
                Estimated cost: ${analysis?.route_decision.estimated_cost_usd?.toFixed(3) || "0.000"}.
              </p>
              <p className="mt-2 font-bold leading-7">
                Generation method: {generation?.source?.generation_method || "not generated"}.
                Fallback used: {String(generation?.source?.fallback_used ?? false)}.
              </p>
            </div>
          </div>
          <div className="rounded-neo border-2 border-black bg-travySunwash p-4">
            <NeoCardTitle className="flex items-center gap-2">
              <DatabaseZap className="h-6 w-6" aria-hidden />
              API Evidence
            </NeoCardTitle>
            <div className="mt-3 grid gap-2">
              {Object.entries(generation?.api_evidence || {}).map(([name, info]) => (
                <div key={name} className="rounded-neo border-2 border-black bg-white p-3">
                  <div className="text-xs font-black uppercase">{name}</div>
                  <p className="text-sm font-bold">
                    {Object.entries(info).map(([key, value]) => `${key}: ${String(value)}`).join(" | ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
        <NeoButton href="/ai-router" className="mt-5" variant="accent">
          View AI Routing Trace
        </NeoButton>
      </NeoCard>
    </div>
  );
}
