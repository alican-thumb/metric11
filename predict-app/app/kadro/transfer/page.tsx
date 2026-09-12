import { redirect } from "next/navigation";
import { auth } from "@clerk/nextjs/server";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads, fantasySquadPlayers } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayerPool, getPlayersById } from "@/lib/fantasy-data";
import { getCurrentFantasyGameweek } from "@/lib/fantasy-week";
import { TransferPanel } from "@/components/fantasy/transfer-panel";

export default async function TransferPage() {
  const { userId } = await auth();
  if (!userId) redirect("/kadro");

  const user = await getOrCreateUser();
  const db = getDb();
  const [squad] = user
    ? await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1)
    : [];
  if (!squad) redirect("/kadro/kur");

  const [squadPlayerRows, pool, gameweek] = await Promise.all([
    db.select().from(fantasySquadPlayers).where(eq(fantasySquadPlayers.squadId, squad.id)),
    getPlayerPool(),
    getCurrentFantasyGameweek(),
  ]);

  const playersById = await getPlayersById();
  const squadPlayers = squadPlayerRows
    .map((sp) => playersById.get(sp.transfermarktId))
    .filter((p): p is NonNullable<typeof p> => Boolean(p));

  const freeTransfers = squad.transfersWeek === gameweek.week ? squad.freeTransfers : 1;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Transfer</h1>
      <p className="text-sm text-slate-400">
        Haftada 1 ücretsiz transfer hakkın var, fazlası -4 puana mal olur. Transfer aynı pozisyonda olmalı.
      </p>
      <TransferPanel squadPlayers={squadPlayers} allPlayers={pool.players} freeTransfers={freeTransfers} locked={gameweek.locked} />
    </div>
  );
}
