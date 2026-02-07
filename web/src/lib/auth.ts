import { betterAuth, BetterAuthOptions } from "better-auth";
import { getMigrations } from "better-auth/db";

// Conditional database: PostgreSQL in production, SQLite in development
// Uses require() for runtime-conditional imports based on DATABASE_URL
function getDatabase() {
  const databaseUrl = process.env.DATABASE_URL;

  // PostgreSQL if DATABASE_URL starts with postgres
  if (databaseUrl?.startsWith("postgres")) {
    const { Pool } = require("pg"); // eslint-disable-line @typescript-eslint/no-require-imports
    return new Pool({ connectionString: databaseUrl });
  }

  // During Vercel build (no DATABASE_URL), use in-memory SQLite to pass build
  // Runtime will have DATABASE_URL set properly
  if (process.env.VERCEL && !databaseUrl) {
    const Database = require("better-sqlite3"); // eslint-disable-line @typescript-eslint/no-require-imports
    return new Database(":memory:");
  }

  // SQLite for local development
  const Database = require("better-sqlite3"); // eslint-disable-line @typescript-eslint/no-require-imports
  const path = require("path"); // eslint-disable-line @typescript-eslint/no-require-imports
  const dbPath = process.env.DATABASE_PATH || path.join(process.cwd(), "../data/jobs.db");
  return new Database(dbPath);
}

const db = getDatabase();

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
  user: {
    deleteUser: {
      enabled: true,
      beforeDelete: async (user) => {
        // GDPR: Delete all user's jobs before deleting account
        // Uses same database connection as Better Auth
        if ("run" in db) {
          // SQLite (better-sqlite3)
          db.prepare("DELETE FROM jobs WHERE user_id = ?").run(user.id);
        } else {
          // PostgreSQL (pg Pool)
          await db.query("DELETE FROM jobs WHERE user_id = $1", [user.id]);
        }
      },
    },
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
