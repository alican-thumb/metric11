import type { FantasyRankedRow } from "@/lib/fantasy-leaderboard";

const VISIBLE_ROWS = 50;
const MEDALS = ["🥇", "🥈", "🥉"];

function Row({ r, viewerId }: { r: FantasyRankedRow; viewerId: number | undefined }) {
  const isSelf = r.userId === viewerId;
  return (
    <tr className={`border-t border-slate-800 ${isSelf ? "bg-lime-300/10" : ""}`}>
      <td className={`px-3 py-2 ${isSelf ? "text-lime-300" : "text-slate-500"}`}>{MEDALS[r.rank - 1] ?? r.rank}</td>
      <td className={`px-3 py-2 ${isSelf ? "font-semibold text-lime-300" : ""}`}>
        {r.displayName}
        {isSelf && <span className="ml-2 rounded bg-lime-300/20 px-1.5 py-0.5 text-xs">Sen</span>}
      </td>
      <td className="px-3 py-2 text-right text-slate-400">{r.gameweeksPlayed}</td>
      <td className="px-3 py-2 text-right font-semibold text-lime-300">{r.totalPoints}</td>
    </tr>
  );
}

export function FantasyLeaderboardTable({
  ranked,
  viewerId,
  emptyMessage = "Henüz kimse kadro kurmadı — ilk sen ol.",
}: {
  ranked: FantasyRankedRow[];
  viewerId: number | undefined;
  emptyMessage?: string;
}) {
  const visible = ranked.slice(0, VISIBLE_ROWS);
  const viewerRow = viewerId !== undefined ? ranked.find((r) => r.userId === viewerId) : undefined;
  const viewerOffScreen = Boolean(viewerRow && viewerRow.rank > VISIBLE_ROWS);

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800">
      <table className="w-full text-sm">
        <thead className="bg-slate-900 text-slate-400">
          <tr>
            <th className="px-3 py-2 text-left">#</th>
            <th className="px-3 py-2 text-left">Kullanıcı</th>
            <th className="px-3 py-2 text-right">Hafta</th>
            <th className="px-3 py-2 text-right">Puan</th>
          </tr>
        </thead>
        <tbody>
          {visible.map((r) => (
            <Row key={r.userId} r={r} viewerId={viewerId} />
          ))}
          {viewerOffScreen && viewerRow && (
            <>
              <tr>
                <td colSpan={4} className="px-3 py-1 text-center text-slate-600">
                  ⋯
                </td>
              </tr>
              <Row r={viewerRow} viewerId={viewerId} />
            </>
          )}
          {ranked.length === 0 && (
            <tr>
              <td colSpan={4} className="px-3 py-6 text-center text-slate-500">
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
