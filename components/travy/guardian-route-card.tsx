import { ShieldCheck } from "lucide-react";
import { NeoBadge } from "@/components/ui/neo-badge";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";
import { guardianRoute } from "@/lib/travy/demo-data";
import { cn } from "@/lib/utils";
import type { GuardianRoute } from "@/lib/travy/types";

export function GuardianRouteCard({
  highlight = false,
  route = guardianRoute
}: {
  highlight?: boolean;
  route?: GuardianRoute;
}) {
  return (
    <NeoCard tone="mint" strong className={cn(highlight && "ring-4 ring-travyDanger")}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <NeoCardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-6 w-6" aria-hidden />
            Guardian Route
          </NeoCardTitle>
          <p className="text-sm font-bold">{route.disclaimer}</p>
        </div>
        <NeoBadge tone="mint">Available</NeoBadge>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-neo border-2 border-black bg-white p-3">
          <div className="text-xs font-black uppercase">Fastest Route</div>
          <div className="font-mono text-3xl font-black">{route.fastestRoute.time}</div>
          <p className="text-sm font-bold">{route.fastestRoute.note}</p>
        </div>
        <div className="rounded-neo border-2 border-black bg-travySunwash p-3">
          <div className="text-xs font-black uppercase">Guardian Route</div>
          <div className="font-mono text-3xl font-black">{route.guardianRoute.time}</div>
          <p className="text-sm font-bold">{route.guardianRoute.note}</p>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {route.signals.map((signal) => (
          <NeoBadge key={signal} tone="default">
            {signal}
          </NeoBadge>
        ))}
      </div>
    </NeoCard>
  );
}
