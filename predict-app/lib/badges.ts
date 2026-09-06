import { sql } from "drizzle-orm";
import { getDb } from "@/db";
import { badges, predictions, users } from "@/db/schema";

export type BadgeCode =
  | "first_prediction"
  | "ten_predictions"
  | "twenty_five_predictions"
  | "oracle"
  | "streak_hunter"
  | "on_fire"
  | "century";

export type BadgeDef = {
  code: BadgeCode;
  icon: string;
  label: string;
  description: string;
};

export const BADGE_CATALOG: BadgeDef[] = [
  { code: "first_prediction", icon: "🥅", label: "İlk Tahmin", description: "İlk tahminini gönderdin." },
  { code: "ten_predictions", icon: "🎽", label: "Düzenli Taraftar", description: "10 tahmin gönderdin." },
  { code: "twenty_five_predictions", icon: "🏟️", label: "Sezonluk Kombine", description: "25 tahmin gönderdin." },
  { code: "oracle", icon: "🔮", label: "Kahin", description: "Bir maçta tam skoru tuttun." },
  { code: "streak_hunter", icon: "🔥", label: "Seri Avcısı", description: "3 maç üst üste isabet ettin." },
  { code: "on_fire", icon: "⚡", label: "Ateş Hattı", description: "5 maç üst üste isabet ettin." },
  { code: "century", icon: "💯", label: "Yüzler Kulübü", description: "Toplamda 100 puana ulaştın." },
];

type UserStats = {
  userId: number;
  predictionCount: number;
  totalPoints: number;
  perfectCount: number;
  bestStreak: number;
};

function earnedCodes(stats: UserStats): BadgeCode[] {
  const codes: BadgeCode[] = [];
  if (stats.predictionCount >= 1) codes.push("first_prediction");
  if (stats.predictionCount >= 10) codes.push("ten_predictions");
  if (stats.predictionCount >= 25) codes.push("twenty_five_predictions");
  if (stats.perfectCount >= 1) codes.push("oracle");
  if (stats.bestStreak >= 3) codes.push("streak_hunter");
  if (stats.bestStreak >= 5) codes.push("on_fire");
  if (stats.totalPoints >= 100) codes.push("century");
  return codes;
}

// Gerçek-zamana yakın tetikleyiciler (her puan/seri güncellemesinde) yerine, mevcut
// istatistiklerden rozet kriterlerini yeniden hesaplayıp eksik olanları ekliyoruz —
// idempotent, ve syncFinishedResults yalnızca yeni puanlama olduğunda çağırır.
export async function syncBadges(): Promise<void> {
  const db = getDb();

  const stats = await db
    .select({
      userId: users.id,
      predictionCount: sql<number>`count(${predictions.id})`.as("prediction_count"),
      totalPoints: sql<number>`coalesce(sum(${predictions.pointsEarned} + ${predictions.streakBonus}), 0)`.as(
        "total_points"
      ),
      perfectCount: sql<number>`count(*) filter (where ${predictions.pointsEarned} = 3)`.as("perfect_count"),
      bestStreak: users.bestStreak,
    })
    .from(users)
    .leftJoin(predictions, sql`${predictions.userId} = ${users.id}`)
    .groupBy(users.id, users.bestStreak);

  const rows = stats.flatMap((s) =>
    earnedCodes(s).map((code) => ({ userId: s.userId, code }))
  );
  if (rows.length === 0) return;

  await db.insert(badges).values(rows).onConflictDoNothing({ target: [badges.userId, badges.code] });
}
