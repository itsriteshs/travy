"use client";

import type { ReactNode } from "react";
import { ArrowRight } from "lucide-react";
import { NeoButton } from "@/components/ui/neo-button";
import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";

export function DemoActionCard({
  title,
  description,
  tone,
  icon,
  actionLabel,
  onAction
}: {
  title: string;
  description: string;
  tone: "yellow" | "blue" | "pink" | "mint" | "orange" | "lavender" | "danger";
  icon: ReactNode;
  actionLabel: string;
  onAction: () => void;
}) {
  return (
    <NeoCard tone={tone} strong className="flex h-full flex-col justify-between gap-5">
      <div>
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-neo border-2 border-black bg-white shadow-neoSm">
          {icon}
        </div>
        <NeoCardTitle>{title}</NeoCardTitle>
        <p className="mt-2 text-sm font-bold leading-6">{description}</p>
      </div>
      <NeoButton variant="secondary" onClick={onAction} rightIcon={<ArrowRight className="h-4 w-4" aria-hidden />}>
        {actionLabel}
      </NeoButton>
    </NeoCard>
  );
}
