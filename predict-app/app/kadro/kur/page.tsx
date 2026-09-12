import { redirect } from "next/navigation";
import { auth } from "@clerk/nextjs/server";
import { eq } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayerPool } from "@/lib/fantasy-data";
import { BUDGET, SQUAD_POSITION_COUNTS, MAX_PER_TEAM } from "@/lib/fantasy-rules";
import { SquadBuilder } from "@/components/fantasy/squad-builder";

export default async function SquadBuilderPage() {
  const { userId } = await auth();
  if (!userId) redirect("/kadro");

  const user = await getOrCreateUser();
  if (user) {
    const db = getDb();
    const [existing] = await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1);
    if (existing) redirect("/kadro");
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
