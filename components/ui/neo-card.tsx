import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type NeoCardProps = HTMLAttributes<HTMLDivElement> & {
  tone?: "paper" | "yellow" | "blue" | "pink" | "mint" | "orange" | "lavender" | "danger" | "ink";
  shadow?: "sm" | "md" | "lg" | "none";
  strong?: boolean;
  interactive?: boolean;
};

const tones = {
  paper: "bg-white text-black",
  yellow: "bg-travyYellow text-black",
  blue: "bg-travyBlue text-black",
  pink: "bg-travyPink text-black",
  mint: "bg-travyMint text-black",
  orange: "bg-travyOrange text-black",
  lavender: "bg-travyLavender text-black",
  danger: "bg-travyDanger text-black",
  ink: "bg-travyInk text-white"
};

const shadows = {
  sm: "shadow-neoSm",
  md: "shadow-neo",
  lg: "shadow-neoLg",
  none: "shadow-none"
};

export function NeoCard({
  className,
  tone = "paper",
  shadow = "md",
  strong = false,
  interactive = false,
  ...props
}: NeoCardProps) {
  return (
    <div
      className={cn(
        "rounded-neo p-4",
        strong ? "border-4" : "border-2",
        "border-black",
        tones[tone],
        shadows[shadow],
        interactive &&
          "transition-all hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-neoLg",
        className
      )}
      {...props}
    />
  );
}

export function NeoCardHeader({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-4 space-y-1", className)} {...props} />;
}

export function NeoCardTitle({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLHeadingElement> & { children: ReactNode }) {
  return (
    <h3 className={cn("text-xl font-black leading-tight", className)} {...props}>
      {children}
    </h3>
  );
}

export function NeoCardDescription({
  className,
  ...props
}: HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-sm font-semibold leading-6 text-zinc-700", className)} {...props} />;
}
