import { NextResponse } from "next/server";
import { eq, and } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads, fantasySquadPlayers, fantasyGameweekLineups } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayersById } from "@/lib/fantasy-data";
import { getCurrentFantasyGameweek } from "@/lib/fantasy-week";
import { validateStartingXi } from "@/lib/fantasy-rules";

export async function GET() {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const db = getDb();
  const [squad] = await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1);
  if (!squad) return NextResponse.json({ lineup: null, gameweek: await getCurrentFantasyGameweek() });

  const gameweek = await getCurrentFantasyGameweek();
  let rows = gameweek.week
    ? await db
        .select()
        .from(fantasyGameweekLineups)
        .where(and(eq(fantasyGameweekLineups.squadId, squad.id), eq(fantasyGameweekLineups.week, gameweek.week)))
    : [];

  // Bu hafta için hiç kayıt yoksa, en son kaydedilmiş haftanın seçimini ön-doldurma
  // olarak göster (kullanıcı her hafta sıfırdan seçmek zorunda kalmasın).
  let prefilled = false;
  if (rows.length === 0) {
    const allRows = await db
      .select()
      .from(fantasyGameweekLineups)
      .where(eq(fantasyGameweekLineups.squadId, squad.id));
    if (allRows.length > 0) {
      const lastWeek = Math.max(...allRows.map((r) => r.week));
      rows = allRows.filter((r) => r.week === lastWeek);
      prefilled = true;
    }
  }

  return NextResponse.json({
    gameweek,
    prefilled,
    lineup: rows.map((r) => ({
      transfermarktId: r.transfermarktId,
      isStarting: r.isStarting,
      isCaptain: r.isCaptain,
      isViceCaptain: r.isViceCaptain,
    })),
  });
}

export async function POST(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const db = getDb();
  const [squad] = await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1);
  if (!squad) return NextResponse.json({ error: "Önce kadro kurmalısın." }, { status: 404 });

  const gameweek = await getCurrentFantasyGameweek();
  if (gameweek.locked || !gameweek.week) {
    return NextResponse.json({ error: "Bu hafta için ilk 11 seçim süresi doldu." }, { status: 409 });
  }

  const body = await req.json().catch(() => null);
  const starterIds = body?.starterIds as string[] | undefined;
  const captainId = body?.captainId as string | undefined;
  const viceCaptainId = body?.viceCaptainId as string | undefined;

  if (!Array.isArray(starterIds) || !captainId || !viceCaptainId) {
    return NextResponse.json({ error: "Geçersiz istek." }, { status: 400 });
  }
  if (!starterIds.includes(captainId) || !starterIds.includes(viceCaptainId) || captainId === viceCaptainId) {
    return NextResponse.json({ error: "Kaptan ve yedek kaptan ilk 11 içinde ve farklı olmalı." }, { status: 400 });
  }

  const squadPlayers = await db
    .select()
    .from(fantasySquadPlayers)
    .where(eq(fantasySquadPlayers.squadId, squad.id));
  const squadIds = squadPlayers.map((sp) => sp.transfermarktId);
  if (starterIds.some((id) => !squadIds.includes(id))) {
    return NextResponse.json({ error: "İlk 11'deki oyuncular kadronda değil." }, { status: 400 });
  }

  const playersById = await getPlayersById();
  const starters = starterIds.map((id) => playersById.get(id)).filter((p): p is NonNullable<typeof p> => Boolean(p));
  if (starters.length !== starterIds.length) {
    return NextResponse.json({ error: "Bazı oyuncular bulunamadı." }, { status: 400 });
  }
  const validation = validateStartingXi(starters);
  if (!validation.ok) {
    return NextResponse.json({ error: validation.error }, { status: 400 });
  }

  await db
    .delete(fantasyGameweekLineups)
    .where(and(eq(fantasyGameweekLineups.squadId, squad.id), eq(fantasyGameweekLineups.week, gameweek.week)));

  await db.insert(fantasyGameweekLineups).values(
    squadIds.map((id) => ({
      squadId: squad.id,
      week: gameweek.week!,
      transfermarktId: id,
      isStarting: starterIds.includes(id),
      isCaptain: id === captainId,
      isViceCaptain: id === viceCaptainId,
    }))
  );

  return NextResponse.json({ ok: true });
}
