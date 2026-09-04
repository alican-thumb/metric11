import { eq } from "drizzle-orm";
import { currentUser } from "@clerk/nextjs/server";
import { getDb } from "@/db";
import { users } from "@/db/schema";

// Kullanıcı sign-up'ta yalnızca e-posta+şifre girer (username alanı yok) — Clerk'in
// e-posta yerel kısmını displayName'e düşürmesine izin vermek, lider tablosunda
// kullanıcının e-posta adresini ifşa eder. Bunun yerine sabit (clerkUserId'den türetilen,
// her seferinde aynı) futbol temalı bir takma ad üretiyoruz — hem gizliliği korur hem de
// oyunlaştırmayı güçlendirir.
const _ADJ = [
  "Cesur", "Sessiz", "Hızlı", "Keskin", "Soğukkanlı", "Yorulmaz", "Vuruşkan",
  "Efsanevi", "Gölge", "Vahşi", "Usta", "Sinsi", "Öngörülü", "Kahraman", "Şanslı",
];
const _NOUN = [
  "Kartal", "Penaltı", "Frikik", "Santrafor", "Libero", "Kaleci", "Golcü",
  "Orta Saha", "Stoper", "Taraftar", "Kupa", "Derbi", "Ofsayt", "Korner", "Şut",
];

function _fallbackNickname(seed: string): string {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  const adj = _ADJ[hash % _ADJ.length];
  const noun = _NOUN[Math.floor(hash / _ADJ.length) % _NOUN.length];
  const num = hash % 100;
  return `${adj}${noun}${num}`;
}

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
    _fallbackNickname(clerkUser.id);

  const [created] = await db
    .insert(users)
    .values({ clerkUserId: clerkUser.id, displayName })
    .returning();
  return created;
}
