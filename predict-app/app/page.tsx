import { eq } from "drizzle-orm";
import { auth } from "@clerk/nextjs/server";
import { getDb } from "@/db";
import { predictions } from "@/db/schema";
import { getUpcomingMatches } from "@/lib/metric11-data";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { MatchPredictionCard } from "@/components/match-prediction-card";

export default async function HomePage() {
  const { userId } = await auth();
  const upcoming = await getUpcomingMatches(); // her zaman tek bir haftanın maçları (bkz. lib/metric11-data.ts)
  const weekLabel = upcoming[0]?.week;

  let existing: Record<string, { predictedHome: number; predictedAway: number }> = {};
  if (userId) {
    const user = await getOrCreateUser();
    if (user) {
      const db = getDb();
      const rows = await db.select().from(predictions).where(eq(predictions.userId, user.id));
      existing = Object.fromEntries(
        rows.map((r) => [r.matchId, { predictedHome: r.predictedHome, predictedAway: r.predictedAway }])
      );
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">
        Bu Haftanın Maçları{weekLabel ? ` (${weekLabel}. Hafta)` : ""}
      </h1>
      <p className="text-sm text-slate-400">
        Kickoff&apos;a kadar tahminini gir/değiştir — maç başladıktan sonra kilitlenir.
      </p>
      {upcoming.length === 0 && <p className="text-slate-400">Şu an tahmin edilecek yaklaşan maç yok.</p>}
      <div className="space-y-3">
        {upcoming.map((m) => (
          <MatchPredictionCard
            key={m.match_id}
            matchId={m.match_id}
            homeTeam={m.home_team}
            awayTeam={m.away_team}
            dateTime={m.date_time}
            metric11Prediction={m.recommended_scoreline.score}
            initialHome={existing[m.match_id]?.predictedHome}
            initialAway={existing[m.match_id]?.predictedAway}
            isSignedIn={Boolean(userId)}
          />
        ))}
      </div>
    </div>
  );
}
