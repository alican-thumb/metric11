import { NextResponse } from "next/server";
import { getDb } from "@/db";
import { fanPicks } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getSuperLigTeams } from "@/lib/fantasy-data";
import { getFanClubStandings } from "@/lib/fanclub";

export async function GET() {
  const user = await getOrCreateUser();
  const standings = await getFanClubStandings(user?.id);
  return NextResponse.json(standings);
}

export async function POST(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const body = await req.json().catch(() => null);
  const team = body?.team as string | undefined;
  if (!team) return NextResponse.json({ error: "Geçersiz istek." }, { status: 400 });

  const validTeams = await getSuperLigTeams();
  if (!validTeams.includes(team)) {
    return NextResponse.json({ error: "Geçersiz takım." }, { status: 400 });
  }

  const db = getDb();
  await db
    .insert(fanPicks)
    .values({ userId: user.id, team })
    .onConflictDoUpdate({ target: fanPicks.userId, set: { team, updatedAt: new Date() } });

  return NextResponse.json({ ok: true, team });
}
