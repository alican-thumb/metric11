import { sql, eq, and, inArray } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions, users } from "@/db/schema";

export type RankedRow = {
  userId: number;
  displayName: string;
  totalPoints: number;
  predictionCount: number;
  rank: number;
};

// Genel, haftalık ve grup lider tabloları aynı toplama mantığını paylaşır — tek fark
// hangi kullanıcı kümesine ve hangi maçlara bakıldığı. `matchIds` verilirse yalnızca o
// maçlara ait tahminler sayılır (haftalık lig); `userIds` verilirse yalnızca o
// kullanıcılar listelenir (grup lig).
export async function getRankedLeaderboard(opts?: {
  matchIds?: string[];
  userIds?: number[];
}): Promise<RankedRow[]> {
  const db = getDb();

  const joinCondition = opts?.matchIds
    ? and(eq(predictions.userId, users.id), inArray(predictions.matchId, opts.matchIds))
    : eq(predictions.userId, users.id);

  let query = db
    .select({
      userId: users.id,
      displayName: users.displayName,
      totalPoints: sql<number>`coalesce(sum(${predictions.pointsEarned} + ${predictions.streakBonus}), 0)`.as(
        "total_points"
      ),
      predictionCount: sql<number>`count(${predictions.id})`.as("prediction_count"),
    })
    .from(users)
    .leftJoin(predictions, joinCondition)
    .$dynamic();

  if (opts?.userIds) {
    query = query.where(inArray(users.id, opts.userIds));
  }

  const rows = await query.groupBy(users.id, users.displayName).orderBy(sql`total_points desc`);
  return rows.map((r, i) => ({ ...r, rank: i + 1 }));
}
