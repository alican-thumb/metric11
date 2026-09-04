import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import * as schema from "./schema";

// Lazy init — DATABASE_URL is only injected once the Neon Marketplace integration is
// provisioned. A module-scope `neon()` call would crash `next build` before that.
// Do NOT wrap this in a JS Proxy (breaks libraries that introspect the client object).
let _db: ReturnType<typeof drizzle<typeof schema>> | null = null;

export function getDb() {
  if (!_db) {
    const sql = neon(process.env.DATABASE_URL!);
    _db = drizzle(sql, { schema });
  }
  return _db;
}
