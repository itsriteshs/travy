import type { TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import { neoFocus } from "@/lib/styles/neo";

type NeoTextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label: string;
  helperText?: string;
  error?: string;
};

export function NeoTextarea({
  label,
  helperText,
  error,
  id,
  className,
  ...props
}: NeoTextareaProps) {
  const inputId = id || props.name || label.toLowerCase().replace(/\s+/g, "-");
  const helperId = `${inputId}-helper`;
  return (
    <label className="block space-y-2" htmlFor={inputId}>
      <span className="text-xs font-black uppercase">{label}</span>
      <textarea
        id={inputId}
        aria-describedby={helperText || error ? helperId : undefined}
        aria-invalid={Boolean(error)}
        className={cn(
          "min-h-40 w-full resize-y rounded-neo border-2 border-black bg-white px-4 py-3 text-base font-bold leading-7 shadow-neoSm",
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
