"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Sparkles, Loader2, Terminal } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { useEffect } from "react";

export default function CreateProject() {
  const router = useRouter();
  
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    user_input: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const project = await apiClient.createProject(formData);
      
      // Start orchestration
      await apiClient.startOrchestration(project.id);
      
      // Redirect to orchestration view
      router.push(`/project/${project.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
      setIsLoading(false);
    }
  };

  const examplePrompts = [
    {
      title: "Social Network",
      description: "A social platform for developers to share code snippets and collaborate",
    },
    {
      title: "Task Manager",
      description: "A productivity app with kanban boards, time tracking, and team collaboration",
    },
    {
      title: "E-commerce Store",
      description: "An online marketplace with product listings, cart, and payment integration",
    },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/30">
      {/* Header */}
      <header className="border-b border-border bg-background/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 text-muted-foreground hover:text-primary transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-mono text-sm">Back</span>
          </Link>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-primary" />
            <span className="text-xl font-bold tracking-tighter">
              OrkestrAI
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-4xl relative">
        {/* Background Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/10 rounded-full blur-[120px] pointer-events-none -z-10" />

        <div className="space-y-8">
          {/* Header */}
          <div className="space-y-2 border-l-2 border-primary pl-4">
            <h1 className="text-4xl font-bold flex items-center space-x-3">
              <Terminal className="w-8 h-8 text-primary" />
              <span>Initialize Project</span>
            </h1>
            <p className="text-muted-foreground max-w-2xl text-lg">
              Define the core parameters for your new orchestration environment. The AI agent swarm will configure resources based on these inputs.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="glass-panel rounded-xl p-8 space-y-6 shadow-2xl">
              {/* Project Name */}
              <div className="space-y-2">
                <label htmlFor="name" className="font-mono text-sm text-muted-foreground block uppercase tracking-wider">
                  Project Identity
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-surface border border-border text-foreground font-mono text-sm rounded-md px-4 py-3 placeholder-muted transition-all neon-focus focus:ring-0"
                  placeholder="e.g., Nexus-Core-Alpha"
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <label htmlFor="description" className="font-mono text-sm text-muted-foreground block uppercase tracking-wider">
                  Brief Description (Optional)
                </label>
                <input
                  id="description"
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-surface border border-border text-foreground rounded-md px-4 py-3 placeholder-muted transition-all neon-focus focus:ring-0"
                  placeholder="A brief one-line description"
                />
              </div>

              {/* User Input */}
              <div className="space-y-2">
                <label htmlFor="user_input" className="font-mono text-sm text-muted-foreground block uppercase tracking-wider">
                  Operational Directives
                </label>
                <textarea
                  id="user_input"
                  required
                  value={formData.user_input}
                  onChange={(e) => setFormData({ ...formData, user_input: e.target.value })}
                  className="w-full bg-surface border border-border text-foreground rounded-md px-4 py-3 placeholder-muted transition-all neon-focus focus:ring-0 resize-y min-h-[150px]"
                  placeholder="Describe the primary goal, architecture needs, and data flows..."
                />
                <div className="flex justify-between items-center text-muted-foreground font-mono text-xs">
                  <span>
                    {formData.user_input.length} characters
                  </span>
                  <span>
                    Be specific and detailed
                  </span>
                </div>
              </div>
            </div>

            {/* Example Prompts */}
            <div className="space-y-3">
              <span className="font-mono text-sm text-muted-foreground uppercase tracking-wider px-1">
                Or Select a Blueprint Template
              </span>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {examplePrompts.map((prompt, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setFormData({ ...formData, name: prompt.title, user_input: prompt.description })}
                    className="text-left bg-surface/50 hover:bg-surface border border-border hover:border-primary/50 rounded-lg p-4 transition-all group shadow-sm hover:shadow-[0_0_15px_rgba(0,212,255,0.1)]"
                  >
                    <h3 className="font-bold text-foreground mb-2 group-hover:text-primary transition-colors">
                      {prompt.title}
                    </h3>
                    <p className="text-muted-foreground text-sm">
                      {prompt.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-error/10 border border-error/30 rounded-md p-4 flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-error animate-pulse" />
                <p className="text-error font-mono text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-6 flex justify-end">
              <button
                type="submit"
                disabled={isLoading || !formData.name || !formData.user_input}
                className="bg-primary text-background font-bold py-3 px-8 rounded-md flex items-center space-x-2 hover:bg-primary-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(0,212,255,0.3)] hover:shadow-[0_0_25px_rgba(0,212,255,0.5)]"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Deploying Swarm...</span>
                  </>
                ) : (
                  <>
                    <span>Start Orchestration</span>
                    <Terminal className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

// Made with Bob
