"use client";

import { useState } from "react";

type Props = {
  matchId: string;
  homeTeam: string;
  awayTeam: string;
  dateTime: string;
  metric11Prediction: string; // ör. "2-1"
  initialHome?: number;
  initialAway?: number;
  isSignedIn: boolean;
};

export function MatchPredictionCard({
  matchId,
  homeTeam,
  awayTeam,
  dateTime,
  metric11Prediction,
  initialHome,
  initialAway,
  isSignedIn,
}: Props) {
  const [home, setHome] = useState(initialHome?.toString() ?? "");
  const [away, setAway] = useState(initialAway?.toString() ?? "");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function submit() {
    if (home === "" || away === "") return;
    setStatus("saving");
    setErrorMsg("");
    try {
      const res = await fetch("/api/predictions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ matchId, predictedHome: Number(home), predictedAway: Number(away) }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setErrorMsg(data.error ?? "Bir hata oluştu.");
        setStatus("error");
        return;
      }
      setStatus("saved");
    } catch {
      setErrorMsg("Bağlantı hatası.");
      setStatus("error");
    }
  }

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="mb-2 flex items-center justify-between text-xs text-slate-400">
        <span>{dateTime}</span>
        <span title="metric11 modelinin tahmini">metric11: {metric11Prediction}</span>
      </div>
      <div className="flex items-center justify-between gap-3">
        <span className="flex-1 text-right font-medium">{homeTeam}</span>
        {isSignedIn ? (
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={0}
              max={20}
              value={home}
              onChange={(e) => setHome(e.target.value)}
              aria-label={`${homeTeam} skoru`}
              className="w-12 rounded border border-slate-700 bg-slate-800 py-1 text-center"
            />
            <span>-</span>
            <input
              type="number"
              min={0}
              max={20}
              value={away}
              onChange={(e) => setAway(e.target.value)}
              aria-label={`${awayTeam} skoru`}
              className="w-12 rounded border border-slate-700 bg-slate-800 py-1 text-center"
            />
          </div>
        ) : (
          <span className="text-slate-500 text-sm">giriş yapınca tahmin gir</span>
        )}
        <span className="flex-1 font-medium">{awayTeam}</span>
      </div>
      {isSignedIn && (
        <div className="mt-3 flex items-center gap-3">
          <button
            onClick={submit}
            disabled={status === "saving" || home === "" || away === ""}
            className="cursor-pointer rounded-md bg-lime-300 px-3 py-1.5 text-sm font-semibold text-slate-900 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {status === "saving" ? "Kaydediliyor…" : "Tahmini Kaydet"}
          </button>
          {status === "saved" && <span className="text-sm text-lime-300">Kaydedildi ✓</span>}
          {status === "error" && <span className="text-sm text-red-400">{errorMsg}</span>}
        </div>
      )}
    </div>
  );
}
