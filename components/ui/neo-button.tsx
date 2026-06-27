import Link from "next/link";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { neoFocus, neoPress } from "@/lib/styles/neo";

type CommonProps = {
  variant?: "primary" | "secondary" | "accent" | "danger" | "ghost" | "mint" | "lavender";
  size?: "sm" | "md" | "lg" | "icon";
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  className?: string;
  children: ReactNode;
};

type ButtonProps = CommonProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    href?: never;
  };

type LinkProps = CommonProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    href: string;
  };

const variants = {
  primary: "bg-travyYellow text-black hover:bg-travyYellowHover",
  secondary: "bg-white text-black hover:bg-travySunwash",
  accent: "bg-travyBlue text-black hover:bg-sky-300",
  danger: "bg-travyDanger text-black hover:bg-red-400",
  ghost: "border-transparent bg-transparent shadow-none hover:bg-white",
  mint: "bg-travyMint text-black hover:bg-emerald-300",
  lavender: "bg-travyLavender text-black hover:bg-violet-300"
};

const sizes = {
  sm: "min-h-10 px-3 py-2 text-xs",
  md: "min-h-11 px-4 py-2 text-sm",
  lg: "min-h-14 px-6 py-3 text-base md:text-lg",
  icon: "h-11 w-11 p-0"
};

function content({
  loading,
  leftIcon,
  rightIcon,
  children
}: Pick<CommonProps, "loading" | "leftIcon" | "rightIcon" | "children">) {
  return (
    <>
      {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : leftIcon}
      <span>{children}</span>
      {rightIcon}
    </>
  );
}

export function NeoButton(props: ButtonProps | LinkProps) {
  const {
    variant = "primary",
    size = "md",
    loading = false,
    leftIcon,
    rightIcon,
    className,
    children,
    ...rest
  } = props;

  const classes = cn(
    "inline-flex items-center justify-center gap-2 rounded-neo border-2 border-black font-black uppercase tracking-normal shadow-neo",
    "disabled:cursor-not-allowed disabled:border-zinc-500 disabled:bg-zinc-300 disabled:text-zinc-600 disabled:shadow-none",
    "hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-neoLg",
    neoPress,
    neoFocus,
    variants[variant],
    sizes[size],
    className
  );

  if ("href" in props && props.href) {
    const { href, ...linkRest } = rest as LinkProps;
    return (
      <Link className={classes} href={href} {...linkRest}>
        {content({ loading, leftIcon, rightIcon, children })}
      </Link>
    );
  }

  const { disabled, ...buttonRest } = rest as ButtonProps;

  return (
    <button className={classes} disabled={loading || disabled} {...buttonRest}>
      {content({ loading, leftIcon, rightIcon, children })}
    </button>
  );
}
