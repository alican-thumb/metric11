import { NextResponse } from "next/server";
import { syncFinishedResults } from "@/lib/sync-results";

export async function GET(req: Request) {
  const authHeader = req.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new NextResponse("Unauthorized", { status: 401 });
  }
  const result = await syncFinishedResults();
  return NextResponse.json(result);
}
