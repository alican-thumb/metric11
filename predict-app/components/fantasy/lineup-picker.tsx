"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { FantasyPlayer } from "@/lib/fantasy-data";
import { STARTING_XI_SIZE, validateStartingXi, formationLabel } from "@/lib/fantasy-rules";
import { Pitch, PlayerChip, groupByPosition } from "./pitch";

type InitialLineupRow = { transfermarktId: string; isStarting: boolean; isCaptain: boolean; isViceCaptain: boolean };

function defaultStarters(players: FantasyPlayer[]): Set<string> {
  const gk = players.filter((p) => p.position_group === "GK").slice(0, 1);
  const def = players.filter((p) => p.position_group === "DEF").slice(0, 4);
  const mid = players.filter((p) => p.position_group === "MID").slice(0, 4);
  const fwd = players.filter((p) => p.position_group === "FWD").slice(0, 2);
  return new Set([...gk, ...def, ...mid, ...fwd].map((p) => p.transfermarkt_id));
}

export function LineupPicker({
  squadPlayers,
  initialLineup,
  week,
  deadlineLabel,
  locked,
}: {
  squadPlayers: FantasyPlayer[];
  initialLineup: InitialLineupRow[] | null;
  week: number | null;
  deadlineLabel: string | null;
  locked: boolean;
}) {
  const router = useRouter();

  const [starters, setStarters] = useState<Set<string>>(() => {
    if (initialLineup && initialLineup.length > 0) {
      return new Set(initialLineup.filter((r) => r.isStarting).map((r) => r.transfermarktId));
    }
    return defaultStarters(squadPlayers);
  });
  const [captainId, setCaptainId] = useState<string | undefined>(
    initialLineup?.find((r) => r.isCaptain)?.transfermarktId
  );
  const [viceCaptainId, setViceCaptainId] = useState<string | undefined>(
    initialLineup?.find((r) => r.isViceCaptain)?.transfermarktId
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const startingPlayers = squadPlayers.filter((p) => starters.has(p.transfermarkt_id));
  const benchPlayers = squadPlayers.filter((p) => !starters.has(p.transfermarkt_id));
  const groups = groupByPosition(startingPlayers);
  const validation = validateStartingXi(startingPlayers);

  function toggle(id: string) {
    if (locked) return;
    setSaved(false);
    setStarters((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
        if (captainId === id) setCaptainId(undefined);
        if (viceCaptainId === id) setViceCaptainId(undefined);
      } else {
        if (next.size >= STARTING_XI_SIZE) return prev;
        next.add(id);
      }
      return next;
    });
  }

  async function save() {
    if (!captainId || !viceCaptainId || !week) return;
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/fantasy/lineup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ week, starterIds: [...starters], captainId, viceCaptainId }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error ?? "Kaydedilemedi.");
        setSaving(false);
        return;
      }
      setSaved(true);
      setSaving(false);
      router.refresh();
    } catch {
      setError("Bağlantı hatası.");
      setSaving(false);
    }
  }

  const captainOptions = startingPlayers;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3">
        <span className="text-sm text-slate-300">
          {week ? `${week}. Hafta` : "Hafta"} · Diziliş <span className="font-semibold text-lime-300">{formationLabel(startingPlayers)}</span>
        </span>
        {locked ? (
          <span className="rounded-full bg-red-500/20 px-3 py-1 text-xs font-semibold text-red-300">🔒 Kilitli — maçlar başladı</span>
        ) : (
          deadlineLabel && <span className="text-xs text-slate-400">Son tarih: {deadlineLabel}</span>
        )}
      </div>

      <Pitch
        gk={groups.gk}
        def={groups.def}
        mid={groups.mid}
        fwd={groups.fwd}
        renderChip={(p) => (
          <PlayerChip
            key={p.transfermarkt_id}
            player={p}
            cornerBadge={p.transfermarkt_id === captainId ? "C" : p.transfermarkt_id === viceCaptainId ? "VC" : undefined}
            onClick={() => toggle(p.transfermarkt_id)}
          />
        )}
      />

      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Yedekler</p>
        <div className="flex flex-wrap gap-3 rounded-xl border border-slate-800 bg-slate-900/40 p-3">
          {benchPlayers.map((p) => (
            <PlayerChip key={p.transfermarkt_id} player={p} sublabel={p.position_group} dimmed onClick={() => toggle(p.transfermarkt_id)} />
          ))}
        </div>
      </div>

      {!validation.ok && <p className="text-sm text-amber-400">{validation.error}</p>}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1 block text-xs text-slate-400">Kaptan (2x puan)</span>
          <select
            value={captainId ?? ""}
            onChange={(e) => setCaptainId(e.target.value || undefined)}
            disabled={locked}
            className="w-full rounded-md border border-slate-700 bg-slate-800 px-2 py-2 text-sm"
          >
            <option value="">Seç…</option>
            {captainOptions.map((p) => (
              <option key={p.transfermarkt_id} value={p.transfermarkt_id} disabled={p.transfermarkt_id === viceCaptainId}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="mb-1 block text-xs text-slate-400">Yedek Kaptan</span>
          <select
            value={viceCaptainId ?? ""}
            onChange={(e) => setViceCaptainId(e.target.value || undefined)}
            disabled={locked}
            className="w-full rounded-md border border-slate-700 bg-slate-800 px-2 py-2 text-sm"
          >
            <option value="">Seç…</option>
            {captainOptions.map((p) => (
              <option key={p.transfermarkt_id} value={p.transfermarkt_id} disabled={p.transfermarkt_id === captainId}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}
      {!locked && (
        <button
          onClick={save}
          disabled={!validation.ok || !captainId || !viceCaptainId || saving}
          className="w-full cursor-pointer rounded-xl bg-gradient-to-r from-lime-300 to-emerald-400 py-3 text-center text-sm font-bold text-slate-950 shadow-lg shadow-lime-500/20 transition-transform hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-30"
        >
          {saving ? "Kaydediliyor…" : saved ? "Kaydedildi ✓" : "İlk 11'i Kaydet"}
        </button>
      )}
    </div>
  );
}
