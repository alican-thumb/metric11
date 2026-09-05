import { NextResponse } from "next/server";
import { eq, ne, sql } from "drizzle-orm";
import { getDb } from "@/db";
import { users } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";

// Türkçe harfler dahil harf/rakam/boşluk/tire/alt çizgi, 2-24 karakter.
const NAME_PATTERN = /^[\p{L}\p{N} _-]{2,24}$/u;

export async function PATCH(req: Request) {
  const user = await getOrCreateUser();
  if (!user) return NextResponse.json({ error: "Giriş yapmalısınız." }, { status: 401 });

  const body = await req.json().catch(() => null);
  const displayName = typeof body?.displayName === "string" ? body.displayName.trim() : "";

  if (!NAME_PATTERN.test(displayName)) {
    return NextResponse.json(
      { error: "Kullanıcı adı 2-24 karakter olmalı, sadece harf/rakam/boşluk/tire/alt çizgi içerebilir." },
      { status: 400 }
    );
  }

  const db = getDb();
  const clash = await db
    .select({ id: users.id })
    .from(users)
    .where(sql`lower(${users.displayName}) = lower(${displayName}) and ${ne(users.id, user.id)}`)
    .limit(1);

  if (clash.length > 0) {
    return NextResponse.json({ error: "Bu kullanıcı adı zaten alınmış." }, { status: 409 });
  }

  const [updated] = await db
    .update(users)
    .set({ displayName })
    .where(eq(users.id, user.id))
    .returning();

  return NextResponse.json({ user: updated });
}
