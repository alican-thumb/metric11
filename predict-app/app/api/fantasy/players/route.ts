import { NextResponse } from "next/server";
import { getPlayerPool } from "@/lib/fantasy-data";

// İstemci tarafı (kadro kurma/transfer ekranları) metric11.com'a doğrudan fetch
// ATMAZ (CORS + gereksiz büyük payload tekrar önbellekleme) — bu route sunucu
// tarafındaki modül-seviyeli önbelleği (bkz. lib/fantasy-data.ts) reuse eder.
export async function GET() {
  const pool = await getPlayerPool();
  return NextResponse.json(pool);
}
