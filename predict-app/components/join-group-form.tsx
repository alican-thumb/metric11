"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function JoinGroupForm({ defaultCode = "" }: { defaultCode?: string }) {
  const router = useRouter();
  const [code, setCode] = useState(defaultCode);
  const [status, setStatus] = useState<"idle" | "saving" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function submit() {
    setStatus("saving");
    setErrorMsg("");
    try {
      const res = await fetch("/api/groups/join", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setErrorMsg(data.error ?? "Bir hata oluştu.");
        setStatus("error");
        return;
      }
      router.push(`/gruplar/${data.group.inviteCode}`);
      router.refresh();
    } catch {
      setErrorMsg("Bağlantı hatası.");
      setStatus("error");
    }
  }

  return (
    <div className="space-y-2">
      <input
        type="text"
        value={code}
        onChange={(e) => {
          setCode(e.target.value.toUpperCase());
          setStatus("idle");
        }}
        placeholder="Davet kodu"
        maxLength={6}
        className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm font-mono uppercase"
      />
      <button
        onClick={submit}
        disabled={status === "saving" || code.trim().length < 4}
        className="cursor-pointer rounded-md bg-lime-300 px-3 py-1.5 text-sm font-semibold text-slate-900 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {status === "saving" ? "Katılıyor…" : "Katıl"}
      </button>
      {status === "error" && <p className="text-sm text-red-400">{errorMsg}</p>}
    </div>
  );
}
