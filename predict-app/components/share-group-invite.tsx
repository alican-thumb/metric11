"use client";

import { useState } from "react";

export function ShareGroupInvite({ groupName, code }: { groupName: string; code: string }) {
  const [copied, setCopied] = useState(false);
  const url = `https://tahmin.metric11.com/gruplar/${code}`;
  const message = `${groupName} grubuna katıl! metric11'de Süper Lig maçlarına skor tahmini gir, aramızda yarışalım 🎮⚽ Davet kodu: ${code}\n${url}`;

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard API unavailable — WhatsApp/native share still work
    }
  }

  async function nativeShare() {
    if (typeof navigator !== "undefined" && navigator.share) {
      try {
        await navigator.share({ title: groupName, text: message, url });
      } catch {
        // user cancelled the share sheet
      }
    } else {
      copyLink();
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        onClick={nativeShare}
        className="cursor-pointer rounded-md bg-lime-300 px-3 py-1.5 text-sm font-semibold text-slate-900"
      >
        📤 Arkadaşını davet et
      </button>
      <a
        href={`https://wa.me/?text=${encodeURIComponent(message)}`}
        target="_blank"
        rel="noopener noreferrer"
        className="rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm font-semibold text-slate-200 hover:border-lime-300/40"
      >
        WhatsApp&apos;ta paylaş
      </a>
      <button
        onClick={copyLink}
        className="cursor-pointer rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm font-semibold text-slate-200 hover:border-lime-300/40"
      >
        {copied ? "Kopyalandı ✓" : "Linki kopyala"}
      </button>
    </div>
  );
}
