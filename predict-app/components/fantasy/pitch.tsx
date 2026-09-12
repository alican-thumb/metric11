import type { ReactNode } from "react";
import type { FantasyPlayer, PositionGroup } from "@/lib/fantasy-data";

const POSITION_COLOR: Record<PositionGroup, string> = {
  GK: "from-amber-400 to-amber-600",
  DEF: "from-sky-400 to-sky-600",
  MID: "from-lime-300 to-emerald-500",
  FWD: "from-rose-400 to-rose-600",
};

export function PlayerChip({
  player,
  sublabel,
  cornerBadge,
  onClick,
  removable,
  dimmed,
}: {
  player: FantasyPlayer;
  sublabel?: string;
  cornerBadge?: string;
  onClick?: () => void;
  removable?: boolean;
  dimmed?: boolean;
}) {
  const initials = player.name
    .split(" ")
    .filter(Boolean)
    .slice(-2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();

  return (
    <button
      type="button"
      onClick={onClick}
      className={`group flex w-[72px] shrink-0 flex-col items-center gap-1 sm:w-20 ${
        dimmed ? "opacity-40" : ""
      } ${onClick ? "cursor-pointer" : "cursor-default"}`}
    >
      <div className="relative">
        <div
          className={`grid h-11 w-11 place-items-center rounded-full bg-gradient-to-br ${POSITION_COLOR[player.position_group]} text-xs font-bold text-slate-950 shadow-lg shadow-black/30 ring-2 ring-slate-950/60 transition-transform group-hover:scale-105 sm:h-12 sm:w-12`}
        >
          {initials}
        </div>
        {cornerBadge && (
          <span className="absolute -right-1 -top-1 grid h-5 w-5 place-items-center rounded-full bg-slate-950 text-[10px] font-bold text-lime-300 ring-1 ring-lime-300">
            {cornerBadge}
          </span>
        )}
        {removable && (
          <span className="absolute -right-1 -bottom-1 grid h-5 w-5 place-items-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-slate-950">
            ×
          </span>
        )}
      </div>
      <span className="w-full truncate text-center text-[10px] font-medium text-white drop-shadow sm:text-[11px]">
        {shortName(player.name)}
      </span>
      {sublabel && <span className="text-[10px] text-lime-300/90 sm:text-[11px]">{sublabel}</span>}
    </button>
  );
}

export function shortName(fullName: string): string {
  const parts = fullName.trim().split(/\s+/);
  if (parts.length <= 1) return fullName;
  return parts[parts.length - 1];
}

export function Pitch({
  gk,
  def,
  mid,
  fwd,
  renderChip,
}: {
  gk: FantasyPlayer[];
  def: FantasyPlayer[];
  mid: FantasyPlayer[];
  fwd: FantasyPlayer[];
  renderChip: (p: FantasyPlayer) => ReactNode;
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-emerald-900 bg-gradient-to-b from-emerald-700 via-emerald-800 to-emerald-950 p-3 shadow-inner sm:p-6">
      <div className="pointer-events-none absolute inset-3 rounded-xl border border-white/15 sm:inset-5" />
      <div className="pointer-events-none absolute left-1/2 top-3 bottom-3 hidden w-px -translate-x-1/2 bg-white/15 sm:block sm:top-5 sm:bottom-5" />
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-16 w-16 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/15 sm:h-24 sm:w-24" />
      <div className="relative flex flex-col gap-4 py-2 sm:gap-6 sm:py-4">
        <div className="flex justify-center gap-3 sm:gap-6">{fwd.map((p) => renderChip(p))}</div>
        <div className="flex justify-center gap-3 sm:gap-6">{mid.map((p) => renderChip(p))}</div>
        <div className="flex justify-center gap-3 sm:gap-6">{def.map((p) => renderChip(p))}</div>
        <div className="flex justify-center gap-3 sm:gap-6">{gk.map((p) => renderChip(p))}</div>
      </div>
    </div>
  );
}

export function groupByPosition(players: FantasyPlayer[]) {
  return {
    gk: players.filter((p) => p.position_group === "GK"),
    def: players.filter((p) => p.position_group === "DEF"),
    mid: players.filter((p) => p.position_group === "MID"),
    fwd: players.filter((p) => p.position_group === "FWD"),
  };
}
