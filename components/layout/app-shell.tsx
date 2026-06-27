import type { ReactNode } from "react";
import { NeoNavbar } from "./neo-navbar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <NeoNavbar />
      <main>{children}</main>
    </div>
  );
}
