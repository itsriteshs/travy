import { cva } from 'class-variance-authority'

import { cn } from '../../lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center px-5 py-2.5 text-sm font-bold uppercase tracking-widest cursor-pointer border-[3px] border-black disabled:pointer-events-none disabled:opacity-40 brutal-press',
  {
    variants: {
      variant: {
        default: 'bg-[var(--primary)] text-black shadow-[4px_4px_0_#000]',
        accent: 'bg-[var(--yellow)] text-black shadow-[4px_4px_0_#000]',
        secondary: 'bg-white text-black shadow-[4px_4px_0_#000]',
        ghost: 'bg-transparent text-black border-transparent shadow-none',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

export function Button({ className, variant, ...props }) {
  return <button className={cn(buttonVariants({ variant }), className)} {...props} />
}
