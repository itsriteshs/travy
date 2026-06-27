import { cn } from '../../lib/utils'

export function Textarea({ className, ...props }) {
  return (
    <textarea
      className={cn(
        'min-h-28 w-full border-[3px] border-black bg-white p-3 text-sm font-medium outline-none placeholder:text-[var(--muted-foreground)] focus:shadow-[4px_4px_0_#000] focus:outline-none transition-shadow',
        className,
      )}
      {...props}
    />
  )
}
