import { cn } from '../../lib/utils'

export function Textarea({ className, ...props }) {
  return (
    <textarea
      className={cn(
        'min-h-28 w-full rounded-lg border border-[var(--border)] bg-white p-3 text-sm outline-none ring-[var(--primary)] placeholder:text-[var(--muted-foreground)] focus:ring-2',
        className,
      )}
      {...props}
    />
  )
}
