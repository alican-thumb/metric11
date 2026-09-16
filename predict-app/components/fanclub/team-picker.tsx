"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SignInButton } from "@clerk/nextjs";

export function TeamPicker({
  teams,
  myTeam,
  myLink,
  signedIn,
}: {
  teams: string[];
  myTeam: string | null;
  myLink: string | null;
  signedIn: boolean;
}) {
  const router = useRouter();
  const [picking, setPicking] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(myTeam);
  const [link, setLink] = useState(myLink ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function save() {
    if (!selectedTeam) return;
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/fanclub", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ team: selectedTeam, link }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error ?? "Kaydedilemedi.");
        setSaving(false);
        return;
      }
      setPicking(false);
      setSaving(false);
      router.refresh();
    } catch {
      setError("Bağlantı hatası.");
      setSaving(false);
    }
  }

  if (!signedIn) {
    return (
      <div className="rounded-xl border border-lime-300/20 bg-lime-300/5 p-4 text-center text-sm">
        <p className="mb-3 text-slate-300">Takımını seçip Amigo Ligi&apos;ne dahil olmak için giriş yap.</p>
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
          Takımını/linkini değiştir
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <p className="text-center text-sm text-slate-300">Taraftarı olduğun takımı seç:</p>
      {error && <p className="text-center text-sm text-red-400">{error}</p>}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {teams.map((team) => (
          <button
            key={team}
            onClick={() => setSelectedTeam(team)}
            className={`rounded-lg border px-2 py-2 text-xs font-medium transition-colors ${
              team === selectedTeam
                ? "border-lime-300 bg-lime-300/10 text-lime-300"
                : "border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-600"
            }`}
          >
            {team}
          </button>
        ))}
      </div>
      {selectedTeam && (
        <div className="space-y-1.5 border-t border-slate-800 pt-3">
          <label className="block text-xs text-slate-400">
            🔥 Amigo olursan görünecek link (opsiyonel — sosyal medyan, kanalın vb.)
          </label>
          <input
            value={link}
            onChange={(e) => setLink(e.target.value)}
            placeholder="https://..."
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs text-slate-200 placeholder:text-slate-600"
          />
          <div className="flex items-center justify-between pt-1">
            {myTeam && (
              <button
                onClick={() => setPicking(false)}
                disabled={saving}
                className="text-xs font-semibold text-slate-500 underline decoration-dotted underline-offset-4 hover:text-slate-300"
              >
                Vazgeç
              </button>
            )}
            <button
              onClick={save}
              disabled={saving}
              className="ml-auto rounded-lg bg-gradient-to-r from-lime-300 to-emerald-400 px-4 py-1.5 text-xs font-bold text-slate-950 transition-transform hover:scale-105 disabled:opacity-40"
            >
              {saving ? "Kaydediliyor…" : "Kaydet"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
