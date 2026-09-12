import Link from "next/link";
import { auth } from "@clerk/nextjs/server";
import { eq, and } from "drizzle-orm";
import { getDb } from "@/db";
import { fantasySquads, fantasySquadPlayers, fantasyGameweekLineups } from "@/db/schema";
import { getOrCreateUser } from "@/lib/get-or-create-user";
import { getPlayersById } from "@/lib/fantasy-data";
import { getCurrentFantasyGameweek } from "@/lib/fantasy-week";
import { squadCost, BUDGET } from "@/lib/fantasy-rules";
import { syncFantasyResults } from "@/lib/sync-fantasy-results";
import { Pitch, PlayerChip, groupByPosition } from "@/components/fantasy/pitch";

export default async function FantasyHubPage() {
  const { userId } = await auth();

  if (!userId) {
    return <SignedOutHero />;
  }

  await syncFantasyResults();
  const user = await getOrCreateUser();
  const db = getDb();
  const [squad] = user
    ? await db.select().from(fantasySquads).where(eq(fantasySquads.userId, user.id)).limit(1)
    : [];

  if (!squad) {
    return <NoSquadHero />;
  }

  const [squadPlayerRows, gameweek] = await Promise.all([
    db.select().from(fantasySquadPlayers).where(eq(fantasySquadPlayers.squadId, squad.id)),
    getCurrentFantasyGameweek(),
  ]);
  const playersById = await getPlayersById();
  const squadPlayers = squadPlayerRows
    .map((sp) => playersById.get(sp.transfermarktId))
    .filter((p): p is NonNullable<typeof p> => Boolean(p));

  let lineupRows = gameweek.week
    ? await db
        .select()
        .from(fantasyGameweekLineups)
        .where(and(eq(fantasyGameweekLineups.squadId, squad.id), eq(fantasyGameweekLineups.week, gameweek.week)))
    : [];
  const hasCurrentLineup = lineupRows.length > 0;
  if (!hasCurrentLineup) {
    const allRows = await db.select().from(fantasyGameweekLineups).where(eq(fantasyGameweekLineups.squadId, squad.id));
    if (allRows.length > 0) {
      const lastWeek = Math.max(...allRows.map((r) => r.week));
      lineupRows = allRows.filter((r) => r.week === lastWeek);
    }
  }

  const startingIds = new Set(lineupRows.filter((r) => r.isStarting).map((r) => r.transfermarktId));
  const captainId = lineupRows.find((r) => r.isCaptain)?.transfermarktId;
  const viceCaptainId = lineupRows.find((r) => r.isViceCaptain)?.transfermarktId;
  const displayPlayers = startingIds.size > 0 ? squadPlayers.filter((p) => startingIds.has(p.transfermarkt_id)) : squadPlayers;
  const groups = groupByPosition(displayPlayers);

  const lastScoredWeekPoints = lineupRows
    .filter((r) => r.points !== null)
    .reduce((sum, r) => sum + (r.isCaptain ? (r.points ?? 0) * 2 : r.points ?? 0), 0);
  const anyScored = lineupRows.some((r) => r.points !== null);

  return (
    <div className="space-y-5">
      <HeroBanner />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Bütçe" value={`${squadCost(squadPlayers).toFixed(1)} / ${BUDGET.toFixed(1)}`} />
        <StatCard label="Ücretsiz Transfer" value={String(squad.transfersWeek === gameweek.week ? squad.freeTransfers : 1)} />
        <StatCard label={anyScored ? "Son Hafta Puanı" : "Hafta"} value={anyScored ? String(lastScoredWeekPoints) : gameweek.week ? `${gameweek.week}.` : "-"} />
        <StatCard label="Durum" value={gameweek.locked ? "🔒 Kilitli" : "✅ Açık"} />
      </div>

      <Pitch
        gk={groups.gk}
        def={groups.def}
        mid={groups.mid}
        fwd={groups.fwd}
        renderChip={(p) => (
          <PlayerChip
            key={p.transfermarkt_id}
            player={p}
            cornerBadge={p.transfermarkt_id === captainId ? "C" : p.transfermarkt_id === viceCaptainId ? "VC" : undefined}
          />
        )}
      />
      {!hasCurrentLineup && (
        <p className="text-center text-xs text-amber-400">
          {gameweek.week ? `${gameweek.week}. hafta` : "Bu hafta"} için ilk 11&apos;ini henüz seçmedin — geçen haftaki kadron gösteriliyor.
        </p>
      )}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <NavCard href="/kadro/hafta" title="İlk 11 & Kaptan" desc="Haftalık dizilişini ve kaptanını seç" />
        <NavCard href="/kadro/transfer" title="Transfer" desc="Kadronu güçlendir" />
        <NavCard href="/kadro/liderlik" title="Lider Tablosu" desc="Arkadaşlarına karşı sırala" />
      </div>
    </div>
  );
}

function HeroBanner() {
  return (
    <div className="overflow-hidden rounded-2xl border border-emerald-800/50 bg-gradient-to-br from-emerald-900/40 via-slate-900 to-slate-950 px-5 py-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-black tracking-tight">
            Kadro <span className="text-lime-300">Kur</span>
          </h1>
          <p className="text-xs text-slate-400">Süper Lig&apos;in gerçek maçlarıyla puan topla.</p>
        </div>
        <span className="rounded-full bg-lime-300/10 px-3 py-1 text-xs font-semibold text-lime-300 ring-1 ring-lime-300/30">
          Fantasy Manager
        </span>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2.5 text-center">
      <div className="text-[11px] text-slate-500">{label}</div>
      <div className="text-lg font-bold text-white">{value}</div>
    </div>
  );
}

function NavCard({ href, title, desc }: { href: string; title: string; desc: string }) {
  return (
    <Link
      href={href}
      className="group rounded-xl border border-slate-800 bg-slate-900/60 p-4 transition-colors hover:border-lime-300/50 hover:bg-slate-900"
    >
      <div className="font-semibold text-white group-hover:text-lime-300">{title} →</div>
      <div className="text-xs text-slate-500">{desc}</div>
    </Link>
  );
}

function NoSquadHero() {
  return (
    <div className="space-y-5">
      <HeroBanner />
      <div className="rounded-2xl border border-lime-300/20 bg-gradient-to-br from-lime-300/5 to-transparent p-6 text-center">
        <p className="mb-4 text-sm text-slate-300">
          {BUDGET.toFixed(1)} birim bütçeyle 15 kişilik kadronu kur, her hafta gerçek maçlardan puan topla, arkadaşlarınla yarış.
        </p>
        <Link
          href="/kadro/kur"
          className="inline-block rounded-xl bg-gradient-to-r from-lime-300 to-emerald-400 px-6 py-3 text-sm font-bold text-slate-950 shadow-lg shadow-lime-500/20 transition-transform hover:scale-105"
        >
          Kadronu Kur →
        </Link>
      </div>
      <RulesGrid />
    </div>
  );
}

function SignedOutHero() {
  return (
    <div className="space-y-5">
      <HeroBanner />
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-center">
        <p className="mb-2 text-sm text-slate-300">Süper Lig&apos;den kendi kadronu kur, her hafta gerçek maç istatistikleriyle puan topla.</p>
        <p className="text-xs text-slate-500">Başlamak için giriş yap veya üye ol (sağ üstte).</p>
      </div>
      <RulesGrid />
    </div>
  );
}

function RulesGrid() {
  const rules = [
    { emoji: "⚽", title: "Gol", desc: "Forvet +4 · Orta saha +5 · Defans/Kaleci +6" },
    { emoji: "🧤", title: "Temiz Sayfa", desc: "Gol yemeyen defans/kaleci +4" },
    { emoji: "🟨", title: "Kartlar", desc: "Sarı -1 · Kırmızı -3" },
    { emoji: "©️", title: "Kaptan", desc: "Kaptanın puanı 2 katına çıkar" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {rules.map((r) => (
        <div key={r.title} className="rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-center">
          <div className="text-xl">{r.emoji}</div>
          <div className="mt-1 text-xs font-semibold text-white">{r.title}</div>
          <div className="text-[11px] text-slate-500">{r.desc}</div>
        </div>
      ))}
    </div>
  );
}
