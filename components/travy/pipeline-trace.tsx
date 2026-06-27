import { ArrowRight } from "lucide-react";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";

export function PipelineTrace({ steps }: { steps: string[] }) {
  return (
    <NeoCard tone="blue" strong>
      <NeoCardTitle className="mb-4">Pipeline Trace</NeoCardTitle>
      <div className="flex flex-wrap items-center gap-2">
        {steps.map((step, index) => (
          <div key={step} className="flex items-center gap-2">
            <span className="rounded-neo border-2 border-black bg-white px-3 py-2 text-sm font-black">
              {step}
            </span>
            {index < steps.length - 1 && <ArrowRight className="h-5 w-5" aria-hidden />}
          </div>
        ))}
      </div>
    </NeoCard>
  );
}
