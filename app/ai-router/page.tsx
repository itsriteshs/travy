"use client";

import { useEffect, useMemo, useState } from "react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { BudgetMeter } from "@/components/travy/budget-meter";
import { ContextPriorityTable } from "@/components/travy/context-priority-table";
import { PipelineTrace } from "@/components/travy/pipeline-trace";
import { RoutingTable } from "@/components/travy/routing-table";
import { defaultBudgetState, defaultPrompt, routingTraceRows } from "@/lib/travy/demo-data";
import {
  calculateComplexity,
  parseTravelRequest,
  scanPromptInjection,
  selectContextByBudget,
  selectRoute
} from "@/lib/travy/demo-logic";
import { getBudgetState } from "@/lib/travy/storage";
import type { BudgetState } from "@/lib/travy/types";

export default function AiRouterPage() {
  const [budget, setBudget] = useState<BudgetState>(defaultBudgetState);

  useEffect(() => {
    setBudget(getBudgetState());
  }, []);

  const parsed = useMemo(() => parseTravelRequest(defaultPrompt), []);
  const risk = useMemo(() => scanPromptInjection(defaultPrompt), []);
  const complexity = useMemo(() => calculateComplexity(parsed), [parsed]);
  const route = useMemo(
    () => selectRoute({ risk, complexity, budgetRemaining: budget.remainingBudgetUsd }),
    [risk, complexity, budget.remainingBudgetUsd]
  );
  const context = useMemo(
    () => selectContextByBudget(budget.remainingBudgetUsd),
    [budget.remainingBudgetUsd]
  );

  const adjustedRows = routingTraceRows.map((row) => {
    if (budget.mode === "critical" && row.task === "Final explanation") {
      return {
        ...row,
        route: "API-only fallback",
        cost: "$0.000",
        reason: "Critical budget: use seeded places, local scoring, and template itinerary"
      };
    }
    if (budget.mode === "low" && row.task === "Final explanation") {
      return {
        ...row,
        route: "Cheap model + compressed context",
        cost: "$0.008",
        reason: "Low budget: optional context is dropped before model call"
      };
    }
    return row;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-8 max-w-4xl">
        <NeoBadge tone="lavender">Otari-style transparency</NeoBadge>
        <h1 className="mt-3 text-5xl font-black leading-none md:text-6xl">
          AI Router: model, cost, and context decisions.
        </h1>
        <p className="mt-4 text-lg font-semibold leading-8 text-zinc-800">
          This page proves which route was selected, why it was selected, how
          much it cost, and how behavior changes when budget drops.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="space-y-6">
          <BudgetMeter budget={budget} />
          <NeoCard tone="yellow" strong>
            <NeoCardTitle>Current Request</NeoCardTitle>
            <p className="mt-3 rounded-neo border-2 border-black bg-white p-4 font-bold leading-7">
              {defaultPrompt}
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <div className="rounded-neo border-2 border-black bg-white p-3">
                <div className="text-xs font-black uppercase">Selected Route</div>
                <div className="font-black">{route.label}</div>
              </div>
              <div className="rounded-neo border-2 border-black bg-white p-3">
                <div className="text-xs font-black uppercase">Reason</div>
                <div className="text-sm font-bold">{route.reason}</div>
              </div>
            </div>
          </NeoCard>
          <NeoCard tone="paper" strong>
            <NeoCardTitle>Model Selection Logic</NeoCardTitle>
            <pre className="mt-4 overflow-x-auto rounded-neo border-2 border-black bg-travyInk p-4 font-mono text-sm font-bold leading-7 text-white">
{`If malicious input is detected:
    Block before model call
If task is simple extraction:
    Use cheap model or parser
If task is deterministic:
    Use local logic or API
If task requires multi-step group planning:
    Use stronger planner model
If budget is low:
    Compress context and use cheaper model
If budget is critical:
    Switch to API-only fallback`}
            </pre>
          </NeoCard>
        </div>
        <div className="space-y-6">
          <PipelineTrace
            steps={[
              "User Prompt",
              "Injection Filter",
              "Intent Extractor",
              "Context Prioritizer",
              "Budget Check",
              "Model Router",
              "Local Scoring",
              "Final Itinerary"
            ]}
          />
          <RoutingTable title="Routing Trace Table" rows={adjustedRows} />
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <NeoCard tone="blue" strong>
          <NeoCardTitle>Complexity Score</NeoCardTitle>
          <div className="mt-4 font-mono text-6xl font-black">{complexity}/100</div>
          <div className="mt-4 space-y-2">
            {[
              "Group size > 1: +20",
              "Budget constraint: +15",
              "Time window: +15",
              "Multiple moods: +15",
              "Route ordering: +20",
              "Past preference context: +10"
            ].map((item) => (
              <div key={item} className="rounded-neo border-2 border-black bg-white p-2 font-bold shadow-neoSm">
                {item}
              </div>
            ))}
          </div>
          <NeoBadge className="mt-4" tone="yellow">
            86/100 {"->"} Strong planner model
          </NeoBadge>
          <div className="mt-4 rounded-neo border-2 border-black bg-white p-3 font-bold">
            Thresholds: 0-30 Local/API, 31-60 Cheap model, 61-85 Balanced model,
            86-100 Strong planner model.
          </div>
        </NeoCard>
        <ContextPriorityTable context={context} />
      </div>

      <NeoCard tone="mint" strong className="mt-6">
        <NeoCardTitle>Context Compression Demo</NeoCardTitle>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {[
            ["Budget healthy", "City, time, budget, group size, mood, weather, friend preferences, past liked places, short reviews"],
            ["Budget low", "Include city, time, budget, group size, mood, weather. Drop long reviews, old friend history, low relevance past likes."],
            ["Budget critical", "Use seeded/API places, local scoring, and template itinerary. Do not call strong planner model."]
          ].map(([title, copy], index) => (
            <div key={title} className="rounded-neo border-2 border-black bg-white p-4 shadow-neoSm">
              <NeoBadge tone={index === 0 ? "mint" : index === 1 ? "orange" : "danger"}>
                {title}
              </NeoBadge>
              <p className="mt-3 text-sm font-bold leading-6">{copy}</p>
            </div>
          ))}
        </div>
      </NeoCard>
    </div>
  );
}
