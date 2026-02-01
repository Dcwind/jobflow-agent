import { betterAuth, BetterAuthOptions } from "better-auth";
import Database from "better-sqlite3";
import path from "path";
import { getMigrations } from "better-auth/db";

// Use shared database with FastAPI backend
const dbPath = process.env.DATABASE_PATH || path.join(process.cwd(), "../data/jobs.db");
const db = new Database(dbPath);

const options: BetterAuthOptions = {
  database: db,
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID || "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "",
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
  },
};

// Run migrations on startup (creates auth tables if missing)
const runMigrations = async () => {
  const { toBeCreated, runMigrations } = await getMigrations(options);
  if (toBeCreated.length > 0) {
    console.log("Running Better Auth migrations:", toBeCreated);
    await runMigrations();
  }
};
runMigrations().catch(console.error);

export const auth = betterAuth(options);
