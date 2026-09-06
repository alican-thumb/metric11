"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function CreateGroupForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function submit() {
    setStatus("saving");
    setErrorMsg("");
    try {
      const res = await fetch("/api/groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setErrorMsg(data.error ?? "Bir hata oluştu.");
        setStatus("error");
        return;
      }
      router.push(`/gruplar/${data.group.inviteCode}`);
    } catch {
      setErrorMsg("Bağlantı hatası.");
      setStatus("error");
    }
  }

  return (
    <div className="space-y-2">
      <input
        type="text"
        value={name}
        onChange={(e) => {
          setName(e.target.value);
          setStatus("idle");
        }}
        placeholder="Grup adı (ör. Mahalle Ligi)"
        maxLength={40}
        className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm"
      />
      <button
        onClick={submit}
        disabled={status === "saving" || name.trim().length < 2}
        className="cursor-pointer rounded-md bg-lime-300 px-3 py-1.5 text-sm font-semibold text-slate-900 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {status === "saving" ? "Kuruluyor…" : "Grubu Kur"}
      </button>
      {status === "error" && <p className="text-sm text-red-400">{errorMsg}</p>}
    </div>
  );
}
