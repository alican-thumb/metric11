import { NextResponse } from "next/server";
import { eq, and } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getMatchById, isLocked } from "@/lib/metric11-data";

export async function GET() {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const db = getDb();
  const rows = await db.select().from(predictions).where(eq(predictions.userId, user.id));
  return NextResponse.json({ predictions: rows });
}

export async function POST(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const body = await req.json().catch(() => null);
  const matchId = body?.matchId as string | undefined;
  const predictedHome = Number(body?.predictedHome);
  const predictedAway = Number(body?.predictedAway);

  if (
    !matchId ||
    !Number.isInteger(predictedHome) ||
    !Number.isInteger(predictedAway) ||
    predictedHome < 0 ||
    predictedAway < 0 ||
    predictedHome > 20 ||
    predictedAway > 20
  ) {
    return NextResponse.json({ error: "Geçersiz tahmin." }, { status: 400 });
  }

  // KRİTİK: kilit kontrolü sunucu tarafında yapılır — istemci tarafı kontrolü tek başına
  // yeterli değil (bypass edilebilir).
  const match = await getMatchById(matchId);
  if (!match) {
    return NextResponse.json({ error: "Maç bulunamadı." }, { status: 404 });
  }
  if (isLocked(match)) {
    return NextResponse.json({ error: "Bu maç için tahmin süresi doldu (kickoff geçti)." }, { status: 409 });
  }

  const db = getDb();
  const existing = await db
    .select()
    .from(predictions)
    .where(and(eq(predictions.userId, user.id), eq(predictions.matchId, matchId)))
    .limit(1);

  if (existing.length > 0) {
    const [updated] = await db
      .update(predictions)
      .set({ predictedHome, predictedAway, updatedAt: new Date() })
      .where(eq(predictions.id, existing[0].id))
      .returning();
    return NextResponse.json({ prediction: updated });
  }

  const [created] = await db
    .insert(predictions)
    .values({ userId: user.id, matchId, predictedHome, predictedAway })
    .returning();
  return NextResponse.json({ prediction: created }, { status: 201 });
}
