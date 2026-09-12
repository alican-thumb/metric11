import { eq, and, isNull } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasyGameweekLineups } from "@/db/schema";
import { getGameweekPlayerPoints } from "./fantasy-data";

// Idempotent, tahmin oyunundaki sync-results.ts ile aynı desen: hem cron'dan hem de
// sayfa yüklerinden fırsatçı çağrılabilir. Yedek oyuncular (isStarting=false) hep 0
// puan alır (oyuna girip girmediği veri kaynağında yok — bkz. build_fantasy_gameweek_scores.py);
// ilk 11'dekiler için puan, o oyuncunun maçı işlenene kadar NULL kalır.
export async function syncFantasyResults(): Promise<{ scored: number }> {
  const db = getDb();
  const pending = await db
    .select()
    .from(fantasyGameweekLineups)
    .where(isNull(fantasyGameweekLineups.points));

  if (pending.length === 0) return { scored: 0 };

  let scored = 0;

  const benchRows = pending.filter((r) => !r.isStarting);
  for (const row of benchRows) {
    await db.update(fantasyGameweekLineups).set({ points: 0 }).where(eq(fantasyGameweekLineups.id, row.id));
    scored += 1;
  }

  const starterRows = pending.filter((r) => r.isStarting);
  const weeks = [...new Set(starterRows.map((r) => r.week))];
  for (const week of weeks) {
    const pointsByPlayer = await getGameweekPlayerPoints(week);
    if (pointsByPlayer.size === 0) continue;
    for (const row of starterRows.filter((r) => r.week === week)) {
      const points = pointsByPlayer.get(row.transfermarktId);
      if (points === undefined) continue; // bu oyuncunun maçı henüz işlenmedi
      await db
        .update(fantasyGameweekLineups)
        .set({ points })
        .where(and(eq(fantasyGameweekLineups.id, row.id)));
      scored += 1;
    }
  }

  return { scored };
}
