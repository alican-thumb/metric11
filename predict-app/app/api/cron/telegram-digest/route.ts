import { NextResponse } from "next/server";
import { getUpcomingMatches } from "@/lib/metric11-data";
import { sendTelegramMessage } from "@/lib/telegram";

// Haftada 1 kez (bkz. vercel.json cron'u) Telegram kanalına o haftanın maçlarını ve
// modelin en net gördüğü maçı CTA linkiyle birlikte paylaşır — kanaldan tahmin.metric11.com'a
// gerçek kullanıcı çekmek için (bkz. PROJECT_STATE 2026-09-13). Haftalık kadans yeterli
// olduğu için (ve dedup için ayrı bir DB tablosu gerektirmemek adına) günlük değil,
// sabit bir günde (Perşembe) çalışıyor — ligin bu sezonki fikstüründe haftalar en erken
// Perşembe başlıyor, o yüzden bu saat neredeyse hep ilk maçtan önce denk geliyor.
export async function GET(req: Request) {
  const authHeader = req.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new NextResponse("Unauthorized", { status: 401 });
  }

  const matches = await getUpcomingMatches();
  if (matches.length === 0) {
    return NextResponse.json({ sent: false, reason: "no_upcoming_matches" });
  }

  const week = matches[0].week;
  const highlight = [...matches].sort((a, b) => {
    const confA = Math.max(a.home_win_probability, a.draw_probability, a.away_win_probability);
    const confB = Math.max(b.home_win_probability, b.draw_probability, b.away_win_probability);
    return confB - confA;
  })[0];

  const maxProb = Math.max(
    highlight.home_win_probability,
    highlight.draw_probability,
    highlight.away_win_probability
  );
  const highlightPct = Math.round(maxProb * 100);
  const highlightPick =
    highlight.home_win_probability === maxProb
      ? `${highlight.home_team} galibiyeti`
      : highlight.away_win_probability === maxProb
        ? `${highlight.away_team} galibiyeti`
        : "beraberlik";

  const lines = [
    `⚽ <b>Hafta ${week} başlıyor</b> — ${matches.length} maç var.`,
    ``,
    `Modelin en net gördüğü maç: <b>${highlight.home_team} - ${highlight.away_team}</b> → %${highlightPct} ${highlightPick} (önerilen skor ${highlight.recommended_scoreline.score}).`,
    ``,
    `Bu haftaki tüm maçlar için tahminini gir, arkadaşlarınla yarış:`,
    `https://tahmin.metric11.com/predictions?src=telegram`,
  ];

  await sendTelegramMessage(lines.join("\n"));
  return NextResponse.json({ sent: true, week, matchCount: matches.length, highlightMatchId: highlight.match_id });
}
