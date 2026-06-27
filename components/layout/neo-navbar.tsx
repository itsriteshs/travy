"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MapPinned } from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Home" },
  { href: "/planner", label: "Planner" },
  { href: "/results", label: "Results" },
  { href: "/ai-router", label: "AI Router" },
  { href: "/security", label: "Security" },
  { href: "/demo", label: "Demo" }
];

export function NeoNavbar() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-50 border-b-4 border-black bg-travyPaper">
      <nav className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between">
        <Link
          href="/"
          className="focus-neo inline-flex w-fit items-center gap-2 rounded-neo border-2 border-black bg-travyYellow px-3 py-2 font-black shadow-neoSm"
        >
          <MapPinned className="h-5 w-5" aria-hidden />
          Travy
        </Link>
        <div className="flex flex-wrap gap-2">
          {links.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "focus-neo rounded-neo border-2 border-black px-3 py-2 text-sm font-black transition-all active:translate-x-1 active:translate-y-1 active:shadow-none",
                  active
                    ? "bg-travyBlue shadow-neoSm"
                    : "bg-white hover:bg-travySunwash hover:shadow-neoSm"
                )}
                aria-current={active ? "page" : undefined}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
