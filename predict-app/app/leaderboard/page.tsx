import { sql, desc } from "drizzle-orm";
import { getDb } from "@/db";
import { predictions, users } from "@/db/schema";
import { syncFinishedResults } from "@/lib/sync-results";

export default async function LeaderboardPage() {
  await syncFinishedResults();

  const db = getDb();
  const rows = await db
    .select({
      displayName: users.displayName,
      totalPoints: sql<number>`coalesce(sum(${predictions.pointsEarned}), 0)`.as("total_points"),
      predictionCount: sql<number>`count(${predictions.id})`.as("prediction_count"),
    })
    .from(users)
    .leftJoin(predictions, sql`${predictions.userId} = ${users.id}`)
    .groupBy(users.id, users.displayName)
    .orderBy(desc(sql`total_points`))
    .limit(50);

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
            {rows.map((r, i) => (
              <tr key={r.displayName + i} className="border-t border-slate-800">
                <td className="px-3 py-2 text-slate-500">{i + 1}</td>
                <td className="px-3 py-2">{r.displayName}</td>
                <td className="px-3 py-2 text-right text-slate-400">{r.predictionCount}</td>
                <td className="px-3 py-2 text-right font-semibold text-lime-300">{r.totalPoints}</td>
              </tr>
            ))}
            {rows.length === 0 && (
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
