"use client";

import { useState, useEffect } from "react";
import { useSession, deleteUser } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function AccountPage() {
  const { data: session, isPending } = useSession();
  const [isDeleting, setIsDeleting] = useState(false);
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [keySaving, setKeySaving] = useState(false);
  const [keyMessage, setKeyMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((data) => setHasGeminiKey(data.has_gemini_key ?? false))
      .catch(() => {});
  }, []);

  const handleSaveKey = async () => {
    if (!apiKeyInput.trim()) return;
    setKeySaving(true);
    setKeyMessage(null);
    try {
      const res = await fetch("/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gemini_api_key: apiKeyInput.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        setKeyMessage({ type: "error", text: data.detail || "Failed to save key" });
        return;
      }
      setHasGeminiKey(true);
      setApiKeyInput("");
      setKeyMessage({ type: "success", text: "API key saved and verified." });
    } catch {
      setKeyMessage({ type: "error", text: "Failed to save key" });
    } finally {
      setKeySaving(false);
    }
  };

  const handleRemoveKey = async () => {
    setKeySaving(true);
    setKeyMessage(null);
    try {
      await fetch("/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gemini_api_key: null }),
      });
      setHasGeminiKey(false);
      setKeyMessage({ type: "success", text: "API key removed." });
    } catch {
      setKeyMessage({ type: "error", text: "Failed to remove key" });
    } finally {
      setKeySaving(false);
    }
  };

  if (isPending) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!session?.user) {
    router.push("/signin");
    return null;
  }

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete your account?\n\nThis will permanently delete:\n- Your account\n- All your saved jobs\n\nThis action cannot be undone."
    );
    if (!confirmed) return;

    // Double confirmation for destructive action
    const doubleConfirmed = window.confirm(
      "This is your final warning. All data will be permanently deleted. Continue?"
    );
    if (!doubleConfirmed) return;

    setIsDeleting(true);
    try {
      await deleteUser();
      window.location.href = "/signin";
    } catch (error) {
      console.error("Failed to delete account:", error);
      alert("Failed to delete account. Please try again.");
      setIsDeleting(false);
    }
  };

  return (
    <main className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline text-sm">
          &larr; Back to Jobs
        </Link>
      </div>

      <h1 className="text-2xl font-bold mb-8">Account Settings</h1>

      <div className="space-y-6">
        {/* Account Info */}
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>Your account information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Name</label>
              <p className="text-gray-900">{session.user.name || "Not set"}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Email</label>
              <p className="text-gray-900">{session.user.email}</p>
            </div>
          </CardContent>
        </Card>

        {/* Data Export */}
        <Card>
          <CardHeader>
            <CardTitle>Your Data</CardTitle>
            <CardDescription>Export or manage your data</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              You can export all your saved jobs as a CSV file from the main dashboard
              using the &quot;Export CSV&quot; button.
            </p>
            <Link href="/">
              <Button variant="outline">Go to Dashboard</Button>
            </Link>
          </CardContent>
        </Card>

        {/* API Key */}
        <Card>
          <CardHeader>
            <CardTitle>Gemini API Key</CardTitle>
            <CardDescription>
              Bring your own key to use AI-powered extraction without limits.
              Your key is encrypted at rest and never shared.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {hasGeminiKey ? (
              <div className="flex items-center justify-between">
                <p className="text-sm text-green-700">
                  Key saved — AI extraction uses your key.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRemoveKey}
                  disabled={keySaving}
                >
                  {keySaving ? "Removing..." : "Remove key"}
                </Button>
              </div>
            ) : (
              <div className="flex gap-2">
                <Input
                  type="password"
                  placeholder="AIzaSy..."
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  disabled={keySaving}
                  className="flex-1"
                />
                <Button
                  onClick={handleSaveKey}
                  disabled={keySaving || !apiKeyInput.trim()}
                >
                  {keySaving ? "Verifying..." : "Save key"}
                </Button>
              </div>
            )}
            {keyMessage && (
              <p className={`text-sm ${keyMessage.type === "error" ? "text-red-600" : "text-green-600"}`}>
                {keyMessage.text}
              </p>
            )}
            <p className="text-xs text-gray-500">
              Get a free API key from{" "}
              <a
                href="https://aistudio.google.com/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                Google AI Studio
              </a>
            </p>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">Danger Zone</CardTitle>
            <CardDescription>Irreversible actions</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Deleting your account will permanently remove all your data, including
              your saved jobs. This action cannot be undone.
            </p>
            <Button
              variant="destructive"
              onClick={handleDeleteAccount}
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting..." : "Delete Account"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
