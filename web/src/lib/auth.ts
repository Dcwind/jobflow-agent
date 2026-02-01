import { betterAuth, BetterAuthOptions } from "better-auth";
import { getMigrations } from "better-auth/db";

// Lazy database connection - only connect at runtime, not build time
function getDatabase() {
  const databaseUrl = process.env.DATABASE_URL;

  // PostgreSQL if DATABASE_URL starts with postgres
  if (databaseUrl?.startsWith("postgres")) {
    const { Pool } = require("pg");
    return new Pool({ connectionString: databaseUrl });
  }

  // SQLite for local development only
  const Database = require("better-sqlite3");
  const path = require("path");
  const dbPath = process.env.DATABASE_PATH || path.join(process.cwd(), "../data/jobs.db");
  return new Database(dbPath);
}

function getOptions(): BetterAuthOptions {
  return {
    database: getDatabase(),
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
}

// Lazy singleton - only initialize when first accessed
let _auth: ReturnType<typeof betterAuth> | null = null;

export const auth = new Proxy({} as ReturnType<typeof betterAuth>, {
  get(_, prop) {
    if (!_auth) {
      const options = getOptions();
      _auth = betterAuth(options);

      // Run migrations on first access
      getMigrations(options)
        .then(({ toBeCreated, runMigrations }) => {
          if (toBeCreated.length > 0) {
            console.log("Running Better Auth migrations:", toBeCreated);
            return runMigrations();
          }
        })
        .catch(console.error);
    }
    return (_auth as any)[prop];
  },
});
