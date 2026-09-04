import { eq, and, isNull } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions } from "@/db/schema";
import { getAllMatches } from "./metric11-data";
import { computePoints, parseActualScore } from "./scoring";

// Idempotent: hem Vercel Cron'dan (app/api/cron/sync-results) hem de sayfa yüklerinden
// (leaderboard/predictions) fırsatçı şekilde çağrılabilir. Cron ne sıklıkta çalışırsa
// çalışsın (plan tipine göre değişebilir), doğruluk buna bağımlı kalmaz — bir kullanıcı
// sayfayı her açtığında da henüz puanlanmamış biten maçlar yakalanır.
export async function syncFinishedResults(): Promise<{ scored: number }> {
  const db = getDb();
  const unscored = await db
    .select()
    .from(predictions)
    .where(isNull(predictions.pointsEarned));

  if (unscored.length === 0) return { scored: 0 };

  const matches = await getAllMatches();
  const matchById = new Map(matches.map((m) => [m.match_id, m]));

  let scored = 0;
  for (const pred of unscored) {
    const match = matchById.get(pred.matchId);
    if (!match || !match.is_played || !match.actual_score) continue;
    const actual = parseActualScore(match.actual_score);
    if (!actual) continue;
    const points = computePoints(pred.predictedHome, pred.predictedAway, actual.home, actual.away);
    await db
      .update(predictions)
      .set({ pointsEarned: points })
      .where(and(eq(predictions.id, pred.id)));
    scored += 1;
  }
  return { scored };
}
