// Kadro Kur (Fantasy Manager) oyuncu havuzu + haftalık gerçek puanlar — ana statik site
// (metric11.com) tarafından yayınlanan JSON'lar, aynı desen (bkz. metric11-data.ts):
// Python pipeline'a dokunmadan doğrudan HTTP ile okunur.
const METRIC11_BASE_URL = process.env.METRIC11_BASE_URL ?? "https://metric11.com";

export type PositionGroup = "GK" | "DEF" | "MID" | "FWD";

export type FantasyPlayer = {
  transfermarkt_id: string;
  name: string;
  team: string;
  shirt_number: string | number | null;
  position: string | null;
  position_group: PositionGroup;
  age: number | null;
  market_value_eur: number;
  price: number;
  tff_external_id: string | null;
  season_stats: {
    starts: number;
    bench: number;
    goals: number;
    own_goals: number;
    yellow_cards: number;
    red_cards: number;
    matches_played: number;
  };
};

type PlayerPoolPayload = {
  generated_at: string;
  season: string;
  player_count: number;
  budget_default: number;
  squad_rules: {
    squad_size: number;
    positions: Record<PositionGroup, number>;
    max_players_per_team: number;
    starting_xi: Record<PositionGroup, [number, number]>;
  };
  players: FantasyPlayer[];
};

export type GameweekPlayerRow = {
  transfermarkt_id: string | null;
  tff_external_id: string;
  name: string;
  team: string;
  position_group: PositionGroup;
  started: boolean;
  goals: number;
  own_goals: number;
  yellow_cards: number;
  red_cards: number;
  clean_sheet: boolean;
  points: number;
};

type GameweekScoresPayload = {
  generated_at: string;
  season: string;
  weeks_scored: number;
  weeks: { week: number; matches: { match_id: string; players: GameweekPlayerRow[] }[] }[];
  player_totals: (GameweekPlayerRow & { total_points: number; gameweeks_played: number })[];
};

let poolCache: { data: PlayerPoolPayload; fetchedAt: number } | null = null;
let scoresCache: { data: GameweekScoresPayload; fetchedAt: number } | null = null;
const CACHE_TTL_MS = 5 * 60 * 1000;

export async function getPlayerPool(): Promise<PlayerPoolPayload> {
  if (poolCache && Date.now() - poolCache.fetchedAt < CACHE_TTL_MS) return poolCache.data;
  const res = await fetch(`${METRIC11_BASE_URL}/fantasy_player_pool_2026_2027.json`, { cache: "no-store" });
  if (!res.ok) throw new Error(`fantasy oyuncu havuzu çekilemedi: HTTP ${res.status}`);
  const data = (await res.json()) as PlayerPoolPayload;
  poolCache = { data, fetchedAt: Date.now() };
  return data;
}

export async function getPlayersById(): Promise<Map<string, FantasyPlayer>> {
  const pool = await getPlayerPool();
  return new Map(pool.players.map((p) => [p.transfermarkt_id, p]));
}

export async function getGameweekScores(): Promise<GameweekScoresPayload> {
  if (scoresCache && Date.now() - scoresCache.fetchedAt < CACHE_TTL_MS) return scoresCache.data;
  const res = await fetch(`${METRIC11_BASE_URL}/fantasy_gameweek_scores_2026_2027.json`, { cache: "no-store" });
  if (!res.ok) throw new Error(`fantasy haftalık puan verisi çekilemedi: HTTP ${res.status}`);
  const data = (await res.json()) as GameweekScoresPayload;
  scoresCache = { data, fetchedAt: Date.now() };
  return data;
}

// Bir hafta içindeki maçların HEPSİ bitmemiş olabilir — bu yüzden oyuncu bazında bakılır:
// oyuncunun kendi maçı işlenmişse (haftanın maç listesinde geçiyorsa) puanı vardır.
export async function getGameweekPlayerPoints(week: number): Promise<Map<string, number>> {
  const scores = await getGameweekScores();
  const weekData = scores.weeks.find((w) => w.week === week);
  const map = new Map<string, number>();
  if (!weekData) return map;
  for (const match of weekData.matches) {
    for (const row of match.players) {
      const key = row.transfermarkt_id ?? `tff:${row.tff_external_id}`;
      map.set(key, row.points);
    }
  }
  return map;
}
