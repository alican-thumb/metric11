import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions, users } from "@/db/schema";
import { getAllMatches, isLocked, parseKickoff } from "@/lib/metric11-data";
import { getOrCreateUser } from "@/lib/get-or-create-user";

export default async function CommunityPredictionsPage() {
  const [matches, viewer] = await Promise.all([getAllMatches(), getOrCreateUser()]);

  const db = getDb();
  const rows = await db
    .select({
      matchId: predictions.matchId,
      userId: predictions.userId,
      displayName: users.displayName,
      predictedHome: predictions.predictedHome,
      predictedAway: predictions.predictedAway,
      pointsEarned: predictions.pointsEarned,
    })
    .from(predictions)
    .innerJoin(users, eq(users.id, predictions.userId));

  const byMatch = new Map<string, typeof rows>();
  for (const r of rows) {
    if (!byMatch.has(r.matchId)) byMatch.set(r.matchId, []);
    byMatch.get(r.matchId)!.push(r);
  }

  const viewerPredictedMatchIds = new Set(
    viewer ? rows.filter((r) => r.userId === viewer.id).map((r) => r.matchId) : []
  );

  const matchById = new Map(matches.map((m) => [m.match_id, m]));
  const relevant = [...byMatch.keys()]
    .map((matchId) => matchById.get(matchId))
    .filter((m): m is NonNullable<typeof m> => Boolean(m))
    .sort((a, b) => parseKickoff(b.date_time).getTime() - parseKickoff(a.date_time).getTime());

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Herkesin Tahminleri</h1>
      <p className="text-sm text-slate-400">
        Kilitlenmemiş (henüz başlamamış) maçlarda başkalarının tahminini görebilmek için
        önce kendi tahminini girmelisin — bu, kopya çekmeyi engeller. Maç başladıktan
        sonra herkese açılır.
      </p>
      <div className="space-y-3">
        {relevant.map((m) => {
          const picks = byMatch.get(m.match_id)!;
          const revealed = isLocked(m) || viewerPredictedMatchIds.has(m.match_id);
          return (
            <div key={m.match_id} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-semibold">
                  {m.home_team} - {m.away_team}
                </span>
                {m.actual_score && <span className="text-slate-400">Gerçek: {m.actual_score}</span>}
              </div>
              {revealed ? (
                <ul className="space-y-1 text-sm">
                  {picks.map((p) => (
                    <li key={p.userId} className="flex items-center justify-between text-slate-300">
                      <span>{p.displayName}</span>
                      <span className="flex items-center gap-2">
                        <span>
                          {p.predictedHome}-{p.predictedAway}
                        </span>
                        {p.pointsEarned !== null && (
                          <span className="rounded bg-lime-300/20 text-lime-300 px-1.5 py-0.5 text-xs font-semibold">
                            +{p.pointsEarned}
                          </span>
                        )}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500">
                  {picks.length} kişi tahmin girdi — görmek için önce sen tahmin gir.
                </p>
              )}
            </div>
          );
        })}
        {relevant.length === 0 && <p className="text-slate-400">Henüz kimse tahmin girmedi.</p>}
      </div>
    </div>
  );
}
