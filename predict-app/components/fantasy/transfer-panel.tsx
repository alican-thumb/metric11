"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { FantasyPlayer } from "@/lib/fantasy-data";
import { BUDGET, MAX_PER_TEAM, squadCost } from "@/lib/fantasy-rules";
import { Pitch, PlayerChip, groupByPosition } from "./pitch";

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
  const groups = groupByPosition(squadPlayers);

  const byTeamCount: Record<string, number> = {};
  for (const p of squadPlayers) byTeamCount[p.team] = (byTeamCount[p.team] ?? 0) + 1;

  const remainingBudget = BUDGET - currentCost;
  const maxAffordable = outPlayer ? BUDGET - (currentCost - outPlayer.price) : 0;

  const samePositionPool = outPlayer
    ? allPlayers.filter((p) => !squadIds.has(p.transfermarkt_id) && p.position_group === outPlayer.position_group)
    : [];
  const affordablePool = outPlayer ? samePositionPool.filter((p) => p.price <= maxAffordable + 1e-6) : [];
  const candidates = outPlayer
    ? affordablePool
        .filter((p) => (byTeamCount[p.team] ?? 0) + (p.team === outPlayer.team ? -1 : 0) < MAX_PER_TEAM)
        .sort((a, b) => b.price - a.price)
        .slice(0, 40)
    : [];
  // Bütçeye uyan aday VAR ama hepsi 3-oyuncu/takım kotasına takılıyorsa kullanıcıya
  // "bütçe yetersiz" değil "takımdan zaten 3 oyuncun var" demek gerekir — 2026-09-16
  // kullanıcı geri bildirimi: "uygun oyuncu yok" mesajı neden olduğunu açıklamıyordu.
  const quotaBlockedOnly = outPlayer && affordablePool.length > 0 && candidates.length === 0;

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

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-slate-300">Kadro bütçesi</span>
          <span className="font-bold text-white">
            {currentCost.toFixed(1)} / {BUDGET.toFixed(1)}{" "}
            <span className={remainingBudget > 0.5 ? "text-lime-300" : "text-amber-400"}>
              ({remainingBudget.toFixed(1)} boşta)
            </span>
          </span>
        </div>
        {remainingBudget < 1 && (
          <p className="mt-1 text-[11px] text-amber-400">
            Bütçen dolmuş — yeni oyuncu alabilmek için çıkardığın oyuncudan daha ucuz birini seçmelisin.
          </p>
        )}
      </div>

      <p className="text-center text-xs text-slate-400">
        <span className="font-bold text-lime-300">1.</span> Çıkaracağın oyuncuya dokun (kırmızı{" "}
        <span className="font-bold text-red-400">×</span> işaretli) &nbsp;→&nbsp;{" "}
        <span className="font-bold text-lime-300">2.</span> Yerine gelecek oyuncuyu seç
      </p>

      <Pitch
        gk={groups.gk}
        def={groups.def}
        mid={groups.mid}
        fwd={groups.fwd}
        renderChip={(p) => (
          <PlayerChip
            key={p.transfermarkt_id}
            player={p}
            sublabel={p.price.toFixed(1)}
            removable
            dimmed={outId !== null && outId !== p.transfermarkt_id}
            onClick={() => setOutId(p.transfermarkt_id)}
          />
        )}
      />

      {outPlayer && (
        <div className="rounded-xl border border-lime-300/30 bg-lime-300/5 p-3">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-lime-300">
              {outPlayer.name} yerine getir ({outPlayer.position_group})
            </p>
            <button
              onClick={() => setOutId(null)}
              className="text-xs font-semibold text-slate-500 underline decoration-dotted underline-offset-4 hover:text-slate-300"
            >
              Vazgeç
            </button>
          </div>
          <p className="mb-2 text-[11px] text-slate-500">
            En fazla <span className="font-semibold text-slate-300">{maxAffordable.toFixed(1)}</span> birimlik oyuncu
            alabilirsin (bu oyuncuyu çıkarınca boşalacak bütçe).
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
            {candidates.length === 0 && quotaBlockedOnly && (
              <p className="py-4 text-center text-sm text-slate-500">
                Bütçene uyan adaylar var ama hepsi aynı takımdan — o takımdan zaten{" "}
                <span className="font-semibold text-slate-300">{MAX_PER_TEAM}</span> oyuncun var. Farklı bir takımdan
                oyuncu ara.
              </p>
            )}
            {candidates.length === 0 && !quotaBlockedOnly && (
              <p className="py-4 text-center text-sm text-slate-500">
                {outPlayer.position_group} pozisyonunda{" "}
                <span className="font-semibold text-slate-300">{maxAffordable.toFixed(1)}</span> birimin altında
                oyuncu yok — daha pahalı birini çıkarırsan bütçen genişler.
              </p>
            )}
          </div>
        </div>
      )}

      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
}
