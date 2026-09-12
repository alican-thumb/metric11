import { NextResponse } from "next/server";
import { syncFantasyResults } from "@/lib/sync-fantasy-results";

export async function GET(req: Request) {
  const authHeader = req.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new NextResponse("Unauthorized", { status: 401 });
  }
  const result = await syncFantasyResults();
  return NextResponse.json(result);
}
