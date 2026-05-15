"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Sparkles, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";

export default function CreateProject() {
  const router = useRouter();
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
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-outline-variant/30 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 text-on-surface-variant hover:text-primary transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-code-sm text-code-sm">Back</span>
          </Link>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-primary" />
            <span className="font-display-lg text-headline-md text-primary tracking-tighter">
              OrkestrAI
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-4xl">
        {/* Background Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/5 rounded-full blur-[120px] pointer-events-none -z-10" />

        <div className="space-y-8">
          {/* Header */}
          <div className="space-y-2">
            <h1 className="font-headline-md text-headline-md text-on-surface flex items-center space-x-3">
              <Sparkles className="w-8 h-8 text-primary" />
              <span>Initialize Project</span>
            </h1>
            <p className="font-body-base text-body-base text-on-surface-variant max-w-2xl">
              Define the core parameters for your new orchestration environment. The AI agent swarm will configure resources based on these inputs.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="glass-panel rounded-xl p-6 space-y-6">
              {/* Project Name */}
              <div className="space-y-2">
                <label htmlFor="name" className="font-label-caps text-label-caps text-on-surface-variant block uppercase tracking-wider">
                  Project Identity
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-surface-dim border border-outline-variant/50 text-on-surface font-code-sm text-code-sm rounded-lg px-4 py-3 placeholder-on-surface-variant/40 transition-all neon-focus focus:ring-0"
                  placeholder="e.g., Nexus-Core-Alpha"
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <label htmlFor="description" className="font-label-caps text-label-caps text-on-surface-variant block uppercase tracking-wider">
                  Brief Description (Optional)
                </label>
                <input
                  id="description"
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-surface-dim border border-outline-variant/50 text-on-surface font-body-base text-body-base rounded-lg px-4 py-3 placeholder-on-surface-variant/40 transition-all neon-focus focus:ring-0"
                  placeholder="A brief one-line description"
                />
              </div>

              {/* User Input */}
              <div className="space-y-2">
                <label htmlFor="user_input" className="font-label-caps text-label-caps text-on-surface-variant block uppercase tracking-wider">
                  Operational Directives
                </label>
                <textarea
                  id="user_input"
                  required
                  value={formData.user_input}
                  onChange={(e) => setFormData({ ...formData, user_input: e.target.value })}
                  className="w-full bg-surface-dim border border-outline-variant/50 text-on-surface font-body-base text-body-base rounded-lg px-4 py-3 placeholder-on-surface-variant/40 transition-all neon-focus focus:ring-0 resize-y min-h-[150px]"
                  placeholder="Describe the primary goal, architecture needs, and data flows..."
                />
                <div className="flex justify-between items-center">
                  <span className="font-code-sm text-code-sm text-on-surface-variant/70">
                    {formData.user_input.length} characters
                  </span>
                  <span className="font-code-sm text-code-sm text-on-surface-variant/70">
                    Be specific and detailed
                  </span>
                </div>
              </div>
            </div>

            {/* Example Prompts */}
            <div className="space-y-3">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider px-1">
                Or Select a Blueprint Template
              </span>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {examplePrompts.map((prompt, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setFormData({ ...formData, name: prompt.title, user_input: prompt.description })}
                    className="text-left bg-surface-container/40 hover:bg-surface-container border border-outline-variant/20 hover:border-primary/50 rounded-lg p-4 transition-all group"
                  >
                    <h3 className="font-code-sm text-code-sm text-on-surface font-semibold mb-2">
                      {prompt.title}
                    </h3>
                    <p className="font-body-base text-body-base text-on-surface-variant/80 group-hover:text-on-surface-variant transition-colors text-sm">
                      {prompt.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-error-container/20 border border-error/30 rounded-lg p-4">
                <p className="font-body-base text-body-base text-error">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-6 flex justify-end">
              <button
                type="submit"
                disabled={isLoading || !formData.name || !formData.user_input}
                className="bg-primary text-on-primary font-body-base text-body-base font-semibold py-3 px-8 rounded-lg flex items-center space-x-2 hover:bg-primary-fixed-dim transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Starting Orchestration...</span>
                  </>
                ) : (
                  <>
                    <span>Start Orchestration</span>
                    <Sparkles className="w-5 h-5" />
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
