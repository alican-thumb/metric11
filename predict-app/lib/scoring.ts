// Puanlama kuralı (plan dosyasında kullanıcıyla onaylandı): tam skor 3 puan, yalnız
// sonuç yönü (1X2) doğruysa 1 puan, yanlışsa 0.
export function computePoints(
  predictedHome: number,
  predictedAway: number,
  actualHome: number,
  actualAway: number
): number {
  if (predictedHome === actualHome && predictedAway === actualAway) return 3;
  const predictedOutcome = outcome(predictedHome, predictedAway);
  const actualOutcome = outcome(actualHome, actualAway);
  return predictedOutcome === actualOutcome ? 1 : 0;
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
