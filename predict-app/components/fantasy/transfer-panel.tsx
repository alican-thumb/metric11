"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { FantasyPlayer } from "@/lib/fantasy-data";
import { BUDGET, MAX_PER_TEAM, squadCost } from "@/lib/fantasy-rules";

export function TransferPanel({
  squadPlayers,
  allPlayers,
  freeTransfers,
  locked,
}: {
  squadPlayers: FantasyPlayer[];
  allPlayers: FantasyPlayer[];
  freeTransfers: number;
  locked: boolean;
}) {
  const router = useRouter();
  const [outId, setOutId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const squadIds = useMemo(() => new Set(squadPlayers.map((p) => p.transfermarkt_id)), [squadPlayers]);
  const currentCost = squadCost(squadPlayers);
  const outPlayer = squadPlayers.find((p) => p.transfermarkt_id === outId) ?? null;

  const byTeamCount: Record<string, number> = {};
  for (const p of squadPlayers) byTeamCount[p.team] = (byTeamCount[p.team] ?? 0) + 1;

  const candidates = outPlayer
    ? allPlayers
        .filter((p) => !squadIds.has(p.transfermarkt_id))
        .filter((p) => p.position_group === outPlayer.position_group)
        .filter((p) => currentCost - outPlayer.price + p.price <= BUDGET + 1e-6)
        .filter((p) => (byTeamCount[p.team] ?? 0) + (p.team === outPlayer.team ? -1 : 0) < MAX_PER_TEAM)
        .sort((a, b) => b.price - a.price)
        .slice(0, 40)
    : [];

  async function confirmTransfer(inId: string) {
    if (!outId) return;
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/fantasy/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ playerOutId: outId, playerInId: inId }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error ?? "Transfer başarısız.");
        setSaving(false);
        return;
      }
      setOutId(null);
      setSaving(false);
      router.refresh();
    } catch {
      setError("Bağlantı hatası.");
      setSaving(false);
    }
  }

  if (locked) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
        🔒 Bu hafta maçlar başladığı için transfer kapalı.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm">
        <span className="text-slate-300">Ücretsiz transfer</span>
        <span className={`font-bold ${freeTransfers > 0 ? "text-lime-300" : "text-amber-400"}`}>
          {freeTransfers > 0 ? freeTransfers : "0 (-4 puan)"}
        </span>
      </div>

      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Kadrondan çıkar</p>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {squadPlayers.map((p) => (
            <button
              key={p.transfermarkt_id}
              onClick={() => setOutId(p.transfermarkt_id)}
              className={`rounded-lg border px-2 py-2 text-left text-xs transition-colors ${
                outId === p.transfermarkt_id
                  ? "border-lime-300 bg-lime-300/10 text-lime-300"
                  : "border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-600"
              }`}
            >
              <div className="truncate font-medium">{p.name}</div>
              <div className="flex justify-between text-slate-500">
                <span>{p.position_group}</span>
                <span>{p.price.toFixed(1)}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {outPlayer && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            {outPlayer.name} yerine getir ({outPlayer.position_group})
          </p>
          <div className="max-h-72 space-y-1 overflow-y-auto rounded-xl border border-slate-800 bg-slate-900/40 p-2">
            {candidates.map((p) => (
              <button
                key={p.transfermarkt_id}
                onClick={() => confirmTransfer(p.transfermarkt_id)}
                disabled={saving}
                className="flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-sm transition-colors hover:bg-slate-800 disabled:opacity-40"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span className="truncate">{p.name}</span>
                  <span className="shrink-0 truncate text-xs text-slate-500">{p.team}</span>
                </span>
                <span className="shrink-0 font-semibold text-lime-300">{p.price.toFixed(1)}</span>
              </button>
            ))}
            {candidates.length === 0 && <p className="py-4 text-center text-sm text-slate-500">Bütçe/kontenjana uyan aday yok.</p>}
          </div>
        </div>
      )}

      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
}
