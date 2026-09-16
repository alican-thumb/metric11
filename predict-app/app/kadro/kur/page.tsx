import { redirect } from "next/navigation";
import Link from "next/link";
import { auth } from "@clerk/nextjs/server";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayerPool } from "@/lib/fantasy-data";
import { BUDGET, SQUAD_POSITION_COUNTS, MAX_PER_TEAM } from "@/lib/fantasy-rules";
import { SquadBuilder } from "@/components/fantasy/squad-builder";
import { ResetSquadButton } from "@/components/fantasy/reset-squad-button";

export default async function SquadBuilderPage() {
  const { userId } = await auth();
  if (!userId) redirect("/kadro");

  const user = await getOrCreateUser();
  if (user) {
    const db = getDb();
    const [existing] = await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1);
    if (existing) return <AlreadyHasSquad />;
  }

  const pool = await getPlayerPool();

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold">Kadronu Kur</h1>
        <p className="text-sm text-slate-400">
          {BUDGET.toFixed(1)} birimlik bütçeyle 15 kişilik kadro kur: {SQUAD_POSITION_COUNTS.GK} kaleci,{" "}
          {SQUAD_POSITION_COUNTS.DEF} defans, {SQUAD_POSITION_COUNTS.MID} orta saha, {SQUAD_POSITION_COUNTS.FWD} forvet —
          bir takımdan en fazla {MAX_PER_TEAM} oyuncu.
        </p>
      </div>
      <SquadBuilder allPlayers={pool.players} />
    </div>
  );
}

function AlreadyHasSquad() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold">Kadronu Kur</h1>
        <p className="text-sm text-slate-400">Zaten bir kadron var. Tek tek değiştirmek için Transfer ekranını kullanabilirsin.</p>
      </div>
      <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-3 text-sm">
          <Link href="/kadro" className="font-semibold text-lime-300 hover:underline">
            Kadromu Gör →
          </Link>
          <Link href="/kadro/transfer" className="font-semibold text-lime-300 hover:underline">
            Transfer Yap →
          </Link>
        </div>
        <ResetSquadButton />
      </div>
    </div>
  );
}
