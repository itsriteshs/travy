import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Tone = "default" | "yellow" | "blue" | "pink" | "mint" | "orange" | "lavender" | "danger" | "ink";

const tones: Record<Tone, string> = {
  default: "bg-white text-black",
  yellow: "bg-travyYellow text-black",
  blue: "bg-travyBlue text-black",
  pink: "bg-travyPink text-black",
  mint: "bg-travyMint text-black",
  orange: "bg-travyOrange text-black",
  lavender: "bg-travyLavender text-black",
  danger: "bg-travyDanger text-black",
  ink: "bg-travyInk text-white"
};

export function NeoBadge({
  className,
  tone = "default",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-[4px] border-2 border-black px-2 py-1 font-mono text-xs font-black uppercase leading-none",
        tones[tone],
        className
      )}
      {...props}
    />
  );
}
