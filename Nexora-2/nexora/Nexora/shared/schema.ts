import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, boolean, timestamp, decimal } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const msmeBusinesses = pgTable("msme_businesses", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").references(() => users.id),
  businessName: text("business_name").notNull(),
  registrationNumber: text("registration_number").notNull(),
  businessType: text("business_type").notNull(),
  category: text("category").notNull(),
  establishedYear: integer("established_year"),
  location: text("location"),
  employees: integer("employees"),
  annualRevenue: decimal("annual_revenue"),
  walletAddress: text("wallet_address"),
  creditScore: integer("credit_score").default(0),
  isVerified: boolean("is_verified").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

export const loans = pgTable("loans", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  businessId: varchar("business_id").references(() => msmeBusinesses.id),
  lenderName: text("lender_name").notNull(),
  amount: decimal("amount").notNull(),
  interestRate: decimal("interest_rate").notNull(),
  tenure: integer("tenure").notNull(),
  status: text("status").notNull().default("active"),
  disbursedAmount: decimal("disbursed_amount").default("0"),
  repaidAmount: decimal("repaid_amount").default("0"),
  contractAddress: text("contract_address"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const products = pgTable("products", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  businessId: varchar("business_id").references(() => msmeBusinesses.id),
  name: text("name").notNull(),
  description: text("description"),
  category: text("category").notNull(),
  price: decimal("price").notNull(),
  minOrder: integer("min_order").default(1),
  stock: integer("stock").default(0),
  imageUrl: text("image_url"),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
});

export const invoices = pgTable("invoices", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  businessId: varchar("business_id").references(() => msmeBusinesses.id),
  invoiceNumber: text("invoice_number").notNull(),
  amount: decimal("amount").notNull(),
  clientName: text("client_name").notNull(),
  dueDate: timestamp("due_date"),
  status: text("status").notNull().default("pending"),
  isVerified: boolean("is_verified").default(false),
  blockchainTxHash: text("blockchain_tx_hash"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const badges = pgTable("badges", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  businessId: varchar("business_id").references(() => msmeBusinesses.id),
  name: text("name").notNull(),
  description: text("description"),
  iconType: text("icon_type").notNull(),
  color: text("color").notNull(),
  earnedAt: timestamp("earned_at").defaultNow(),
});

// Insert schemas
export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertMsmeBusinessSchema = createInsertSchema(msmeBusinesses).omit({
  id: true,
  createdAt: true,
});

export const insertLoanSchema = createInsertSchema(loans).omit({
  id: true,
  createdAt: true,
});

export const insertProductSchema = createInsertSchema(products).omit({
  id: true,
  createdAt: true,
});

export const insertInvoiceSchema = createInsertSchema(invoices).omit({
  id: true,
  createdAt: true,
});

export const insertBadgeSchema = createInsertSchema(badges).omit({
  id: true,
  earnedAt: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type MsmeBusiness = typeof msmeBusinesses.$inferSelect;
export type InsertMsmeBusiness = z.infer<typeof insertMsmeBusinessSchema>;
export type Loan = typeof loans.$inferSelect;
export type InsertLoan = z.infer<typeof insertLoanSchema>;
export type Product = typeof products.$inferSelect;
export type InsertProduct = z.infer<typeof insertProductSchema>;
export type Invoice = typeof invoices.$inferSelect;
export type InsertInvoice = z.infer<typeof insertInvoiceSchema>;
export type Badge = typeof badges.$inferSelect;
export type InsertBadge = z.infer<typeof insertBadgeSchema>;