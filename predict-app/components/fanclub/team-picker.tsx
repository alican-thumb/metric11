"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SignInButton } from "@clerk/nextjs";

export function TeamPicker({
  teams,
  myTeam,
  signedIn,
}: {
  teams: string[];
  myTeam: string | null;
  signedIn: boolean;
}) {
  const router = useRouter();
  const [picking, setPicking] = useState(false);
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function pick(team: string) {
    setSaving(team);
    setError(null);
    try {
      const res = await fetch("/api/fanclub", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ team }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error ?? "Kaydedilemedi.");
        setSaving(null);
        return;
      }
      setPicking(false);
      setSaving(null);
      router.refresh();
    } catch {
      setError("Bağlantı hatası.");
      setSaving(null);
    }
  }

  if (!signedIn) {
    return (
      <div className="rounded-xl border border-lime-300/20 bg-lime-300/5 p-4 text-center text-sm">
        <p className="mb-3 text-slate-300">Takımını seçip taraftar sayacına dahil olmak için giriş yap.</p>
        <SignInButton mode="modal">
          <button className="rounded-xl bg-gradient-to-r from-lime-300 to-emerald-400 px-5 py-2 text-sm font-bold text-slate-950 hover:scale-105 transition-transform">
            Giriş Yap
          </button>
        </SignInButton>
      </div>
    );
  }

  if (!picking && myTeam) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-center text-sm">
        <p className="text-slate-300">
          Taraftarı olduğun takım: <span className="font-bold text-lime-300">{myTeam}</span>
        </p>
        <button
          onClick={() => setPicking(true)}
          className="text-xs font-semibold text-slate-500 underline decoration-dotted underline-offset-4 hover:text-slate-300"
        >
          Takımını Değiştir
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <p className="text-center text-sm text-slate-300">Taraftarı olduğun takımı seç:</p>
      {error && <p className="text-center text-sm text-red-400">{error}</p>}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {teams.map((team) => (
          <button
            key={team}
            onClick={() => pick(team)}
            disabled={saving !== null}
            className={`rounded-lg border px-2 py-2 text-xs font-medium transition-colors disabled:opacity-40 ${
              team === myTeam
                ? "border-lime-300 bg-lime-300/10 text-lime-300"
                : "border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-600"
            }`}
          >
            {saving === team ? "Kaydediliyor…" : team}
          </button>
        ))}
      </div>
      {myTeam && (
        <div className="text-center">
          <button
            onClick={() => setPicking(false)}
            className="text-xs font-semibold text-slate-500 underline decoration-dotted underline-offset-4 hover:text-slate-300"
          >
            Vazgeç
          </button>
        </div>
      )}
    </div>
  );
}
