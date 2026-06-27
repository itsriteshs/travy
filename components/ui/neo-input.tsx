import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { neoFocus } from "@/lib/styles/neo";

type NeoInputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  helperText?: string;
  error?: string;
};

export function NeoInput({ label, helperText, error, id, className, ...props }: NeoInputProps) {
  const inputId = id || props.name || label.toLowerCase().replace(/\s+/g, "-");
  const helperId = `${inputId}-helper`;
  return (
    <label className="block space-y-2" htmlFor={inputId}>
      <span className="text-xs font-black uppercase">{label}</span>
      <input
        id={inputId}
        aria-describedby={helperText || error ? helperId : undefined}
        aria-invalid={Boolean(error)}
        className={cn(
          "h-11 w-full rounded-neo border-2 border-black bg-white px-3 font-bold shadow-neoSm",
          neoFocus,
          error && "bg-red-50",
          className
        )}
        {...props}
      />
      {(helperText || error) && (
        <span
          id={helperId}
          className={cn("block text-sm font-bold", error ? "text-red-700" : "text-zinc-700")}
        >
          {error || helperText}
        </span>
      )}
    </label>
  );
}
