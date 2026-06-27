import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import type { ContextSelection } from "@/lib/travy/types";

const rows = [
  ["P1", "City/location", "city", "Required to find relevant places"],
  ["P1", "Time window", "timeWindow", "Required for route order and availability"],
  ["P1", "Budget", "budgetPerPerson", "Hard constraint"],
  ["P1", "Group size", "groupSize", "Needed for per-person cost"],
  ["P2", "Mood/preferences", "mood", "Needed for matching activities"],
  ["P2", "Weather", "weather", "Affects outdoor spots"],
  ["P3", "Past liked places", "pastLikedPlaces", "Improves personalization"],
  ["P3", "Friend history", "friendHistory", "Useful but optional"],
  ["P4", "Long reviews/photos", "longReviews", "Expensive context, low priority"]
];

export function ContextPriorityTable({ context }: { context: ContextSelection }) {
  const modeLabel = {
    full_context: "Full context",
    low_budget: "Compressed context",
    critical_budget: "API-only fallback"
  }[context.mode];

  return (
    <NeoCard tone="lavender" strong>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <NeoCardTitle>Context Priority Stack</NeoCardTitle>
          <p className="text-sm font-bold">
            Travy ranks context before spending model budget.
          </p>
        </div>
        <NeoBadge tone={context.mode === "full_context" ? "mint" : context.mode === "low_budget" ? "orange" : "danger"}>
          {modeLabel}
        </NeoBadge>
      </div>
      <div className="overflow-x-auto neo-scrollbar">
        <table className="w-full min-w-[620px] border-collapse text-left text-sm">
          <thead>
            <tr className="border-b-2 border-black bg-white">
              <th className="p-2 font-black">Priority</th>
              <th className="p-2 font-black">Context</th>
              <th className="p-2 font-black">Used?</th>
              <th className="p-2 font-black">Reason</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([priority, label, key, reason]) => {
              const used = context.included.includes(key);
              return (
                <tr key={key} className="border-b-2 border-black bg-white/75">
                  <td className="p-2 font-mono font-black">{priority}</td>
                  <td className="p-2 font-bold">{label}</td>
                  <td className="p-2">
                    <NeoBadge tone={used ? "mint" : "danger"}>{used ? "Yes" : "Dropped"}</NeoBadge>
                  </td>
                  <td className="p-2 font-semibold">{reason}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </NeoCard>
  );
}
