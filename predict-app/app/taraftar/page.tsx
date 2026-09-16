import { auth } from "@clerk/nextjs/server";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getSuperLigTeams } from "@/lib/fantasy-data";
import { getFanClubStandings } from "@/lib/fanclub";
import { TeamPicker } from "@/components/fanclub/team-picker";

export default async function FanClubPage() {
  const { userId } = await auth();
  const user = userId ? await getOrCreateUser() : null;
  const [teams, standings] = await Promise.all([getSuperLigTeams(), getFanClubStandings(user?.id)]);

  return (
    <div className="space-y-5">
      <div className="overflow-hidden rounded-2xl border border-emerald-800/50 bg-gradient-to-br from-emerald-900/40 via-slate-900 to-slate-950 px-5 py-4">
        <h1 className="text-xl font-black tracking-tight">
          Taraftar <span className="text-lime-300">Sayacı</span>
        </h1>
        <p className="text-xs text-slate-400">
          Süper Lig takımlarının gerçek taraftar sayımı — {standings.totalVotes} kullanıcı takımını seçti.
        </p>
      </div>

      <TeamPicker teams={teams} myTeam={standings.myTeam} signedIn={Boolean(userId)} />

      <div className="space-y-2">
        {standings.teams.map((row, i) => (
          <TeamRow key={row.team} rank={i + 1} team={row.team} count={row.count} percentage={row.percentage} isMine={row.team === standings.myTeam} />
        ))}
      </div>
    </div>
  );
}

function TeamRow({
  rank,
  team,
  count,
  percentage,
  isMine,
}: {
  rank: number;
  team: string;
  count: number;
  percentage: number;
  isMine: boolean;
}) {
  return (
    <div
      className={`relative overflow-hidden rounded-xl border px-4 py-2.5 ${
        isMine ? "border-lime-300/50 bg-lime-300/5" : "border-slate-800 bg-slate-900/60"
      }`}
    >
      <div
        className="absolute inset-y-0 left-0 bg-lime-300/10"
        style={{ width: `${Math.max(percentage * 100, count > 0 ? 2 : 0)}%` }}
      />
      <div className="relative flex items-center justify-between gap-3 text-sm">
        <div className="flex min-w-0 items-center gap-3">
          <span className="w-5 shrink-0 text-right text-xs font-semibold text-slate-500">{rank}</span>
          <span className={`truncate font-medium ${isMine ? "text-lime-300" : "text-white"}`}>{team}</span>
        </div>
        <div className="flex shrink-0 items-center gap-2 text-xs text-slate-400">
          <span className="font-bold text-white">{count}</span>
          <span>({(percentage * 100).toFixed(1)}%)</span>
        </div>
      </div>
    </div>
  );
}
