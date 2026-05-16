"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, GitBranch, ShieldCheck, Loader2, CheckCircle2, AlertCircle, Trash2, Key } from "lucide-react";
import { apiClient } from "@/lib/api/client";

export default function SettingsPage() {
  const router = useRouter();
  const [githubToken, setGithubToken] = useState("");
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const profile = await apiClient.request<any>("/api/v1/auth/me");
        setUser(profile);
      } catch (err) {
        console.error("Failed to fetch profile", err);
        router.push("/login");
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfile();
  }, [router]);

  const handleUpdateToken = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage(null);
    try {
      await apiClient.request("/api/v1/auth/github-token", {
        method: "POST",
        body: JSON.stringify({ github_token: githubToken })
      });
      setMessage({ text: "GitHub token updated successfully!", type: 'success' });
      setGithubToken("");
      setUser({ ...user, has_github_token: true });
    } catch (err: any) {
      setMessage({ text: err.message || "Failed to update token", type: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm("Are you sure you want to disconnect your GitHub account?")) return;
    setIsSaving(true);
    try {
      await apiClient.request("/api/v1/auth/github-token", { method: "DELETE" });
      setUser({ ...user, has_github_token: false });
      setMessage({ text: "GitHub account disconnected", type: 'success' });
    } catch (err: any) {
      setMessage({ text: err.message || "Failed to disconnect", type: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-background/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 text-muted-foreground hover:text-primary transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-mono text-sm font-bold">Back to Dashboard</span>
          </Link>
          <h1 className="text-xl font-bold tracking-tighter">System Settings</h1>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-2xl">
        <div className="space-y-8">
          <div>
            <h2 className="text-3xl font-bold flex items-center space-x-3 mb-2">
              <ShieldCheck className="w-8 h-8 text-primary" />
              <span>Integrations</span>
            </h2>
            <p className="text-muted-foreground">Manage your third-party API credentials and platform connections.</p>
          </div>

          {message && (
            <div className={`p-4 rounded-xl border flex items-center space-x-3 ${
              message.type === 'success' ? 'bg-success/10 border-success/30 text-success' : 'bg-error/10 border-error/30 text-error'
            }`}>
              {message.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
              <span className="font-mono text-sm font-bold">{message.text}</span>
            </div>
          )}

          <div className="glass-panel p-8 rounded-3xl border border-border space-y-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-2xl ${user?.has_github_token ? 'bg-success/10 text-success' : 'bg-muted/10 text-muted-foreground'}`}>
                  <GitBranch className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">GitHub Personal Access Token</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {user?.has_github_token 
                      ? "✓ Account connected. Tokens are used to create repos and push code." 
                      : "Not connected. Projects will skip repository creation."}
                  </p>
                </div>
              </div>
              {user?.has_github_token && (
                <button 
                  onClick={handleDisconnect}
                  className="p-2 text-muted-foreground hover:text-error transition-colors bg-surface border border-border rounded-lg"
                  title="Disconnect account"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              )}
            </div>

            <form onSubmit={handleUpdateToken} className="space-y-4 pt-4 border-t border-border/50">
              <div className="space-y-2">
                <label className="text-xs font-mono text-muted-foreground uppercase tracking-widest block pl-1">
                  New Personal Access Token (PAT)
                </label>
                <div className="relative">
                  <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="password"
                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                    value={githubToken}
                    onChange={(e) => setGithubToken(e.target.value)}
                    required
                    className="w-full pl-10 pr-4 py-3 bg-background border border-border rounded-xl focus:ring-2 focus:ring-primary outline-none transition-all font-mono text-sm"
                  />
                </div>
                <p className="text-[10px] text-muted-foreground pl-1 italic">
                  Tokens are stored securely in your private profile. Required scopes: <code className="text-primary">repo</code>, <code className="text-primary">workflow</code>.
                </p>
              </div>

              <button
                type="submit"
                disabled={isSaving || !githubToken}
                className="w-full py-4 bg-primary text-background rounded-xl font-bold hover:bg-primary-hover transition-all disabled:opacity-50 flex items-center justify-center space-x-2 shadow-[0_0_20px_rgba(0,212,255,0.3)]"
              >
                {isSaving ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Update GitHub Credential</span>}
              </button>
            </form>
          </div>

          <div className="p-6 bg-surface/30 border border-border rounded-2xl">
            <h4 className="text-sm font-bold flex items-center space-x-2 text-muted-foreground mb-2">
              <ShieldCheck className="w-4 h-4" />
              <span>Security Note</span>
            </h4>
            <p className="text-xs text-muted-foreground leading-relaxed">
              OrkestrAI uses your tokens exclusively for creating the project repository and pushing the initial codebase. We never store your tokens in clear text in logs or environment files. You can revoke access at any time through this dashboard or your GitHub settings.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
