"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function DisplayNameForm({ initialName }: { initialName: string }) {
  const router = useRouter();
  const [name, setName] = useState(initialName);
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function submit() {
    setStatus("saving");
    setErrorMsg("");
    try {
      const res = await fetch("/api/user/display-name", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ displayName: name }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setErrorMsg(data.error ?? "Bir hata oluştu.");
        setStatus("error");
        return;
      }
      setStatus("saved");
      router.refresh();
    } catch {
      setErrorMsg("Bağlantı hatası.");
      setStatus("error");
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm text-slate-400" htmlFor="displayName">
        Kullanıcı adı
      </label>
      <div className="flex items-center gap-2">
        <input
          id="displayName"
          type="text"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setStatus("idle");
          }}
          maxLength={24}
          className="w-full max-w-xs rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm"
        />
        <button
          onClick={submit}
          disabled={status === "saving" || name.trim() === "" || name.trim() === initialName}
          className="cursor-pointer rounded-md bg-lime-300 px-3 py-1.5 text-sm font-semibold text-slate-900 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {status === "saving" ? "Kaydediliyor…" : "Kaydet"}
        </button>
      </div>
      <p className="text-xs text-slate-500">2-24 karakter — harf, rakam, boşluk, tire, alt çizgi.</p>
      {status === "saved" && <p className="text-sm text-lime-300">Kaydedildi ✓</p>}
      {status === "error" && <p className="text-sm text-red-400">{errorMsg}</p>}
    </div>
  );
}
