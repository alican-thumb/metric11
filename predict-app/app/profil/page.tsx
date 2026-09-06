import { eq, desc } from "drizzle-orm";
import { getDb } from "@/db";
import { badges as badgesTable } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { BADGE_CATALOG } from "@/lib/badges";
import { DisplayNameForm } from "@/components/display-name-form";

export default async function ProfilePage() {
  const user = await getOrCreateUser();
  if (!user) {
    return <p className="text-slate-400">Bu sayfayı görmek için giriş yapmalısınız.</p>;
  }

  const db = getDb();
  const earned = await db
    .select()
    .from(badgesTable)
    .where(eq(badgesTable.userId, user.id))
    .orderBy(desc(badgesTable.earnedAt));
  const earnedCodes = new Set(earned.map((b) => b.code));

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Profil</h1>
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <DisplayNameForm initialName={user.displayName} />
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-2 text-sm font-semibold text-slate-300">Seri</h2>
        <div className="flex gap-6 text-sm">
          <div>
            <div className="text-slate-500">Güncel seri</div>
            <div className="text-lg font-semibold text-orange-300">🔥 {user.currentStreak}</div>
          </div>
          <div>
            <div className="text-slate-500">En iyi seri</div>
            <div className="text-lg font-semibold text-orange-300">🔥 {user.bestStreak}</div>
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-300">Rozetler</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {BADGE_CATALOG.map((b) => {
            const isEarned = earnedCodes.has(b.code);
            return (
              <div
                key={b.code}
                className={`rounded-lg border p-3 text-center ${
                  isEarned ? "border-lime-300/40 bg-lime-300/10" : "border-slate-800 bg-slate-950 opacity-40"
                }`}
                title={b.description}
              >
                <div className="text-2xl">{b.icon}</div>
                <div className="mt-1 text-xs font-semibold">{b.label}</div>
              </div>
            );
          })}
        </div>
        {earned.length === 0 && (
          <p className="mt-3 text-sm text-slate-500">Henüz rozet kazanmadın — tahmin yapmaya devam et.</p>
        )}
      </div>
    </div>
  );
}
