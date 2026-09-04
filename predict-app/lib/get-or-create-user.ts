import { eq } from "drizzle-orm";
import { currentUser } from "@clerk/nextjs/server";
import { getDb } from "@/db";
import { users } from "@/db/schema";

// Clerk kimliği doğrulanmış oturumu tek gerçek kaynak olarak kullanır; yerel `users`
// satırı yalnızca predictions/leaderboard tarafında join yapabilmek için var — Clerk'in
// kendisini tekrar üretmez (parola, e-posta vb. hiçbiri burada tutulmaz).
export async function getOrCreateUser() {
  const clerkUser = await currentUser();
  if (!clerkUser) return null;

  const db = getDb();
  const existing = await db.select().from(users).where(eq(users.clerkUserId, clerkUser.id)).limit(1);
  if (existing.length > 0) return existing[0];

  const displayName =
    clerkUser.username ??
    clerkUser.firstName ??
    clerkUser.emailAddresses[0]?.emailAddress?.split("@")[0] ??
    "Kullanıcı";

  const [created] = await db
    .insert(users)
    .values({ clerkUserId: clerkUser.id, displayName })
    .returning();
  return created;
}
