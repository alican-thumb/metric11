// Ana statik site (metric11.com) zaten data/processed/*.json dosyalarını public statik
// dosya olarak yayınlıyor — bu uygulama Python pipeline'a hiç dokunmadan, aynı verileri
// doğrudan HTTP ile okur. Doğrulanmış gerçek alan adları için bkz. plan dosyası.
const METRIC11_BASE_URL = process.env.METRIC11_BASE_URL ?? "https://metric11.com";

export type Metric11Match = {
  match_id: string;
  date_time: string; // "DD.MM.YYYY HH:MM", Türkiye yerel saati (UTC+3)
  home_team: string;
  away_team: string;
  is_played: boolean;
  actual_score: string | null; // "H - A" veya null
  home_win_probability: number;
  draw_probability: number;
  away_win_probability: number;
  recommended_scoreline: { score: string; home_goals: number; away_goals: number; probability: number };
};

type FixturePayload = {
  generated_at: string;
  weeks: { week: number; matches: Metric11Match[] }[];
};

export type ScorerCandidate = {
  player: string;
  scores_probability: number;
  projected: boolean;
};

type ScorerPayload = {
  matches: Record<string, { home_scorers: ScorerCandidate[]; away_scorers: ScorerCandidate[]; lineup_confirmed: boolean }>;
};

let fixtureCache: { data: Metric11Match[]; fetchedAt: number } | null = null;
const FIXTURE_CACHE_TTL_MS = 5 * 60 * 1000; // 5 dk — ana site zaten en sık 6 saatte bir yenileniyor

export async function getAllMatches(): Promise<Metric11Match[]> {
  if (fixtureCache && Date.now() - fixtureCache.fetchedAt < FIXTURE_CACHE_TTL_MS) {
    return fixtureCache.data;
  }
  const res = await fetch(`${METRIC11_BASE_URL}/season_fixture_predictions_2026_2027.json`, {
    next: { revalidate: 300 },
  });
  if (!res.ok) {
    throw new Error(`metric11 fixture verisi çekilemedi: HTTP ${res.status}`);
  }
  const payload = (await res.json()) as FixturePayload;
  const matches = payload.weeks.flatMap((w) => w.matches);
  fixtureCache = { data: matches, fetchedAt: Date.now() };
  return matches;
}

export async function getMatchById(matchId: string): Promise<Metric11Match | undefined> {
  const matches = await getAllMatches();
  return matches.find((m) => m.match_id === matchId);
}

export async function getUpcomingMatches(): Promise<Metric11Match[]> {
  const matches = await getAllMatches();
  const now = new Date();
  return matches
    .filter((m) => !m.is_played && parseKickoff(m.date_time) > now)
    .sort((a, b) => parseKickoff(a.date_time).getTime() - parseKickoff(b.date_time).getTime());
}

export async function getScorerPredictions(matchId: string): Promise<ScorerPayload["matches"][string] | undefined> {
  const res = await fetch(`${METRIC11_BASE_URL}/goal_scorer_predictions_2026_2027.json`, {
    next: { revalidate: 300 },
  });
  if (!res.ok) return undefined;
  const payload = (await res.json()) as ScorerPayload;
  return payload.matches[matchId];
}

// "DD.MM.YYYY HH:MM" (Türkiye yerel, UTC+3, DST yok) -> gerçek UTC Date.
// src/model_league_predictions.py::parse_tff_datetime ile aynı format varsayımı.
export function parseKickoff(dateTime: string): Date {
  const [datePart, timePart] = dateTime.trim().split(" ");
  const [day, month, year] = datePart.split(".").map(Number);
  const [hour, minute] = timePart.split(":").map(Number);
  // UTC+3 yerel saat -> UTC: 3 saat çıkar.
  return new Date(Date.UTC(year, month - 1, day, hour - 3, minute));
}

export function isLocked(match: Metric11Match): boolean {
  return match.is_played || parseKickoff(match.date_time) <= new Date();
}
