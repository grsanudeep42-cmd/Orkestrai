"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api/client";
import { Loader2, Lock, User, RefreshCw, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [captchaAnswer, setCaptchaAnswer] = useState("");
  const [captcha, setCaptcha] = useState<{ id: string; question: string } | null>(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCaptcha = async () => {
    try {
      const data = await apiClient.getCaptcha();
      setCaptcha(data);
    } catch (err) {
      console.error("Failed to fetch captcha", err);
    }
  };

  useEffect(() => {
    fetchCaptcha();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!captcha) return;
    
    setIsLoading(true);
    setError(null);

    try {
      await apiClient.login({
        username,
        password,
        captcha_id: captcha.id,
        captcha_answer: parseInt(captchaAnswer)
      });
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to login");
      fetchCaptcha(); // Refresh captcha on failure
      setCaptchaAnswer("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-md space-y-8 bg-surface p-8 rounded-2xl border border-border shadow-xl">
        <div className="text-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-success bg-clip-text text-transparent">
            OrkestrAI Login
          </h1>
          <p className="mt-2 text-muted-foreground">Access your project swarm</p>
        </div>

        {error && (
          <div className="p-4 bg-error/10 border border-error/20 rounded-lg text-error text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary outline-none transition-all font-mono"
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary outline-none transition-all font-mono"
              />
            </div>
          </div>

          {/* Captcha Section */}
          <div className="p-4 bg-muted/5 border border-border rounded-lg space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-sm text-primary font-bold">
                <ShieldCheck className="w-4 h-4" />
                <span>Verification</span>
              </div>
              <button 
                type="button" 
                onClick={fetchCaptcha}
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            <p className="text-lg font-bold font-mono text-center">
              {captcha?.question || "..."}
            </p>
            <input
              type="number"
              placeholder="Answer"
              value={captchaAnswer}
              onChange={(e) => setCaptchaAnswer(e.target.value)}
              required
              className="w-full px-4 py-2 bg-background border border-border rounded-lg text-center font-bold text-lg outline-none focus:border-primary transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !captcha}
            className="w-full py-4 bg-primary text-background rounded-xl font-bold hover:bg-primary-hover transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Login to Dashboard</span>}
          </button>
        </form>

        <div className="text-center text-sm">
          <span className="text-muted-foreground">Don't have an account? </span>
          <Link href="/signup" className="text-primary hover:underline font-bold">
            Sign up now
          </Link>
        </div>
      </div>
    </div>
  );
}
