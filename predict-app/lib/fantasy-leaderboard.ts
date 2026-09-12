import { sql, eq, inArray } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasyGameweekLineups, fantasySquads, fantasyTransferLog, users } from "@/db/schema";

export type FantasyRankedRow = {
  userId: number;
  displayName: string;
  totalPoints: number;
  gameweeksPlayed: number;
  rank: number;
};

const TRANSFER_PENALTY = 4;

// Kaptan çarpanı (2x) ve transfer cezası (-4/fazla transfer) burada, tek yerde
// uygulanır — ham puanlar hiç değiştirilmez (bkz. lib/scoring.ts'deki aynı ilke).
// İki toplama AYRI sorgularla yapılır: fantasyGameweekLineups ve fantasyTransferLog
// ikisi de fantasySquads'a one-to-many olduğu için tek sorguda join etmek satırları
// çarpıp puan toplamını yanlış şişirir.
export async function getFantasyLeaderboard(opts?: { userIds?: number[] }): Promise<FantasyRankedRow[]> {
  const db = getDb();

  let pointsQuery = db
    .select({
      userId: users.id,
      displayName: users.displayName,
      totalPoints: sql<number>`coalesce(sum(case when ${fantasyGameweekLineups.isCaptain} then ${fantasyGameweekLineups.points} * 2 else ${fantasyGameweekLineups.points} end), 0)`.as(
        "total_points"
      ),
      gameweeksPlayed: sql<number>`count(distinct case when ${fantasyGameweekLineups.points} is not null then ${fantasyGameweekLineups.week} end)`.as(
        "gameweeks_played"
      ),
    })
    .from(users)
    .innerJoin(fantasySquads, eq(fantasySquads.userId, users.id))
    .leftJoin(fantasyGameweekLineups, eq(fantasyGameweekLineups.squadId, fantasySquads.id))
    .$dynamic();
  if (opts?.userIds) pointsQuery = pointsQuery.where(inArray(users.id, opts.userIds));
  const pointsRows = await pointsQuery.groupBy(users.id, users.displayName);

  let penaltyQuery = db
    .select({
      userId: users.id,
      penaltyCount: sql<number>`coalesce(sum(case when ${fantasyTransferLog.penalized} then 1 else 0 end), 0)`.as(
        "penalty_count"
      ),
    })
    .from(users)
    .innerJoin(fantasySquads, eq(fantasySquads.userId, users.id))
    .leftJoin(fantasyTransferLog, eq(fantasyTransferLog.squadId, fantasySquads.id))
    .$dynamic();
  if (opts?.userIds) penaltyQuery = penaltyQuery.where(inArray(users.id, opts.userIds));
  const penaltyRows = await penaltyQuery.groupBy(users.id);
  const penaltyByUser = new Map(penaltyRows.map((r) => [r.userId, r.penaltyCount]));

  const merged = pointsRows.map((r) => ({
    userId: r.userId,
    displayName: r.displayName,
    totalPoints: r.totalPoints - (penaltyByUser.get(r.userId) ?? 0) * TRANSFER_PENALTY,
    gameweeksPlayed: r.gameweeksPlayed,
  }));

  merged.sort((a, b) => b.totalPoints - a.totalPoints);
  return merged.map((r, i) => ({ ...r, rank: i + 1 }));
}
