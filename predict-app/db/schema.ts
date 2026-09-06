import { pgTable, serial, text, integer, timestamp, uniqueIndex } from "drizzle-orm/pg-core";

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
