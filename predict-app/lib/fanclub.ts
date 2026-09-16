import { getDb } from "@/db";
import { fanPicks } from "@/db/schema";
import { getSuperLigTeams } from "@/lib/fantasy-data";
import { getRankedLeaderboard } from "@/lib/leaderboard";

export type Amigo = { displayName: string; totalPoints: number; link: string | null } | null;
export type FanClubStanding = { team: string; count: number; percentage: number; amigo: Amigo };

// "Amigo": memleket.lol'daki parasal "Ağa" sisteminin YERİNE — o takımı seçenler arasında
// SİTE LEADERBOARD PUANI (tahmin oyunu, bkz. lib/leaderboard.ts) en yüksek kişi. Para yerine
// performans bahis konusu; dinamik — biri daha çok/iyi oynayarak Amigo'yu geçebilir.
export async function getFanClubStandings(userId?: number): Promise<{
  teams: FanClubStanding[];
  totalVotes: number;
  myTeam: string | null;
  myLink: string | null;
}> {
  const db = getDb();
  const [teams, picks, leaderboard] = await Promise.all([
    getSuperLigTeams(),
    db.select().from(fanPicks),
    getRankedLeaderboard(),
  ]);

  const pointsByUserId = new Map(leaderboard.map((r) => [r.userId, r]));
  const picksByTeam = new Map<string, typeof picks>();
  for (const pick of picks) {
    const list = picksByTeam.get(pick.team) ?? [];
    list.push(pick);
    picksByTeam.set(pick.team, list);
  }

  const totalVotes = picks.length;

  const rows = teams
    .map((team) => {
      const teamPicks = picksByTeam.get(team) ?? [];
      const count = teamPicks.length;
      let amigo: Amigo = null;
      let bestPoints = -1;
      for (const pick of teamPicks) {
        const row = pointsByUserId.get(pick.userId);
        const points = row?.totalPoints ?? 0;
        if (points > bestPoints) {
          bestPoints = points;
          amigo = { displayName: row?.displayName ?? "Bilinmeyen", totalPoints: points, link: pick.link };
        }
      }
      return { team, count, percentage: totalVotes > 0 ? count / totalVotes : 0, amigo };
    })
    .sort((a, b) => b.count - a.count);

  let myTeam: string | null = null;
  let myLink: string | null = null;
  if (userId) {
    const mine = picks.find((p) => p.userId === userId);
    myTeam = mine?.team ?? null;
    myLink = mine?.link ?? null;
  }

  return { teams: rows, totalVotes, myTeam, myLink };
}
