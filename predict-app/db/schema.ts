import { pgTable, serial, text, integer, timestamp, uniqueIndex } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  clerkUserId: text("clerk_user_id").notNull(),
  displayName: text("display_name").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
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
}, (table) => ({
  userMatchIdx: uniqueIndex("predictions_user_match_idx").on(table.userId, table.matchId),
}));
