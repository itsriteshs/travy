"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  BadgeCheck,
  CircleDollarSign,
  Gauge,
  HelpCircle,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  WalletCards
} from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoButton } from "@/components/ui/neo-button";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { DemoActionCard } from "@/components/travy/demo-action-card";
import { budgetFromAnalysis, parsedFromBackend, runDemoScenario } from "@/lib/travy/backend-api";
import {
  clearLatestBackendRun,
  resetDemoState,
  setBackendError,
  setBudgetState,
  setDemoRequest,
  setLatestAnalysis,
  setLatestGeneration
} from "@/lib/travy/storage";

const scenarios = [
  {
    key: "valid_delhi",
    title: "Valid Delhi Plan",
    description: "Analyze and generate the core 5-hour Delhi ₹800 itinerary.",
    tone: "yellow" as const,
    icon: <Sparkles className="h-6 w-6" aria-hidden />,
    actionLabel: "Run + Results",
    destination: "/results"
  },
  {
    key: "bangalore_low",
    title: "Low Budget Mode",
    description: "Shows compressed context and cheap model routing for Bangalore.",
    tone: "orange" as const,
    icon: <CircleDollarSign className="h-6 w-6" aria-hidden />,
    actionLabel: "Run + Router",
    destination: "/ai-router"
  },
  {
    key: "critical_budget",
    title: "Critical Budget",
    description: "Forces API-only fallback and skips Otari generation.",
    tone: "danger" as const,
    icon: <WalletCards className="h-6 w-6" aria-hidden />,
    actionLabel: "Run + Router",
    destination: "/ai-router"
  },
  {
    key: "prompt_injection",
    title: "Prompt Injection",
    description: "Blocks malicious input before any model call.",
    tone: "lavender" as const,
    icon: <ShieldAlert className="h-6 w-6" aria-hidden />,
    actionLabel: "Run + Security",
    destination: "/security"
  },
  {
    key: "vague_prompt",
    title: "Clarify Vague Prompt",
    description: "Shows missing fields and CLARIFY_REQUIRED route.",
    tone: "blue" as const,
    icon: <HelpCircle className="h-6 w-6" aria-hidden />,
    actionLabel: "Run + Planner",
    destination: "/planner"
  },
  {
    key: "booking_out_of_scope",
    title: "Booking Out Of Scope",
    description: "Shows booking/payment requests are not part of MVP.",
    tone: "pink" as const,
    icon: <BadgeCheck className="h-6 w-6" aria-hidden />,
    actionLabel: "Run + Router",
    destination: "/ai-router"
  },
  {
    key: "unsupported_live_data",
    title: "Unsupported Live Crime Data",
    description: "Shows Guardian Route uses proxy safety signals, not live crime data.",
    tone: "mint" as const,
    icon: <Gauge className="h-6 w-6" aria-hidden />,
    actionLabel: "Run + Router",
    destination: "/ai-router"
  }
];

export default function DemoPage() {
  const router = useRouter();
  const [message, setMessage] = useState("Backend demo state ready.");
  const [running, setRunning] = useState("");

  async function runScenario(key: string, destination: string) {
    setRunning(key);
    try {
      const result = await runDemoScenario(key);
      setLatestAnalysis(result.analysis);
      setBudgetState(budgetFromAnalysis(result.analysis));
      const parsed = parsedFromBackend(result.analysis);
      setDemoRequest({
        city: parsed.city,
        groupSize: parsed.groupSize,
        budgetPerPerson: parsed.budgetPerPerson,
        timeWindow: parsed.timeWindow,
        mood: parsed.moods,
        energy: parsed.energy,
        budgetRemainingUsd: result.analysis.budget.remaining_usd || 0,
        selectedRoute: result.analysis.route_decision.model_id || result.analysis.route_decision.model_tier
      });
      if (result.generation) setLatestGeneration(result.generation);
      setMessage(`${key}: next_action=${result.next_action}, route=${result.analysis.route_decision.route}, generation=${result.generation?.status || "not run"}`);
      router.push(destination);
    } catch (err) {
      const nextMessage = err instanceof Error ? err.message : "Backend scenario failed.";
      setMessage(`Backend unavailable: ${nextMessage}`);
      setBackendError(nextMessage);
    } finally {
      setRunning("");
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-8 max-w-4xl">
        <NeoBadge tone="yellow">Judge control room</NeoBadge>
        <h1 className="mt-3 text-5xl font-black leading-none md:text-6xl">
          Travy Round 2 Backend Demo Control
        </h1>
        <p className="mt-4 text-lg font-semibold leading-8 text-zinc-800">
          Trigger real FastAPI scenarios for planning, routing, budget fallback,
          clarification, out-of-scope handling, and security.
        </p>
      </div>

      <NeoCard tone="mint" strong className="mb-6">
        <NeoCardTitle>Current presenter note</NeoCardTitle>
        <p className="mt-2 font-bold">{message}</p>
      </NeoCard>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {scenarios.map((scenario) => (
          <DemoActionCard
            key={scenario.key}
            title={scenario.title}
            description={scenario.description}
            tone={scenario.tone}
            icon={scenario.icon}
            actionLabel={running === scenario.key ? "Running..." : scenario.actionLabel}
            onAction={() => runScenario(scenario.key, scenario.destination)}
          />
        ))}
        <DemoActionCard
          title="Reset Backend Demo State"
          description="Clears local frontend state. Use backend /api/demo/reset separately if you need DB logs reset."
          tone="lavender"
          icon={<RotateCcw className="h-6 w-6" aria-hidden />}
          actionLabel="Reset Local"
          onAction={() => {
            resetDemoState();
            clearLatestBackendRun();
            setMessage("Local demo state reset. Backend DB logs are untouched.");
          }}
        />
        <NeoCard tone="paper" strong>
          <BadgeCheck className="mb-4 h-8 w-8" aria-hidden />
          <NeoCardTitle>Recommended flow</NeoCardTitle>
          <p className="mt-2 text-sm font-bold leading-6">
            Run Valid Delhi Plan, then visit Results and AI Router. Use Low/Critical
            budget, Prompt Injection, and Vague Prompt when judges ask for core requirement proof.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <NeoButton href="/planner" variant="accent">Planner</NeoButton>
            <NeoButton href="/ai-router" variant="mint">Router</NeoButton>
            <NeoButton href="/security" variant="danger">Security</NeoButton>
          </div>
        </NeoCard>
      </div>
    </div>
  );
}
