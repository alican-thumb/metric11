import { getUpcomingMatches, getCurrentWeekMatchIds, parseKickoff } from "./metric11-data";

export type FantasyGameweek = { week: number | null; deadline: Date | null; locked: boolean };

// Kadro Kur haftaları, tahmin oyunuyla AYNI TFF hafta numaralandırmasını kullanır — "bu
// haftanın maçları" ile aynı tanım (bkz. metric11-data.ts::getUpcomingMatches):
// deadline = haftanın ilk maçının kickoff'u. O andan sonra ilk 11/transfer o hafta için
// kilitlenir.
export async function getCurrentFantasyGameweek(): Promise<FantasyGameweek> {
  const upcoming = await getUpcomingMatches();
  if (upcoming.length > 0) {
    return { week: upcoming[0].week, deadline: parseKickoff(upcoming[0].date_time), locked: false };
  }
  const { week } = await getCurrentWeekMatchIds();
  return { week, deadline: null, locked: true };
}
