import { syncFantasyResults } from "@/lib/sync-fantasy-results";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getFantasyLeaderboard } from "@/lib/fantasy-leaderboard";
import { FantasyLeaderboardTable } from "@/components/fantasy/fantasy-leaderboard-table";

export default async function FantasyLeaderboardPage() {
  await syncFantasyResults();
  const [viewer, ranked] = await Promise.all([getOrCreateUser(), getFantasyLeaderboard()]);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Kadro Kur — Lider Tablosu</h1>
      <FantasyLeaderboardTable ranked={ranked} viewerId={viewer?.id} />
    </div>
  );
}
