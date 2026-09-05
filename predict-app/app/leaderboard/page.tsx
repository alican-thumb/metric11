import { sql, desc } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions, users } from "@/db/schema";
import { syncFinishedResults } from "@/lib/sync-results";
import { getOrCreateUser } from "@/lib/get-or-create-user";

const VISIBLE_ROWS = 50;

type RankedRow = {
  userId: number;
  displayName: string;
  totalPoints: number;
  predictionCount: number;
  rank: number;
};

function Row({ r, viewerId }: { r: RankedRow; viewerId: number | undefined }) {
  const isSelf = r.userId === viewerId;
  return (
    <tr className={`border-t border-slate-800 ${isSelf ? "bg-lime-300/10" : ""}`}>
      <td className={`px-3 py-2 ${isSelf ? "text-lime-300" : "text-slate-500"}`}>{r.rank}</td>
      <td className={`px-3 py-2 ${isSelf ? "font-semibold text-lime-300" : ""}`}>
        {r.displayName}
        {isSelf && <span className="ml-2 rounded bg-lime-300/20 px-1.5 py-0.5 text-xs">Sen</span>}
      </td>
      <td className="px-3 py-2 text-right text-slate-400">{r.predictionCount}</td>
      <td className="px-3 py-2 text-right font-semibold text-lime-300">{r.totalPoints}</td>
    </tr>
  );
}

export default async function LeaderboardPage() {
  await syncFinishedResults();

  const [viewer, rows] = await Promise.all([
    getOrCreateUser(),
    (async () => {
      const db = getDb();
      return db
        .select({
          userId: users.id,
          displayName: users.displayName,
          totalPoints: sql<number>`coalesce(sum(${predictions.pointsEarned}), 0)`.as("total_points"),
          predictionCount: sql<number>`count(${predictions.id})`.as("prediction_count"),
        })
        .from(users)
        .leftJoin(predictions, sql`${predictions.userId} = ${users.id}`)
        .groupBy(users.id, users.displayName)
        .orderBy(desc(sql`total_points`));
    })(),
  ]);

  const ranked = rows.map((r, i) => ({ ...r, rank: i + 1 }));
  const visible = ranked.slice(0, VISIBLE_ROWS);
  const viewerRow = viewer ? ranked.find((r) => r.userId === viewer.id) : undefined;
  const viewerOffScreen = Boolean(viewerRow && viewerRow.rank > VISIBLE_ROWS);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Lider Tablosu</h1>
      <div className="overflow-hidden rounded-lg border border-slate-800">
        <table className="w-full text-sm">
          <thead className="bg-slate-900 text-slate-400">
            <tr>
              <th className="px-3 py-2 text-left">#</th>
              <th className="px-3 py-2 text-left">Kullanıcı</th>
              <th className="px-3 py-2 text-right">Tahmin</th>
              <th className="px-3 py-2 text-right">Puan</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((r) => (
              <Row key={r.userId} r={r} viewerId={viewer?.id} />
            ))}
            {viewerOffScreen && viewerRow && (
              <>
                <tr>
                  <td colSpan={4} className="px-3 py-1 text-center text-slate-600">
                    ⋯
                  </td>
                </tr>
                <Row r={viewerRow} viewerId={viewer?.id} />
              </>
            )}
            {ranked.length === 0 && (
              <tr>
                <td colSpan={4} className="px-3 py-6 text-center text-slate-500">
                  Henüz kimse tahmin girmedi — ilk sen ol.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
