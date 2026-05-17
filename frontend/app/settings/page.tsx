"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, GitBranch, Settings, Loader2, CheckCircle2, AlertCircle, Trash2, Key, Cpu, Sparkles, Zap, Globe } from "lucide-react";
import { apiClient } from "@/lib/api/client";

export default function SettingsPage() {
  const router = useRouter();
  const [keys, setKeys] = useState({
    github_token: "",
    openai_key: "",
    gemini_key: "",
    groq_key: "",
    openrouter_key: "",
    bob_key: ""
  });
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState<string | null>(null);
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

  const handleUpdateKey = async (fieldName: string) => {
    const value = (keys as any)[fieldName];
    if (!value) return;

    setIsSaving(fieldName);
    setMessage(null);
    try {
      const response = await apiClient.request<any>("/api/v1/auth/keys", {
        method: "POST",
        body: JSON.stringify({ [fieldName]: value })
      });
      setMessage({ text: `${fieldName.replace('_', ' ').toUpperCase()} updated successfully!`, type: 'success' });
      setKeys({ ...keys, [fieldName]: "" });
      setUser(response);
    } catch (err: any) {
      setMessage({ text: err.message || "Failed to update key", type: 'error' });
    } finally {
      setIsSaving(null);
    }
  };

  const handleRemoveKey = async (fieldName: string) => {
    if (!confirm(`Are you sure you want to remove this credential?`)) return;
    setIsSaving(fieldName);
    try {
      const response = await apiClient.request<any>("/api/v1/auth/keys", {
        method: "POST",
        body: JSON.stringify({ [fieldName]: "" })
      });
      setUser(response);
      setMessage({ text: "Credential removed", type: 'success' });
    } catch (err: any) {
      setMessage({ text: err.message || "Failed to remove credential", type: 'error' });
    } finally {
      setIsSaving(null);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }

  const sections = [
    { id: 'github_token', label: 'GitHub Personal Access Token', icon: GitBranch, hasKey: user?.has_github_token, placeholder: 'ghp_xxxxxxxxxxxx', color: 'text-success' },
    { id: 'openai_key', label: 'OpenAI API Key', icon: Sparkles, hasKey: user?.has_openai_key, placeholder: 'sk-xxxxxxxxxxxx', color: 'text-primary' },
    { id: 'gemini_key', label: 'Google Gemini API Key', icon: Zap, hasKey: user?.has_gemini_key, placeholder: 'AIzaSyxxxxxxxxxxxx', color: 'text-secondary' },
    { id: 'groq_key', label: 'Groq API Key', icon: Cpu, hasKey: user?.has_groq_key, placeholder: 'gsk_xxxxxxxxxxxx', color: 'text-warning' },
    { id: 'openrouter_key', label: 'OpenRouter API Key', icon: Globe, hasKey: user?.has_openrouter_key, placeholder: 'sk-or-xxxxxxxxxxxx', color: 'text-error' },
    { id: 'bob_key', label: 'Bob AI API Key', icon: Zap, hasKey: user?.has_bob_key, placeholder: 'bob_xxxxxxxxxxxx', color: 'text-primary' },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-background/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 text-muted-foreground hover:text-primary transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-mono text-sm font-bold">Back to Dashboard</span>
          </Link>
          <h1 className="text-xl font-bold tracking-tighter flex items-center space-x-2">
            <Settings className="w-5 h-5 text-primary" />
            <span>System Settings</span>
          </h1>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-3xl">
        <div className="space-y-8">
          <div>
            <h2 className="text-3xl font-bold mb-2">API Credentials</h2>
            <p className="text-muted-foreground">Manage your AI provider keys and platform tokens. These are used directly to power your swarm orchestrations.</p>
          </div>

          {message && (
            <div className={`p-4 rounded-xl border flex items-center space-x-3 sticky top-20 z-40 animate-in fade-in slide-in-from-top-4 ${
              message.type === 'success' ? 'bg-success/10 border-success/30 text-success' : 'bg-error/10 border-error/30 text-error'
            }`}>
              {message.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
              <span className="font-mono text-sm font-bold">{message.text}</span>
            </div>
          )}

          <div className="grid gap-6">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <div key={section.id} className="glass-panel p-6 rounded-2xl border border-border space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`p-3 rounded-xl ${section.hasKey ? 'bg-success/10 ' + section.color : 'bg-muted/10 text-muted-foreground'}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold">{section.label}</h3>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {section.hasKey ? "✓ Credential active and ready for use." : "Not configured."}
                        </p>
                      </div>
                    </div>
                    {section.hasKey && (
                      <button 
                        onClick={() => handleRemoveKey(section.id)}
                        className="p-2 text-muted-foreground hover:text-error transition-colors bg-surface border border-border rounded-lg"
                        title="Remove key"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="flex space-x-3 pt-2">
                    <div className="relative flex-1">
                      <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <input
                        type="password"
                        placeholder={section.placeholder}
                        value={(keys as any)[section.id]}
                        onChange={(e) => setKeys({ ...keys, [section.id]: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 bg-background border border-border rounded-xl focus:ring-2 focus:ring-primary outline-none transition-all font-mono text-sm"
                      />
                    </div>
                    <button
                      onClick={() => handleUpdateKey(section.id)}
                      disabled={isSaving !== null || !(keys as any)[section.id]}
                      className="px-6 bg-primary text-background rounded-xl font-bold hover:bg-primary-hover transition-all disabled:opacity-50 flex items-center justify-center min-w-[120px]"
                    >
                      {isSaving === section.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>Update</span>}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="p-6 bg-surface/30 border border-border rounded-2xl">
            <h4 className="text-sm font-bold flex items-center space-x-2 text-muted-foreground mb-2">
              <Zap className="w-4 h-4" />
              <span>Usage Note</span>
            </h4>
            <p className="text-xs text-muted-foreground leading-relaxed">
              OrkestrAI now uses your personal API tokens exclusively. This gives you full control over your usage and costs. Tokens are encrypted at rest and never shared with third parties other than the specified AI provider.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
