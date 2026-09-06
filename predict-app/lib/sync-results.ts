import { eq, and, isNull, inArray } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions, users } from "@/db/schema";
import { getAllMatches, parseKickoff } from "./metric11-data";
import { computePoints, computeStreakBonus, parseActualScore } from "./scoring";
import { syncBadges } from "./badges";

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

  const finished = unscored
    .map((pred) => ({ pred, match: matchById.get(pred.matchId) }))
    .filter(
      (x): x is { pred: (typeof unscored)[number]; match: NonNullable<(typeof x)["match"]> } =>
        Boolean(x.match?.is_played && x.match.actual_score)
    );
  if (finished.length === 0) return { scored: 0 };

  // Seri bonusu maç kickoff sırasına bağlı olduğundan (bkz. lib/scoring.ts), toplu
  // senkronizasyonda bile kullanıcı başına kronolojik sırayla işlenmesi gerekir —
  // aksi halde ileri tarihli bir maç geriye dönük bir seriyi yanlış etkiler.
  finished.sort((a, b) => parseKickoff(a.match.date_time).getTime() - parseKickoff(b.match.date_time).getTime());

  const userIds = [...new Set(finished.map((x) => x.pred.userId))];
  const userRows = await db.select().from(users).where(inArray(users.id, userIds));
  const streakByUser = new Map(userRows.map((u) => [u.id, u.currentStreak]));
  const bestByUser = new Map(userRows.map((u) => [u.id, u.bestStreak]));

  let scored = 0;
  for (const { pred, match } of finished) {
    const actual = parseActualScore(match.actual_score!);
    if (!actual) continue;
    const points = computePoints(pred.predictedHome, pred.predictedAway, actual.home, actual.away);

    const prevStreak = streakByUser.get(pred.userId) ?? 0;
    const streak = points > 0 ? prevStreak + 1 : 0;
    streakByUser.set(pred.userId, streak);
    bestByUser.set(pred.userId, Math.max(bestByUser.get(pred.userId) ?? 0, streak));
    const streakBonus = computeStreakBonus(streak);

    await db
      .update(predictions)
      .set({ pointsEarned: points, streakBonus })
      .where(and(eq(predictions.id, pred.id)));
    scored += 1;
  }

  for (const userId of userIds) {
    await db
      .update(users)
      .set({ currentStreak: streakByUser.get(userId) ?? 0, bestStreak: bestByUser.get(userId) ?? 0 })
      .where(eq(users.id, userId));
  }

  if (scored > 0) await syncBadges();
  return { scored };
}
