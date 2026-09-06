"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Show, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

const LINKS = [
  { href: "/", label: "Bu Hafta", authOnly: false },
  { href: "/predictions", label: "Tahminlerim", authOnly: true },
  { href: "/gruplar", label: "Gruplar", authOnly: true },
  { href: "/profil", label: "Profil", authOnly: true },
  { href: "/topluluk", label: "Topluluk Tahminleri", authOnly: false },
  { href: "/leaderboard", label: "Lider Tablosu", authOnly: false },
] as const;

function NavLink({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <Link
      href={href}
      className={`shrink-0 border-b-2 pb-0.5 transition-colors ${
        active
          ? "border-lime-300 text-white"
          : "border-transparent text-slate-400 hover:text-white"
      }`}
    >
      {label}
    </Link>
  );
}

export function NavBar() {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex max-w-4xl flex-col gap-2 px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
          <div className="flex min-w-0 items-center gap-3">
            <a
              href="https://metric11.com"
              className="shrink-0 text-xs text-slate-500 hover:text-slate-300"
            >
              ← metric11.com
            </a>
            <Link href="/" className="flex shrink-0 items-center gap-2 font-bold text-lg">
              <span className="grid h-7 w-7 place-items-center rounded-md bg-lime-300 text-slate-900 text-sm">
                11
              </span>
              <span className="hidden sm:inline">
                metric11 <span className="text-lime-300">Tahmin</span>
              </span>
            </Link>
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <Show when="signed-out">
              <SignInButton mode="modal">
                <button className="cursor-pointer text-sm text-slate-300 hover:text-white">Giriş Yap</button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="cursor-pointer rounded-md bg-lime-300 px-3 py-1.5 text-sm font-semibold text-slate-900">
                  Üye Ol
                </button>
              </SignUpButton>
            </Show>
            <Show when="signed-in">
              <UserButton />
            </Show>
          </div>
        </div>
        <nav className="flex items-center gap-4 overflow-x-auto text-sm">
          {LINKS.map((link) =>
            link.authOnly ? (
              <Show key={link.href} when="signed-in">
                <NavLink href={link.href} label={link.label} active={pathname === link.href} />
              </Show>
            ) : (
              <NavLink key={link.href} href={link.href} label={link.label} active={pathname === link.href} />
            )
          )}
        </nav>
      </div>
    </header>
  );
}
