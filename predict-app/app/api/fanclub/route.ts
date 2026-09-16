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

// Amigo olunca gösterilecek link — yalnızca http(s) kabul edilir (javascript: vb. XSS
// vektörlerini engellemek için), boş string/undefined verilirse link temizlenir (null).
function _sanitizeLink(raw: unknown): string | null {
  if (typeof raw !== "string" || raw.trim() === "") return null;
  try {
    const url = new URL(raw.trim());
    return url.protocol === "http:" || url.protocol === "https:" ? url.toString() : null;
  } catch {
    return null;
  }
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
  const link = _sanitizeLink(body?.link);

  const db = getDb();
  await db
    .insert(fanPicks)
    .values({ userId: user.id, team, link })
    .onConflictDoUpdate({ target: fanPicks.userId, set: { team, link, updatedAt: new Date() } });

  return NextResponse.json({ ok: true, team, link });
}
