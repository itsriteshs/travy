import { cn } from "@/lib/utils";

export function NeoProgress({
  value,
  label,
  tone = "yellow",
  className
}: {
  value: number;
  label?: string;
  tone?: "yellow" | "blue" | "mint" | "pink" | "orange" | "danger" | "lavender";
  className?: string;
}) {
  const colors = {
    yellow: "bg-travyYellow",
    blue: "bg-travyBlue",
    mint: "bg-travyMint",
    pink: "bg-travyPink",
    orange: "bg-travyOrange",
    danger: "bg-travyDanger",
    lavender: "bg-travyLavender"
  };
  const safeValue = Math.max(0, Math.min(100, value));
  return (
    <div className={cn("space-y-2", className)}>
      {label && <div className="text-xs font-black uppercase">{label}</div>}
      <div className="h-5 overflow-hidden rounded-[4px] border-2 border-black bg-white">
        <div
          className={cn("h-full border-r-2 border-black", colors[tone])}
          style={{ width: `${safeValue}%` }}
          role="progressbar"
          aria-valuenow={safeValue}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={label || "Progress"}
        />
      </div>
    </div>
  );
}
