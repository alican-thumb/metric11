import { sql, eq, and, isNotNull } from "drizzle-orm";
import { getDb } from "@/db";
import { badges, predictions, users, fantasySquads, fantasyGameweekLineups } from "@/db/schema";
import { getFantasyLeaderboard } from "./fantasy-leaderboard";

export type BadgeCode =
  | "first_prediction"
  | "ten_predictions"
  | "twenty_five_predictions"
  | "oracle"
  | "streak_hunter"
  | "on_fire"
  | "century"
  | "fantasy_first_squad"
  | "fantasy_century"
  | "fantasy_super_week"
  | "fantasy_captain_hero";

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
  { code: "fantasy_first_squad", icon: "🎯", label: "İlk Kadro", description: "Kadro Kur'da ilk kadronu oluşturdun." },
  { code: "fantasy_century", icon: "🏆", label: "Kadro Yüzler Kulübü", description: "Kadro Kur'da toplamda 100 puana ulaştın." },
  { code: "fantasy_super_week", icon: "🚀", label: "Süper Hafta", description: "Kadro Kur'da bir haftada 50+ puan topladın." },
  { code: "fantasy_captain_hero", icon: "©️", label: "Kaptan Kahramanı", description: "Kaptanın tek başına bir haftada 20+ puan getirdi." },
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

// syncFantasyResults ile aynı desende çağrılan idempotent rozet senkronu — tahmin
// rozetlerinden ayrı tutulur çünkü kaynak veri (fantasySquads/fantasyGameweekLineups)
// tamamen farklı tablolar.
export async function syncFantasyBadges(): Promise<void> {
  const db = getDb();

  const squadOwners = await db.select({ userId: fantasySquads.userId }).from(fantasySquads);
  if (squadOwners.length === 0) return;

  const totals = await getFantasyLeaderboard();
  const totalByUser = new Map(totals.map((r) => [r.userId, r.totalPoints]));

  // Haftalık toplam (kaptan 2x dahil) — her (squad, hafta) için, yalnızca puanlanmış satırlar.
  const weeklyTotals = await db
    .select({
      userId: fantasySquads.userId,
      week: fantasyGameweekLineups.week,
      weekTotal: sql<number>`sum(case when ${fantasyGameweekLineups.isCaptain} then ${fantasyGameweekLineups.points} * 2 else ${fantasyGameweekLineups.points} end)`.as(
        "week_total"
      ),
    })
    .from(fantasyGameweekLineups)
    .innerJoin(fantasySquads, eq(fantasySquads.id, fantasyGameweekLineups.squadId))
    .where(isNotNull(fantasyGameweekLineups.points))
    .groupBy(fantasySquads.userId, fantasyGameweekLineups.week);

  const bestWeekByUser = new Map<number, number>();
  for (const row of weeklyTotals) {
    bestWeekByUser.set(row.userId, Math.max(bestWeekByUser.get(row.userId) ?? 0, row.weekTotal));
  }

  const captainHauls = await db
    .select({
      userId: fantasySquads.userId,
      captainPoints: fantasyGameweekLineups.points,
    })
    .from(fantasyGameweekLineups)
    .innerJoin(fantasySquads, eq(fantasySquads.id, fantasyGameweekLineups.squadId))
    .where(and(eq(fantasyGameweekLineups.isCaptain, true), isNotNull(fantasyGameweekLineups.points)));

  const bestCaptainByUser = new Map<number, number>();
  for (const row of captainHauls) {
    const haul = (row.captainPoints ?? 0) * 2;
    bestCaptainByUser.set(row.userId, Math.max(bestCaptainByUser.get(row.userId) ?? 0, haul));
  }

  const rows: { userId: number; code: BadgeCode }[] = [];
  for (const { userId } of squadOwners) {
    rows.push({ userId, code: "fantasy_first_squad" });
    if ((totalByUser.get(userId) ?? 0) >= 100) rows.push({ userId, code: "fantasy_century" });
    if ((bestWeekByUser.get(userId) ?? 0) >= 50) rows.push({ userId, code: "fantasy_super_week" });
    if ((bestCaptainByUser.get(userId) ?? 0) >= 20) rows.push({ userId, code: "fantasy_captain_hero" });
  }
  if (rows.length === 0) return;

  await db.insert(badges).values(rows).onConflictDoNothing({ target: [badges.userId, badges.code] });
}
