import { cn } from '../../lib/utils'

export function Card({ className, ...props }) {
  return (
    <div
      className={cn('border-[3px] border-black bg-[var(--card)] text-[var(--card-foreground)] shadow-[6px_6px_0_#000]', className)}
      {...props}
    />
  )
}

export function CardHeader({ className, ...props }) {
  return <div className={cn('p-5 pb-3 border-b-[3px] border-black', className)} {...props} />
}

export function CardTitle({ className, ...props }) {
  return <h3 className={cn('m-0 text-base font-black uppercase tracking-widest', className)} {...props} />
}

export function CardContent({ className, ...props }) {
  return <div className={cn('p-5 pt-4', className)} {...props} />
}
