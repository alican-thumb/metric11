import { NextResponse } from "next/server";
import { eq, and } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads, fantasySquadPlayers, fantasyTransferLog } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayersById } from "@/lib/fantasy-data";
import { getCurrentFantasyGameweek } from "@/lib/fantasy-week";
import { validateSquad, MAX_PER_TEAM } from "@/lib/fantasy-rules";

export async function POST(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const body = await req.json().catch(() => null);
  const playerOutId = body?.playerOutId as string | undefined;
  const playerInId = body?.playerInId as string | undefined;
  if (!playerOutId || !playerInId || playerOutId === playerInId) {
    return NextResponse.json({ error: "Geçersiz transfer isteği." }, { status: 400 });
  }

  const db = getDb();
  const [squad] = await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1);
  if (!squad) return NextResponse.json({ error: "Önce kadro kurmalısın." }, { status: 404 });

  const gameweek = await getCurrentFantasyGameweek();
  if (gameweek.locked) {
    return NextResponse.json(
      { error: "Bu hafta maçlar başladığı için transfer kapalı — bir sonraki haftaya kadar bekle." },
      { status: 409 }
    );
  }

  const squadPlayers = await db
    .select()
    .from(fantasySquadPlayers)
    .where(eq(fantasySquadPlayers.squadId, squad.id));
  const currentIds = squadPlayers.map((sp) => sp.transfermarktId);
  if (!currentIds.includes(playerOutId)) {
    return NextResponse.json({ error: "Bu oyuncu kadronda değil." }, { status: 400 });
  }
  if (currentIds.includes(playerInId)) {
    return NextResponse.json({ error: "Bu oyuncu zaten kadronda." }, { status: 400 });
  }

  const playersById = await getPlayersById();
  const playerOut = playersById.get(playerOutId);
  const playerIn = playersById.get(playerInId);
  if (!playerOut || !playerIn) {
    return NextResponse.json({ error: "Oyuncu bulunamadı." }, { status: 400 });
  }
  if (playerOut.position_group !== playerIn.position_group) {
    return NextResponse.json(
      { error: `Transfer aynı pozisyonda olmalı (${playerOut.position_group} yerine ${playerIn.position_group} olamaz).` },
      { status: 400 }
    );
  }

  const newIds = currentIds.map((id) => (id === playerOutId ? playerInId : id));
  const newPlayers = newIds.map((id) => playersById.get(id)!);
  const teamCount = newPlayers.filter((p) => p.team === playerIn.team).length;
  if (teamCount > MAX_PER_TEAM) {
    return NextResponse.json({ error: `${playerIn.team}'dan en fazla ${MAX_PER_TEAM} oyuncu olabilir.` }, { status: 400 });
  }
  const validation = validateSquad(newPlayers);
  if (!validation.ok) {
    return NextResponse.json({ error: validation.error }, { status: 400 });
  }

  // Haftalık ücretsiz transfer sayacı: yeni hafta algılanınca 1'e sıfırlanır (biriktirme yok — MVP).
  let freeTransfers = squad.freeTransfers;
  if (squad.transfersWeek !== gameweek.week) {
    freeTransfers = 1;
  }
  const penalized = freeTransfers <= 0;
  const nextFreeTransfers = penalized ? 0 : freeTransfers - 1;

  await db
    .update(fantasySquadPlayers)
    .set({ transfermarktId: playerInId })
    .where(and(eq(fantasySquadPlayers.squadId, squad.id), eq(fantasySquadPlayers.transfermarktId, playerOutId)));

  await db
    .update(fantasySquads)
    .set({ freeTransfers: nextFreeTransfers, transfersWeek: gameweek.week, updatedAt: new Date() })
    .where(eq(fantasySquads.id, squad.id));

  await db.insert(fantasyTransferLog).values({
    squadId: squad.id,
    week: gameweek.week ?? 0,
    playerOutId,
    playerInId,
    penalized,
  });

  return NextResponse.json({ ok: true, penalized, freeTransfersRemaining: nextFreeTransfers });
}
