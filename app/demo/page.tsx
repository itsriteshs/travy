"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  BadgeCheck,
  CircleDollarSign,
  Gauge,
  RotateCcw,
  Route,
  ShieldAlert,
  Sparkles
} from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { DemoActionCard } from "@/components/travy/demo-action-card";
import {
  criticalBudgetState,
  defaultBudgetState,
  defaultRequestState,
  lowBudgetState
} from "@/lib/travy/demo-data";
import {
  resetDemoState,
  setBudgetState,
  setDemoRequest,
  setRouteHighlight,
  setSecurityDemo
} from "@/lib/travy/storage";

export default function DemoPage() {
  const router = useRouter();
  const [message, setMessage] = useState("Demo state ready.");

  function go(path: string) {
    router.push(path);
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-8 max-w-4xl">
        <NeoBadge tone="yellow">Judge control room</NeoBadge>
        <h1 className="mt-3 text-5xl font-black leading-none md:text-6xl">
          Travy Round 2 Demo Control
        </h1>
        <p className="mt-4 text-lg font-semibold leading-8 text-zinc-800">
          Trigger core scenarios for planning, routing, budget fallback, and security.
        </p>
      </div>

      <NeoCard tone="mint" strong className="mb-6">
        <NeoCardTitle>Current presenter note</NeoCardTitle>
        <p className="mt-2 font-bold">{message}</p>
      </NeoCard>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <DemoActionCard
          title="Generate Delhi ₹800 Plan"
          description="Loads the main planner request, sets normal budget mode, and opens results."
          tone="yellow"
          icon={<Sparkles className="h-6 w-6" aria-hidden />}
          actionLabel="Open Results"
          onAction={() => {
            setDemoRequest(defaultRequestState);
            setBudgetState(defaultBudgetState);
            setRouteHighlight(false);
            setMessage("Loaded normal Delhi plan with healthy budget.");
            go("/results");
          }}
        />
        <DemoActionCard
          title="Show Routing Trace"
          description="Navigates to the AI Router with healthy budget mode."
          tone="blue"
          icon={<Gauge className="h-6 w-6" aria-hidden />}
          actionLabel="Open Router"
          onAction={() => {
            setBudgetState(defaultBudgetState);
            setMessage("Routing trace opened with healthy budget.");
            go("/ai-router");
          }}
        />
        <DemoActionCard
          title="Trigger Low Budget Mode"
          description="Sets remaining AI budget to $0.12 and shows compressed context with cheaper route."
          tone="orange"
          icon={<CircleDollarSign className="h-6 w-6" aria-hidden />}
          actionLabel="Show Low Budget"
          onAction={() => {
            setBudgetState(lowBudgetState);
            setMessage("Low budget mode enabled: compressed context and cheap model route.");
            go("/ai-router");
          }}
        />
        <DemoActionCard
          title="Trigger Critical Budget Mode"
          description="Sets remaining AI budget to $0.02 and switches to API-only fallback."
          tone="danger"
          icon={<CircleDollarSign className="h-6 w-6" aria-hidden />}
          actionLabel="Show Fallback"
          onAction={() => {
            setBudgetState(criticalBudgetState);
            setMessage("Critical budget mode enabled: no strong planner model call.");
            go("/ai-router");
          }}
        />
        <DemoActionCard
          title="Trigger Prompt Injection Attack"
          description="Opens the security page with malicious event text blocked before AI."
          tone="lavender"
          icon={<ShieldAlert className="h-6 w-6" aria-hidden />}
          actionLabel="Open Security"
          onAction={() => {
            setSecurityDemo(true);
            setMessage("Security scenario opened.");
            go("/security");
          }}
        />
        <DemoActionCard
          title="Show Guardian Route"
          description="Highlights the Guardian Route panel on the generated itinerary."
          tone="mint"
          icon={<Route className="h-6 w-6" aria-hidden />}
          actionLabel="Highlight Route"
          onAction={() => {
            setDemoRequest(defaultRequestState);
            setBudgetState(defaultBudgetState);
            setRouteHighlight(true);
            setMessage("Guardian Route highlight enabled.");
            go("/results");
          }}
        />
        <DemoActionCard
          title="Reset Demo"
          description="Resets local state to the default $2.00 budget and clears special flags."
          tone="pink"
          icon={<RotateCcw className="h-6 w-6" aria-hidden />}
          actionLabel="Reset State"
          onAction={() => {
            resetDemoState();
            setMessage("Reset complete: budget is back to $2.00 and demo flags are cleared.");
          }}
        />
        <NeoCard tone="paper" strong>
          <BadgeCheck className="mb-4 h-8 w-8" aria-hidden />
          <NeoCardTitle>Recommended flow</NeoCardTitle>
          <p className="mt-2 text-sm font-bold leading-6">
            Home {"->"} Planner {"->"} Results {"->"} AI Router {"->"} Security {"->"} Demo. Use the
            action cards when a judge asks to see budget fallback or security quickly.
          </p>
        </NeoCard>
      </div>
    </div>
  );
}
