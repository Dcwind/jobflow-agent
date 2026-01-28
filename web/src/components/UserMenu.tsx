"use client";

import { useSession, signOut } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function UserMenu() {
  const { data: session, isPending } = useSession();

  if (isPending) {
    return (
      <div className="h-9 w-20 bg-gray-100 animate-pulse rounded-md" />
    );
  }

  if (!session?.user) {
    return (
      <Link href="/signin">
        <Button variant="outline" size="sm">
          Sign in
        </Button>
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600">
        {session.user.email}
      </span>
      <Button
        variant="outline"
        size="sm"
        onClick={() => signOut()}
      >
        Sign out
      </Button>
    </div>
  );
}
