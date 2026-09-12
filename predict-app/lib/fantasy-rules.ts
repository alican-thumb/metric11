import type { FantasyPlayer, PositionGroup } from "./fantasy-data";

export const BUDGET = 100.0;
export const SQUAD_SIZE = 15;
export const SQUAD_POSITION_COUNTS: Record<PositionGroup, number> = { GK: 2, DEF: 5, MID: 5, FWD: 3 };
export const MAX_PER_TEAM = 3;
export const STARTING_XI_SIZE = 11;
export const STARTING_XI_RANGE: Record<PositionGroup, [number, number]> = {
  GK: [1, 1],
  DEF: [3, 5],
  MID: [2, 5],
  FWD: [1, 3],
};

export function validateSquad(players: FantasyPlayer[]): { ok: true } | { ok: false; error: string } {
  if (players.length !== SQUAD_SIZE) {
    return { ok: false, error: `Kadro tam olarak ${SQUAD_SIZE} oyuncudan oluşmalı (şu an ${players.length}).` };
  }
  const totalCost = players.reduce((sum, p) => sum + p.price, 0);
  if (totalCost > BUDGET + 1e-6) {
    return { ok: false, error: `Bütçe aşıldı: ${totalCost.toFixed(1)} / ${BUDGET.toFixed(1)}.` };
  }
  const byPosition: Record<string, number> = {};
  const byTeam: Record<string, number> = {};
  for (const p of players) {
    byPosition[p.position_group] = (byPosition[p.position_group] ?? 0) + 1;
    byTeam[p.team] = (byTeam[p.team] ?? 0) + 1;
  }
  for (const [pos, required] of Object.entries(SQUAD_POSITION_COUNTS)) {
    if ((byPosition[pos] ?? 0) !== required) {
      return { ok: false, error: `${pos} sayısı ${required} olmalı (şu an ${byPosition[pos] ?? 0}).` };
    }
  }
  for (const [team, count] of Object.entries(byTeam)) {
    if (count > MAX_PER_TEAM) {
      return { ok: false, error: `${team}'dan en fazla ${MAX_PER_TEAM} oyuncu seçebilirsin (şu an ${count}).` };
    }
  }
  const uniqueIds = new Set(players.map((p) => p.transfermarkt_id));
  if (uniqueIds.size !== players.length) {
    return { ok: false, error: "Aynı oyuncu birden fazla kez seçilemez." };
  }
  return { ok: true };
}

export function validateStartingXi(
  starters: FantasyPlayer[]
): { ok: true } | { ok: false; error: string } {
  if (starters.length !== STARTING_XI_SIZE) {
    return { ok: false, error: `İlk 11 tam olarak ${STARTING_XI_SIZE} oyuncu olmalı (şu an ${starters.length}).` };
  }
  const byPosition: Record<string, number> = {};
  for (const p of starters) byPosition[p.position_group] = (byPosition[p.position_group] ?? 0) + 1;
  for (const [pos, [min, max]] of Object.entries(STARTING_XI_RANGE)) {
    const count = byPosition[pos] ?? 0;
    if (count < min || count > max) {
      return { ok: false, error: `${pos}: ${min}-${max} arası olmalı (şu an ${count}).` };
    }
  }
  return { ok: true };
}

export function squadCost(players: FantasyPlayer[]): number {
  return Math.round(players.reduce((sum, p) => sum + p.price, 0) * 10) / 10;
}

export function formationLabel(starters: FantasyPlayer[]): string {
  const def = starters.filter((p) => p.position_group === "DEF").length;
  const mid = starters.filter((p) => p.position_group === "MID").length;
  const fwd = starters.filter((p) => p.position_group === "FWD").length;
  return `${def}-${mid}-${fwd}`;
}
