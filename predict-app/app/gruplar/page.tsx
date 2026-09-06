import Link from "next/link";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { groups, groupMembers } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { CreateGroupForm } from "@/components/create-group-form";
import { JoinGroupForm } from "@/components/join-group-form";

export default async function GruplarPage() {
  const user = await getOrCreateUser();
  if (!user) {
    return <p className="text-slate-400">Bu sayfayı görmek için giriş yapmalısınız.</p>;
  }

  const db = getDb();
  const rows = await db
    .select({ id: groups.id, name: groups.name, inviteCode: groups.inviteCode })
    .from(groupMembers)
    .innerJoin(groups, eq(groups.id, groupMembers.groupId))
    .where(eq(groupMembers.userId, user.id));

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Gruplar</h1>
      <p className="text-sm text-slate-400">
        Arkadaşlarınla özel bir lig kur, davet kodunu paylaş, sadece aranızda yarışın.
      </p>

      <div className="space-y-2">
        {rows.map((g) => (
          <Link
            key={g.id}
            href={`/gruplar/${g.inviteCode}`}
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm hover:border-lime-300/40"
          >
            <span className="font-semibold">{g.name}</span>
            <span className="font-mono text-slate-500">{g.inviteCode}</span>
          </Link>
        ))}
        {rows.length === 0 && <p className="text-slate-500">Henüz bir grubun yok.</p>}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h2 className="mb-2 text-sm font-semibold text-slate-300">Yeni grup kur</h2>
          <CreateGroupForm />
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h2 className="mb-2 text-sm font-semibold text-slate-300">Davet koduyla katıl</h2>
          <JoinGroupForm />
        </div>
      </div>
    </div>
  );
}
