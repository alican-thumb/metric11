import { notFound } from "next/navigation";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { groups, groupMembers } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getRankedLeaderboard } from "@/lib/leaderboard";
import { syncFinishedResults } from "@/lib/sync-results";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { JoinGroupForm } from "@/components/join-group-form";

export default async function GroupPage({ params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;
  const user = await getOrCreateUser();
  if (!user) {
    return <p className="text-slate-400">Bu sayfayı görmek için giriş yapmalısınız.</p>;
  }

  const db = getDb();
  const [group] = await db
    .select()
    .from(groups)
    .where(eq(groups.inviteCode, code.toUpperCase()))
    .limit(1);
  if (!group) notFound();

  const members = await db.select().from(groupMembers).where(eq(groupMembers.groupId, group.id));
  const isMember = members.some((m) => m.userId === user.id);

  if (!isMember) {
    return (
      <div className="space-y-4">
        <h1 className="text-xl font-bold">{group.name}</h1>
        <p className="text-slate-400">Bu gruba henüz üye değilsin.</p>
        <div className="max-w-xs rounded-lg border border-slate-800 bg-slate-900 p-4">
          <JoinGroupForm defaultCode={group.inviteCode} />
        </div>
      </div>
    );
  }

  await syncFinishedResults();
  const ranked = await getRankedLeaderboard({ userIds: members.map((m) => m.userId) });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{group.name}</h1>
        <span className="text-xs text-slate-500">
          Davet kodu: <span className="font-mono text-lime-300">{group.inviteCode}</span>
        </span>
      </div>
      <p className="text-sm text-slate-400">
        Bu kodu paylaşarak arkadaşlarını davet edebilirsin — {members.length} üye.
      </p>
      <LeaderboardTable
        ranked={ranked}
        viewerId={user.id}
        emptyMessage="Grupta henüz kimse tahmin girmedi."
      />
    </div>
  );
}
