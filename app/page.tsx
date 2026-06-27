import { ArrowRight, BrainCircuit, Coins, Map, ShieldCheck, Sparkles, Users } from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoButton } from "@/components/ui/neo-button";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { BudgetMeter } from "@/components/travy/budget-meter";
import { FitScoreCard } from "@/components/travy/fit-score-card";
import { GuardianRouteCard } from "@/components/travy/guardian-route-card";
import { featureCards, defaultBudgetState } from "@/lib/travy/demo-data";

const icons = [Sparkles, Users, BrainCircuit, ShieldCheck, Coins, ShieldCheck];
const tones = ["yellow", "pink", "mint", "blue", "lavender", "danger"] as const;

export default function HomePage() {
  return (
    <div>
      <section className="border-b-4 border-black bg-travyCream">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-14 md:grid-cols-[1fr_0.9fr] md:py-20">
          <div className="flex flex-col justify-center">
            <NeoBadge tone="yellow" className="mb-4 w-fit">
              What should we actually do today?
            </NeoBadge>
            <h1 className="max-w-3xl text-6xl font-black leading-[0.92] md:text-8xl">
              Travy
            </h1>
            <p className="mt-5 max-w-2xl text-2xl font-black">
              Cost-aware social travel assistant for real-world group plans.
            </p>
            <p className="mt-4 max-w-2xl text-lg font-semibold leading-8 text-zinc-800">
              Tell Travy your city, budget, group, time, and mood. It builds a
              practical plan while showing which model was used, why it was
              selected, and how much it cost.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <NeoButton href="/planner" size="lg" rightIcon={<ArrowRight className="h-5 w-5" aria-hidden />}>
                Start Planning
              </NeoButton>
              <NeoButton href="/ai-router" variant="accent" size="lg">
                View Routing Demo
              </NeoButton>
              <NeoButton href="/security" variant="secondary" size="lg">
                Prompt Injection Demo
              </NeoButton>
            </div>
          </div>
          <NeoCard tone="paper" strong className="relative overflow-hidden p-0">
            <div className="border-b-4 border-black bg-travyBlue p-4">
              <div className="flex items-center justify-between gap-3">
                <NeoCardTitle>Live Demo Preview</NeoCardTitle>
                <NeoBadge tone="mint">Budget safe</NeoBadge>
              </div>
            </div>
            <div className="grid gap-4 p-4">
              <div className="rounded-neo border-2 border-black bg-travyYellow p-4">
                <div className="text-xs font-black uppercase">Selected Plan</div>
                <div className="mt-1 text-2xl font-black">Delhi hangout: shopping + food + photos</div>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                {[
                  ["Route", "Strong planner", "lavender"],
                  ["Cost", "$0.045", "mint"],
                  ["Fit", "87/100", "yellow"]
                ].map(([label, value, tone]) => (
                  <div key={label} className="rounded-neo border-2 border-black bg-white p-3 shadow-neoSm">
                    <div className="text-xs font-black uppercase">{label}</div>
                    <NeoBadge tone={tone as "lavender" | "mint" | "yellow"}>{value}</NeoBadge>
                  </div>
                ))}
              </div>
              <div className="min-h-[220px] rounded-neo border-4 border-black bg-travySunwash p-4">
                <div className="flex h-full flex-col justify-between gap-4">
                  <div className="flex items-center gap-2 font-black">
                    <Map className="h-5 w-5" aria-hidden />
                    Map preview without real map calls
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {["Janpath", "CP Food", "India Gate", "Dessert"].map((place, i) => (
                      <div key={place} className="rounded-neo border-2 border-black bg-white p-3 font-black shadow-neoSm">
                        {i + 1}. {place}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </NeoCard>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16">
        <div className="grid gap-4 md:grid-cols-3">
          {[
            ["Too many tabs", "Groups bounce between maps, reviews, reels, budgets, and chats."],
            ["Different priorities", "One friend wants food, one wants photos, one wants low walking."],
            ["AI cost matters", "Complex planning needs reasoning, but every model call eats budget."]
          ].map(([title, copy], index) => (
            <NeoCard key={title} tone={index === 0 ? "orange" : index === 1 ? "pink" : "lavender"} strong>
              <NeoCardTitle>{title}</NeoCardTitle>
              <p className="mt-2 font-bold leading-7">{copy}</p>
            </NeoCard>
          ))}
        </div>
      </section>

      <section className="border-y-4 border-black bg-white">
        <div className="mx-auto max-w-7xl px-4 py-16">
          <div className="mb-8 max-w-3xl">
            <NeoBadge tone="blue">Features</NeoBadge>
            <h2 className="mt-3 text-4xl font-black md:text-5xl">Built for judge-visible reasoning</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {featureCards.map((feature, index) => {
              const Icon = icons[index];
              return (
                <NeoCard key={feature.title} tone={tones[index]} strong>
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-neo border-2 border-black bg-white shadow-neoSm">
                    <Icon className="h-6 w-6" aria-hidden />
                  </div>
                  <NeoCardTitle>{feature.title}</NeoCardTitle>
                  <p className="mt-2 text-sm font-bold leading-6">{feature.description}</p>
                </NeoCard>
              );
            })}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16">
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <NeoBadge tone="yellow">How it works</NeoBadge>
            <h2 className="mt-3 text-4xl font-black md:text-5xl">Natural language in. Practical plan out.</h2>
            <div className="mt-6 space-y-3">
              {[
                "Parse city, time, budget, group, and mood.",
                "Scan untrusted text before model calls.",
                "Compress context when budget drops.",
                "Route each subtask to local logic, API, cheap model, or strong planner.",
                "Show itinerary, fit score, route comfort, and cost reasoning."
              ].map((step, index) => (
                <div key={step} className="flex gap-3 rounded-neo border-2 border-black bg-white p-3 shadow-neoSm">
                  <span className="font-mono text-xl font-black">{index + 1}</span>
                  <p className="font-bold">{step}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="grid gap-4">
            <BudgetMeter budget={defaultBudgetState} />
            <FitScoreCard />
          </div>
        </div>
      </section>

      <section className="border-y-4 border-black bg-travySunwash">
        <div className="mx-auto grid max-w-7xl gap-4 px-4 py-16 lg:grid-cols-2">
          <GuardianRouteCard />
          <NeoCard tone="ink" strong>
            <NeoBadge tone="yellow">Final CTA</NeoBadge>
            <h2 className="mt-4 text-4xl font-black md:text-5xl">Run the complete Round 2 flow.</h2>
            <p className="mt-4 text-lg font-semibold leading-8 text-white/85">
              Start with the planner, generate the Delhi itinerary, then inspect
              routing, budget fallback, and prompt injection protection.
            </p>
            <NeoButton href="/planner" size="lg" className="mt-8" rightIcon={<ArrowRight className="h-5 w-5" aria-hidden />}>
              Start Planning
            </NeoButton>
          </NeoCard>
        </div>
      </section>

      <footer className="border-t-4 border-black bg-travyInk px-4 py-8 text-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <strong className="text-2xl">Travy</strong>
          <span className="font-semibold text-white/80">Frontend-only Round 2 demo. No real AI, backend, maps, auth, or payments.</span>
        </div>
      </footer>
    </div>
  );
}
