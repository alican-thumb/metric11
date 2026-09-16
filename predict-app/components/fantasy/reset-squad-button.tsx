"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function ResetSquadButton({ className }: { className?: string }) {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function resetSquad() {
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/fantasy/squad", { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error ?? "Kadro silinemedi.");
        setSaving(false);
        return;
      }
      router.refresh();
    } catch {
      setError("Bağlantı hatası.");
      setSaving(false);
    }
  }

  if (confirming) {
    return (
      <div className={`space-y-2 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm ${className ?? ""}`}>
        <p className="text-red-300">
          Emin misin? Kadron, transfer geçmişin ve bu sezonki tüm hafta puanların kalıcı olarak silinir.
        </p>
        {error && <p className="text-red-400">{error}</p>}
        <div className="flex gap-2">
          <button
            onClick={resetSquad}
            disabled={saving}
            className="rounded-lg bg-red-500 px-3 py-1.5 text-xs font-bold text-white transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            {saving ? "Siliniyor…" : "Evet, sıfırla"}
          </button>
          <button
            onClick={() => setConfirming(false)}
            disabled={saving}
            className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:border-slate-500"
          >
            Vazgeç
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={() => setConfirming(true)}
      className={`text-xs font-semibold text-red-400 underline decoration-dotted underline-offset-4 hover:text-red-300 ${className ?? ""}`}
    >
      Kadromu Sıfırla ve Yeniden Kur
    </button>
  );
}
