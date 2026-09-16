"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Show, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

const LINKS = [
  { href: "/", label: "Bu Hafta", authOnly: false, highlight: false },
  { href: "/predictions", label: "Tahminlerim", authOnly: true, highlight: false },
  { href: "/kadro", label: "Kadro Kur", authOnly: false, highlight: false },
  { href: "/taraftar", label: "Tribün Lideri", authOnly: false, highlight: true },
  { href: "/gruplar", label: "Gruplar", authOnly: true, highlight: false },
  { href: "/profil", label: "Profil", authOnly: true, highlight: false },
  { href: "/topluluk", label: "Topluluk Tahminleri", authOnly: false, highlight: false },
  { href: "/leaderboard", label: "Lider Tablosu", authOnly: false, highlight: false },
] as const;

function NavLink({
  href,
  label,
  active,
  highlight,
}: {
  href: string;
  label: string;
  active: boolean;
  highlight?: boolean;
}) {
  return (
    <Link
      href={href}
      className={`relative shrink-0 border-b-2 pb-0.5 transition-colors ${
        active
          ? "border-lime-300 text-white"
          : "border-transparent text-slate-400 hover:text-white"
      } ${highlight && !active ? "font-semibold text-lime-300" : ""}`}
    >
      {label}
      {highlight && (
        <span className="absolute -right-2 -top-1.5 flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-lime-300 opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-lime-300" />
        </span>
      )}
    </Link>
  );
}

function isActivePath(pathname: string, href: string): boolean {
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
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
                <NavLink
                  href={link.href}
                  label={link.label}
                  active={isActivePath(pathname, link.href)}
                  highlight={link.highlight}
                />
              </Show>
            ) : (
              <NavLink
                key={link.href}
                href={link.href}
                label={link.label}
                active={isActivePath(pathname, link.href)}
                highlight={link.highlight}
              />
            )
          )}
        </nav>
      </div>
    </header>
  );
}
