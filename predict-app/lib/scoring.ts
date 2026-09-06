// Puanlama kuralı (2026-09-06'da kullanıcı isteğiyle güncellendi): üç ayrı kriter var,
// her biri kendi puanını ayrı ayrı ekliyor (üst üste biniyor, birbirini dışlamıyor):
//   1) Doğru sonuç (1X2 — kim kazandı/kaybetti ya da beraberlik)  → +1
//   2) Doğru gol farkı (kaç farkla kazanıldığı/kaybedildiği)      → +1
//   3) Tam doğru skor                                             → +1
// Gol farkı doğruysa sonuç yönü de otomatik doğru olur (aynı işaretli fark aynı
// sonucu ima eder), tam skor doğruysa ikisi de doğrudur — yani puanlar doğal olarak
// üst üste yığılıyor: yalnız yön doğru=1, yön+fark doğru ama skor değil=2, tam skor=3.
export function computePoints(
  predictedHome: number,
  predictedAway: number,
  actualHome: number,
  actualAway: number
): number {
  let points = 0;
  if (outcome(predictedHome, predictedAway) === outcome(actualHome, actualAway)) points += 1;
  if (predictedHome - predictedAway === actualHome - actualAway) points += 1;
  if (predictedHome === actualHome && predictedAway === actualAway) points += 1;
  return points;
}

function outcome(home: number, away: number): "home" | "draw" | "away" {
  if (home > away) return "home";
  if (home < away) return "away";
  return "draw";
}

// "2 - 2" -> {home: 2, away: 2}. metric11'in actual_score alanı bu formatta.
export function parseActualScore(actualScore: string): { home: number; away: number } | null {
  const match = actualScore.match(/^(\d+)\s*-\s*(\d+)$/);
  if (!match) return null;
  return { home: Number(match[1]), away: Number(match[2]) };
}

// Seri bonusu: ardışık isabetli (pointsEarned > 0) tahminler için ödül. `streak`, bu
// tahmin dahil edilmiş ardışık isabet sayısıdır (bkz. lib/sync-results.ts).
export function computeStreakBonus(streak: number): number {
  if (streak >= 5) return 2;
  if (streak >= 3) return 1;
  return 0;
}
