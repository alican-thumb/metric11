import { pgTable, serial, text, integer, timestamp, uniqueIndex, boolean } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  clerkUserId: text("clerk_user_id").notNull(),
  displayName: text("display_name").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  // Ardışık doğru tahmin sayısı (sync-results.ts'de maç kickoff sırasına göre güncellenir).
  // pointsEarned > 0 (en az yön doğru) bir isabet sayılır; bir kaçırma sıfırlar.
  currentStreak: integer("current_streak").notNull().default(0),
  bestStreak: integer("best_streak").notNull().default(0),
}, (table) => ({
  clerkUserIdIdx: uniqueIndex("users_clerk_user_id_idx").on(table.clerkUserId),
  displayNameIdx: uniqueIndex("users_display_name_idx").on(table.displayName),
}));

export const predictions = pgTable("predictions", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  matchId: text("match_id").notNull(),
  predictedHome: integer("predicted_home").notNull(),
  predictedAway: integer("predicted_away").notNull(),
  submittedAt: timestamp("submitted_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  pointsEarned: integer("points_earned"),
  // Skorlama anındaki seri bonusu (bkz. lib/scoring.ts::computeStreakBonus) — pointsEarned'dan
  // ayrı tutulur ki puanlama kuralının kendisi (1X2/fark/skor) hiç bulanıklaşmasın.
  streakBonus: integer("streak_bonus").notNull().default(0),
}, (table) => ({
  userMatchIdx: uniqueIndex("predictions_user_match_idx").on(table.userId, table.matchId),
}));

export const badges = pgTable("badges", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  code: text("code").notNull(),
  earnedAt: timestamp("earned_at", { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  userCodeIdx: uniqueIndex("badges_user_code_idx").on(table.userId, table.code),
}));

export const groups = pgTable("groups", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  inviteCode: text("invite_code").notNull(),
  createdBy: integer("created_by").notNull().references(() => users.id),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  inviteCodeIdx: uniqueIndex("groups_invite_code_idx").on(table.inviteCode),
}));

export const groupMembers = pgTable("group_members", {
  id: serial("id").primaryKey(),
  groupId: integer("group_id").notNull().references(() => groups.id),
  userId: integer("user_id").notNull().references(() => users.id),
  joinedAt: timestamp("joined_at", { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  groupUserIdx: uniqueIndex("group_members_group_user_idx").on(table.groupId, table.userId),
}));

// --- Kadro Kur (Fantasy Manager) ---
// Oyuncu kimliği her yerde `transfermarkt_id` (text) — kaynak metric11.com'daki
// fantasy_player_pool_2026_2027.json'dan gelir, DB'de ayrı bir players tablosu YOK
// (metric11-data.ts'deki fixture verisiyle aynı desen: canlı JSON tek gerçek kaynak).

export const fantasySquads = pgTable("fantasy_squads", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  // Bu hafta kaç ücretsiz transfer kaldı (haftada 1 ile sıfırlanır, bkz. lib/fantasy-transfers.ts);
  // fazlası -4 puan cezası.
  freeTransfers: integer("free_transfers").notNull().default(1),
  // Ücretsiz transfer sayacının hangi haftaya ait olduğu — yeni hafta algılandığında sıfırlanır.
  transfersWeek: integer("transfers_week"),
}, (table) => ({
  userIdIdx: uniqueIndex("fantasy_squads_user_id_idx").on(table.userId),
}));

export const fantasySquadPlayers = pgTable("fantasy_squad_players", {
  id: serial("id").primaryKey(),
  squadId: integer("squad_id").notNull().references(() => fantasySquads.id),
  transfermarktId: text("transfermarkt_id").notNull(),
  addedAt: timestamp("added_at", { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  squadPlayerIdx: uniqueIndex("fantasy_squad_players_squad_player_idx").on(table.squadId, table.transfermarktId),
}));

// Haftalık ilk 11 + kaptan seçimi — kullanıcı kaydetmezse bir önceki haftanın seçimi
// UI'da ön dolu gösterilir (bkz. app/kadro/hafta), ama puanlama yalnızca bu tabloda o
// hafta için GERÇEKTEN kaydedilmiş bir satır varsa yapılır.
export const fantasyGameweekLineups = pgTable("fantasy_gameweek_lineups", {
  id: serial("id").primaryKey(),
  squadId: integer("squad_id").notNull().references(() => fantasySquads.id),
  week: integer("week").notNull(),
  transfermarktId: text("transfermarkt_id").notNull(),
  isStarting: boolean("is_starting").notNull().default(false),
  isCaptain: boolean("is_captain").notNull().default(false),
  isViceCaptain: boolean("is_vice_captain").notNull().default(false),
  // NULL = maçı henüz oynanmadı/puanlanmadı (bkz. lib/sync-fantasy-results.ts); kaptan
  // çarpanı burada DEĞİL, toplama/leaderboard sorgusunda uygulanır (scoring.ts ile aynı
  // ayrıştırma ilkesi — ham oyuncu puanı hiç bulanıklaşmasın).
  points: integer("points"),
}, (table) => ({
  lineupIdx: uniqueIndex("fantasy_gameweek_lineups_idx").on(table.squadId, table.week, table.transfermarktId),
}));

// Transfer cezası denetimi/şeffaflığı için log — free transfer sayacı fantasySquads'ta
// tutulur, bu tablo yalnızca "hangi hafta ne oldu"yu gösterebilmek içindir.
export const fantasyTransferLog = pgTable("fantasy_transfer_log", {
  id: serial("id").primaryKey(),
  squadId: integer("squad_id").notNull().references(() => fantasySquads.id),
  week: integer("week").notNull(),
  playerOutId: text("player_out_id").notNull(),
  playerInId: text("player_in_id").notNull(),
  penalized: boolean("penalized").notNull().default(false),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

// --- Taraftar Sayacı (Fan Counter) ---
// memleket.lol'un tekrar-tıklanabilir/anonim oy savaşı YERİNE: hesap başına tek satır
// (istenirse değiştirilebilir) bir takım seçimi — "kaç kullanıcı bu takımı destekliyor"
// anlamına gelsin diye, spam/bot riskini de ortadan kaldırsın diye böyle tasarlandı.
export const fanPicks = pgTable("fan_picks", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull().references(() => users.id),
  team: text("team").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
  userIdIdx: uniqueIndex("fan_picks_user_id_idx").on(table.userId),
}));
