import { sql } from "drizzle-orm";
import { getDb } from "@/db";
import { fanPicks } from "@/db/schema";
import { getSuperLigTeams } from "@/lib/fantasy-data";

export type FanClubStanding = { team: string; count: number; percentage: number };

export async function getFanClubStandings(userId?: number): Promise<{
  teams: FanClubStanding[];
  totalVotes: number;
  myTeam: string | null;
}> {
  const db = getDb();
  const [teams, counted] = await Promise.all([
    getSuperLigTeams(),
    db
      .select({ team: fanPicks.team, count: sql<number>`count(*)`.as("count") })
      .from(fanPicks)
      .groupBy(fanPicks.team),
  ]);

  const countByTeam = new Map(counted.map((row) => [row.team, Number(row.count)]));
  const totalVotes = counted.reduce((sum, row) => sum + Number(row.count), 0);

  const rows = teams
    .map((team) => {
      const count = countByTeam.get(team) ?? 0;
      return { team, count, percentage: totalVotes > 0 ? count / totalVotes : 0 };
    })
    .sort((a, b) => b.count - a.count);

  let myTeam: string | null = null;
  if (userId) {
    const [pick] = await db.select().from(fanPicks).where(sql`${fanPicks.userId} = ${userId}`).limit(1);
    myTeam = pick?.team ?? null;
  }

  return { teams: rows, totalVotes, myTeam };
}
