import Link from "next/link";
import { redirect } from "next/navigation";
import { auth } from "@clerk/nextjs/server";
import { eq, and } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads, fantasySquadPlayers, fantasyGameweekLineups } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayersById } from "@/lib/fantasy-data";
import { getCurrentFantasyGameweek } from "@/lib/fantasy-week";
import { LineupPicker } from "@/components/fantasy/lineup-picker";

export default async function LineupPage() {
  const { userId } = await auth();
  if (!userId) redirect("/kadro");

  const user = await getOrCreateUser();
  const db = getDb();
  const [squad] = user
    ? await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1)
    : [];
  if (!squad) redirect("/kadro/kur");

  const [squadPlayerRows, gameweek] = await Promise.all([
    db.select().from(fantasySquadPlayers).where(eq(fantasySquadPlayers.squadId, squad.id)),
    getCurrentFantasyGameweek(),
  ]);

  const playersById = await getPlayersById();
  const squadPlayers = squadPlayerRows
    .map((sp) => playersById.get(sp.transfermarktId))
    .filter((p): p is NonNullable<typeof p> => Boolean(p));

  let lineupRows = gameweek.week
    ? await db
        .select()
        .from(fantasyGameweekLineups)
        .where(and(eq(fantasyGameweekLineups.squadId, squad.id), eq(fantasyGameweekLineups.week, gameweek.week)))
    : [];
  if (lineupRows.length === 0) {
    const allRows = await db.select().from(fantasyGameweekLineups).where(eq(fantasyGameweekLineups.squadId, squad.id));
    if (allRows.length > 0) {
      const lastWeek = Math.max(...allRows.map((r) => r.week));
      lineupRows = allRows.filter((r) => r.week === lastWeek);
    }
  }

  const deadlineLabel = gameweek.deadline
    ? new Intl.DateTimeFormat("tr-TR", {
        timeZone: "Europe/Istanbul",
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      }).format(gameweek.deadline)
    : null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">İlk 11&apos;ini Seç</h1>
        <Link href="/kadro/transfer" className="text-sm text-lime-300 hover:underline">
          Transfer yap →
        </Link>
      </div>
      <p className="text-sm text-slate-400">15 kişilik kadrondan ilk 11&apos;ini ve kaptanını seç. Kaptan aldığı puanı 2 katına çıkarır.</p>
      <LineupPicker
        squadPlayers={squadPlayers}
        initialLineup={lineupRows.map((r) => ({
          transfermarktId: r.transfermarktId,
          isStarting: r.isStarting,
          isCaptain: r.isCaptain,
          isViceCaptain: r.isViceCaptain,
        }))}
        week={gameweek.week}
        deadlineLabel={deadlineLabel}
        locked={gameweek.locked}
      />
    </div>
  );
}
