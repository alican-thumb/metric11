import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { groups, groupMembers } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { generateInviteCode } from "@/lib/invite-code";

export async function POST(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const body = await req.json().catch(() => null);
  const name = (body?.name as string | undefined)?.trim();
  if (!name || name.length < 2 || name.length > 40) {
    return NextResponse.json({ error: "Grup adı 2-40 karakter olmalı." }, { status: 400 });
  }

  const db = getDb();

  let inviteCode = generateInviteCode();
  for (let attempt = 0; attempt < 5; attempt++) {
    const existing = await db.select().from(groups).where(eq(groups.inviteCode, inviteCode)).limit(1);
    if (existing.length === 0) break;
    inviteCode = generateInviteCode();
  }

  const [group] = await db.insert(groups).values({ name, inviteCode, createdBy: user.id }).returning();
  await db.insert(groupMembers).values({ groupId: group.id, userId: user.id });

  return NextResponse.json({ group }, { status: 201 });
}
