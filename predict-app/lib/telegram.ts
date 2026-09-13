const TELEGRAM_API = "https://api.telegram.org";

// Ana repo'daki Python botuyla aynı Telegram kanalı — bot token/kanal ID'si zaten
// GitHub Actions secret'ı olarak var, burada Vercel env değişkeni olarak ayrıca
// tanımlanması gerekiyor (iki sistem farklı ortamlarda çalıştığı için paylaşılmıyor).
export async function sendTelegramMessage(text: string): Promise<void> {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHANNEL_ID;
  if (!token || !chatId) {
    throw new Error("TELEGRAM_BOT_TOKEN veya TELEGRAM_CHANNEL_ID tanımlı değil.");
  }

  const res = await fetch(`${TELEGRAM_API}/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      parse_mode: "HTML",
    }),
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Telegram sendMessage başarısız: HTTP ${res.status} ${body}`);
  }
}
