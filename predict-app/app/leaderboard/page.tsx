import Link from "next/link";
import { syncFinishedResults } from "@/lib/sync-results";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getCurrentWeekMatchIds } from "@/lib/metric11-data";
import { getRankedLeaderboard } from "@/lib/leaderboard";
import { LeaderboardTable } from "@/components/leaderboard-table";

export default async function LeaderboardPage({
  searchParams,
}: {
  searchParams: Promise<{ view?: string }>;
}) {
  await syncFinishedResults();
  const { view } = await searchParams;
  const isWeekly = view === "hafta";

  const { week, matchIds } = await getCurrentWeekMatchIds();

  const [viewer, ranked] = await Promise.all([
    getOrCreateUser(),
    isWeekly ? getRankedLeaderboard({ matchIds }) : getRankedLeaderboard(),
  ]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Lider Tablosu</h1>
        <Link href="/gruplar" className="text-sm text-lime-300 hover:underline">
          Arkadaşlarınla karşılaştır →
        </Link>
      </div>
      <div className="flex gap-2 text-sm">
        <Link
          href="/leaderboard"
          className={`rounded-md px-3 py-1.5 ${!isWeekly ? "bg-lime-300 font-semibold text-slate-900" : "bg-slate-900 text-slate-300"}`}
        >
          Genel
        </Link>
        <Link
          href="/leaderboard?view=hafta"
          className={`rounded-md px-3 py-1.5 ${isWeekly ? "bg-lime-300 font-semibold text-slate-900" : "bg-slate-900 text-slate-300"}`}
        >
          Bu Hafta{week ? ` (${week}. Hafta)` : ""}
        </Link>
      </div>
      <LeaderboardTable
        ranked={ranked}
        viewerId={viewer?.id}
        emptyMessage={
          isWeekly ? "Bu hafta henüz kimse tahmin girmedi." : "Henüz kimse tahmin girmedi — ilk sen ol."
        }
      />
    </div>
  );
}
