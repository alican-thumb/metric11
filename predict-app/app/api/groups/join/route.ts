import { NextResponse } from "next/server";
import { eq, and } from "drizzle-orm";
import { getDb } from "@/db";
import { groups, groupMembers } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";

export async function POST(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const body = await req.json().catch(() => null);
  const code = (body?.code as string | undefined)?.trim().toUpperCase();
  if (!code) return NextResponse.json({ error: "Davet kodu gerekli." }, { status: 400 });

  const db = getDb();
  const [group] = await db.select().from(groups).where(eq(groups.inviteCode, code)).limit(1);
  if (!group) return NextResponse.json({ error: "Geçersiz davet kodu." }, { status: 404 });

  const existing = await db
    .select()
    .from(groupMembers)
    .where(and(eq(groupMembers.groupId, group.id), eq(groupMembers.userId, user.id)))
    .limit(1);
  if (existing.length === 0) {
    await db.insert(groupMembers).values({ groupId: group.id, userId: user.id });
  }

  return NextResponse.json({ group });
}
