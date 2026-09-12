import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads, fantasySquadPlayers } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayersById } from "@/lib/fantasy-data";
import { validateSquad, squadCost, BUDGET } from "@/lib/fantasy-rules";

export async function GET() {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const db = getDb();
  const [squad] = await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1);
  if (!squad) return NextResponse.json({ squad: null });

  const squadPlayers = await db
    .select()
    .from(fantasySquadPlayers)
    .where(eq(fantasySquadPlayers.squadId, squad.id));

  const playersById = await getPlayersById();
  const players = squadPlayers
    .map((sp) => playersById.get(sp.transfermarktId))
    .filter((p): p is NonNullable<typeof p> => Boolean(p));

  return NextResponse.json({
    squad: { id: squad.id, freeTransfers: squad.freeTransfers },
    players,
    budgetUsed: squadCost(players),
    budget: BUDGET,
  });
}

// Yalnızca İLK kadro kurma — sonrasında değişiklikler /api/fantasy/transfer üzerinden yapılır
// (böylece ücretsiz transfer/ceza mantığı tek bir yerde uygulanır).
export async function POST(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const db = getDb();
  const [existing] = await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1);
  if (existing) {
    return NextResponse.json(
      { error: "Zaten bir kadron var. Değişiklik için Transfer ekranını kullan." },
      { status: 409 }
    );
  }

  const body = await req.json().catch(() => null);
  const transfermarktIds = body?.transfermarktIds as string[] | undefined;
  if (!Array.isArray(transfermarktIds)) {
    return NextResponse.json({ error: "Geçersiz istek." }, { status: 400 });
  }

  const playersById = await getPlayersById();
  const players = transfermarktIds.map((id) => playersById.get(id)).filter((p): p is NonNullable<typeof p> => Boolean(p));
  if (players.length !== transfermarktIds.length) {
    return NextResponse.json({ error: "Bazı oyuncular bulunamadı." }, { status: 400 });
  }

  const validation = validateSquad(players);
  if (!validation.ok) {
    return NextResponse.json({ error: validation.error }, { status: 400 });
  }

  const [squad] = await db.insert(fantasySquads).values({ userId: user.id }).returning();
  await db.insert(fantasySquadPlayers).values(transfermarktIds.map((id) => ({ squadId: squad.id, transfermarktId: id })));

  return NextResponse.json({ squad: { id: squad.id, freeTransfers: squad.freeTransfers } }, { status: 201 });
}
