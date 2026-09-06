import { randomBytes } from "crypto";

// Karışabilecek karakterler (0/O, 1/I/L) çıkarıldı — kullanıcılar kodu elle
// paylaşıp yazacak (Telegram/WhatsApp), okurken hata payını azaltır.
const ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";

export function generateInviteCode(length = 6): string {
  const bytes = randomBytes(length);
  let code = "";
  for (let i = 0; i < length; i++) {
    code += ALPHABET[bytes[i] % ALPHABET.length];
  }
  return code;
}
