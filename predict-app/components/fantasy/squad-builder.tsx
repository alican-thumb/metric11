"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { FantasyPlayer, PositionGroup } from "@/lib/fantasy-data";
import { BUDGET, SQUAD_POSITION_COUNTS, MAX_PER_TEAM, validateSquad, squadCost } from "@/lib/fantasy-rules";
import { Pitch, PlayerChip, groupByPosition } from "./pitch";

const POSITION_TABS: { key: PositionGroup | "ALL"; label: string }[] = [
  { key: "ALL", label: "Tümü" },
  { key: "GK", label: "Kaleci" },
  { key: "DEF", label: "Defans" },
  { key: "MID", label: "Orta Saha" },
  { key: "FWD", label: "Forvet" },
];

export function SquadBuilder({ allPlayers }: { allPlayers: FantasyPlayer[] }) {
  const router = useRouter();
  const [selected, setSelected] = useState<FantasyPlayer[]>([]);
  const [posFilter, setPosFilter] = useState<PositionGroup | "ALL">("ALL");
  const [teamFilter, setTeamFilter] = useState<string>("ALL");
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const teams = useMemo(() => [...new Set(allPlayers.map((p) => p.team))].sort(), [allPlayers]);
  const selectedIds = useMemo(() => new Set(selected.map((p) => p.transfermarkt_id)), [selected]);
  const cost = squadCost(selected);
  const remaining = Math.round((BUDGET - cost) * 10) / 10;

  const byPosition: Record<string, number> = {};
  const byTeam: Record<string, number> = {};
  for (const p of selected) {
    byPosition[p.position_group] = (byPosition[p.position_group] ?? 0) + 1;
    byTeam[p.team] = (byTeam[p.team] ?? 0) + 1;
  }

  const filtered = allPlayers
    .filter((p) => !selectedIds.has(p.transfermarkt_id))
    .filter((p) => posFilter === "ALL" || p.position_group === posFilter)
    .filter((p) => teamFilter === "ALL" || p.team === teamFilter)
    .filter((p) => p.name.toLocaleUpperCase("tr-TR").includes(search.toLocaleUpperCase("tr-TR")))
    .sort((a, b) => b.price - a.price)
    .slice(0, 60);

  function canAdd(p: FantasyPlayer): string | null {
    if (selected.length >= 15) return "Kadro dolu (15/15).";
    if ((byPosition[p.position_group] ?? 0) >= SQUAD_POSITION_COUNTS[p.position_group]) {
      return `${p.position_group} kontenjanı dolu.`;
    }
    if ((byTeam[p.team] ?? 0) >= MAX_PER_TEAM) return `${p.team}'dan en fazla ${MAX_PER_TEAM} oyuncu.`;
    if (cost + p.price > BUDGET + 1e-6) return "Bütçe yetersiz.";
    return null;
  }

  function add(p: FantasyPlayer) {
    if (canAdd(p)) return;
    setSelected((s) => [...s, p]);
    setError(null);
  }
  function remove(id: string) {
    setSelected((s) => s.filter((p) => p.transfermarkt_id !== id));
    setError(null);
  }

  const validation = validateSquad(selected);
  const groups = groupByPosition(selected);

  async function save() {
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/fantasy/squad", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transfermarktIds: selected.map((p) => p.transfermarkt_id) }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error ?? "Kadro kaydedilemedi.");
        setSaving(false);
        return;
      }
      router.push("/kadro/hafta");
      router.refresh();
    } catch {
      setError("Bağlantı hatası.");
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 to-slate-950 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-lime-300">{remaining.toFixed(1)}</span>
            <span className="text-xs text-slate-400">/ {BUDGET.toFixed(1)} bütçe kaldı</span>
          </div>
          <div className="flex gap-3 text-xs text-slate-400">
            {(Object.keys(SQUAD_POSITION_COUNTS) as PositionGroup[]).map((pos) => (
              <span key={pos} className={byPosition[pos] === SQUAD_POSITION_COUNTS[pos] ? "text-lime-300" : ""}>
                {pos} {byPosition[pos] ?? 0}/{SQUAD_POSITION_COUNTS[pos]}
              </span>
            ))}
          </div>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${
              remaining < 0 ? "from-red-500 to-red-600" : "from-lime-400 to-emerald-500"
            } transition-all`}
            style={{ width: `${Math.min(100, (cost / BUDGET) * 100)}%` }}
          />
        </div>
      </div>

      <Pitch
        gk={groups.gk}
        def={groups.def}
        mid={groups.mid}
        fwd={groups.fwd}
        renderChip={(p) => (
          <PlayerChip key={p.transfermarkt_id} player={p} sublabel={p.price.toFixed(1)} removable onClick={() => remove(p.transfermarkt_id)} />
        )}
      />
      {selected.length < 15 && (
        <p className="text-center text-xs text-slate-500">
          {15 - selected.length} oyuncu daha seç ({selected.length}/15)
        </p>
      )}

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-3">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          {POSITION_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setPosFilter(tab.key)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                posFilter === tab.key ? "bg-lime-300 text-slate-900" : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
          <select
            value={teamFilter}
            onChange={(e) => setTeamFilter(e.target.value)}
            className="ml-auto rounded-md border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-slate-200"
          >
            <option value="ALL">Tüm takımlar</option>
            {teams.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Oyuncu ara…"
            className="w-full rounded-md border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-slate-200 sm:w-40"
          />
        </div>
        <div className="max-h-80 space-y-1 overflow-y-auto pr-1">
          {filtered.map((p) => {
            const blocked = canAdd(p);
            return (
              <button
                key={p.transfermarkt_id}
                onClick={() => add(p)}
                disabled={Boolean(blocked)}
                title={blocked ?? undefined}
                className="flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-sm transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-30"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span className="w-9 shrink-0 rounded bg-slate-800 px-1.5 py-0.5 text-center text-[10px] font-bold text-slate-300">
                    {p.position_group}
                  </span>
                  <span className="truncate">{p.name}</span>
                  <span className="shrink-0 truncate text-xs text-slate-500">{p.team}</span>
                </span>
                <span className="shrink-0 font-semibold text-lime-300">{p.price.toFixed(1)}</span>
              </button>
            );
          })}
          {filtered.length === 0 && <p className="py-4 text-center text-sm text-slate-500">Sonuç yok.</p>}
        </div>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}
      {!validation.ok && selected.length === 15 && <p className="text-sm text-amber-400">{validation.error}</p>}
      <button
        onClick={save}
        disabled={!validation.ok || saving}
        className="w-full cursor-pointer rounded-xl bg-gradient-to-r from-lime-300 to-emerald-400 py-3 text-center text-sm font-bold text-slate-950 shadow-lg shadow-lime-500/20 transition-transform hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-30"
      >
        {saving ? "Kaydediliyor…" : "Kadroyu Kaydet"}
      </button>
    </div>
  );
}
