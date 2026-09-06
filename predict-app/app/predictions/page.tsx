import { eq, desc } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getAllMatches } from "@/lib/metric11-data";
import { syncFinishedResults } from "@/lib/sync-results";

export default async function PredictionsPage() {
  // Sayfa her açıldığında fırsatçı senkronizasyon — cron'un ne sıklıkla çalıştığından
  // bağımsız olarak, biten ama henüz puanlanmamış maçlar burada da yakalanır. Kullanıcıyı
  // bundan SONRA okuyoruz ki currentStreak/bestStreak güncel değerlerini yansıtsın.
  await syncFinishedResults();

  const user = await getOrCreateUser();
  if (!user) {
    return <p className="text-slate-400">Bu sayfayı görmek için giriş yapmalısınız.</p>;
  }

  const db = getDb();
  const rows = await db
    .select()
    .from(predictions)
    .where(eq(predictions.userId, user.id))
    .orderBy(desc(predictions.submittedAt));

  const matches = await getAllMatches();
  const matchById = new Map(matches.map((m) => [m.match_id, m]));

  const totalPoints = rows.reduce((sum, r) => sum + (r.pointsEarned ?? 0) + r.streakBonus, 0);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Tahminlerim</h1>
      <p className="text-sm text-slate-400">
        Toplam puan: <span className="text-lime-300 font-semibold">{totalPoints}</span>
        {user.currentStreak > 0 && (
          <span className="ml-3 text-orange-300">
            🔥 {user.currentStreak} maçlık seri {user.currentStreak >= 3 ? "(bonus aktif)" : ""}
          </span>
        )}
      </p>
      <div className="space-y-2">
        {rows.map((r) => {
          const match = matchById.get(r.matchId);
          return (
            <div key={r.id} className="rounded-lg border border-slate-800 bg-slate-900 p-3 flex items-center justify-between text-sm">
              <span>
                {match ? `${match.home_team} - ${match.away_team}` : r.matchId}
                <span className="text-slate-500 ml-2">
                  ({r.predictedHome}-{r.predictedAway})
                </span>
              </span>
              <span className="flex items-center gap-3">
                {match?.actual_score && <span className="text-slate-400">Gerçek: {match.actual_score}</span>}
                {r.pointsEarned !== null ? (
                  <span className="rounded bg-lime-300/20 text-lime-300 px-2 py-0.5 font-semibold">
                    +{r.pointsEarned + r.streakBonus} puan
                    {r.streakBonus > 0 && <span className="ml-1 text-orange-300">🔥+{r.streakBonus}</span>}
                  </span>
                ) : (
                  <span className="text-slate-500">bekliyor</span>
                )}
              </span>
            </div>
          );
        })}
        {rows.length === 0 && <p className="text-slate-400">Henüz tahmin girmediniz.</p>}
      </div>
    </div>
  );
}
