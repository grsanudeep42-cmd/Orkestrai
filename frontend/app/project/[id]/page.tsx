"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, CheckCircle2, Circle, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { useWebSocket } from "@/hooks/use-websocket";
import { Project, OrchestrationStatus } from "@/types";
import { formatDistanceToNow } from "date-fns";

export default function OrchestrationView() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [status, setStatus] = useState<OrchestrationStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { isConnected, events, lastEvent } = useWebSocket(projectId);

  // Fetch project and status
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectData, statusData] = await Promise.all([
          apiClient.getProject(projectId),
          apiClient.getOrchestrationStatus(projectId),
        ]);
        setProject(projectData);
        setStatus(statusData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load project");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    
    // Poll status every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [projectId]);

  // Update status based on WebSocket events
  useEffect(() => {
    if (lastEvent?.type === "orchestration_complete") {
      router.push(`/project/${projectId}/results`);
    }
  }, [lastEvent, projectId, router]);

  const agents = [
    { name: "ProductStrategyAgent", label: "Strategy", icon: "🎯", color: "text-secondary" },
    { name: "ArchitectureAgent", label: "Architecture", icon: "🏗️", color: "text-primary" },
    { name: "CodeBuilderAgent", label: "Builder", icon: "⚡", color: "text-tertiary" },
    { name: "GitHubAgent", label: "GitHub", icon: "🔀", color: "text-error" },
    { name: "PitchAgent", label: "Pitch", icon: "✨", color: "text-secondary-fixed-dim" },
  ];

  const getAgentStatus = (agentName: string) => {
    if (!status) return "pending";
    if (status.completed_agents.includes(agentName)) return "completed";
    if (status.current_agent === agentName) return "active";
    return "pending";
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto" />
          <p className="font-body-base text-body-base text-on-surface-variant">Loading project...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-error mx-auto" />
          <p className="font-body-base text-body-base text-error">{error || "Project not found"}</p>
          <Link href="/" className="text-primary hover:underline">
            Go back home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-outline-variant/30 bg-background/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <Link href="/" className="flex items-center space-x-2 text-on-surface-variant hover:text-primary transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span className="font-code-sm text-code-sm">Back</span>
            </Link>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-tertiary animate-pulse' : 'bg-outline'}`} />
                <span className="font-code-sm text-code-sm text-on-surface-variant">
                  {isConnected ? 'Live' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-headline-md text-headline-md text-on-surface mb-1">
                {project.name}
              </h1>
              <p className="font-code-sm text-code-sm text-on-surface-variant">
                Run ID: #{projectId.slice(0, 8)}
              </p>
            </div>
            <div className="text-right">
              <span className="font-label-caps text-label-caps text-primary">OVERALL PROGRESS</span>
              <div className="font-code-sm text-code-sm text-on-surface mt-1">
                {status?.progress || 0}% Complete
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden mt-4 border border-outline-variant/20">
            <div 
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${status?.progress || 0}%` }}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agent Status Panel */}
          <div className="space-y-4">
            <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-4">
              SWARM STATUS
            </h3>
            {agents.map((agent) => {
              const agentStatus = getAgentStatus(agent.name);
              return (
                <div
                  key={agent.name}
                  className={`glass-panel p-4 rounded-lg border-l-2 transition-all ${
                    agentStatus === "active"
                      ? "border-l-primary glow-active"
                      : agentStatus === "completed"
                      ? "border-l-tertiary"
                      : "border-l-outline-variant opacity-70"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xl">{agent.icon}</span>
                      <span className={`font-code-sm text-code-sm ${
                        agentStatus === "active" ? "text-primary" : "text-on-surface"
                      }`}>
                        {agent.label}
                      </span>
                    </div>
                    {agentStatus === "completed" && (
                      <CheckCircle2 className="w-4 h-4 text-tertiary" />
                    )}
                    {agentStatus === "active" && (
                      <Loader2 className="w-4 h-4 text-primary animate-spin" />
                    )}
                    {agentStatus === "pending" && (
                      <Circle className="w-4 h-4 text-outline-variant" />
                    )}
                  </div>
                  <p className="font-code-sm text-[11px] text-on-surface-variant">
                    {agentStatus === "active" && "Processing..."}
                    {agentStatus === "completed" && "Completed successfully"}
                    {agentStatus === "pending" && "Waiting..."}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Activity Timeline */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-4">
              EVENT LOG
            </h3>
            <div className="glass-panel rounded-lg p-6 min-h-[500px] max-h-[600px] overflow-y-auto">
              {events.length === 0 ? (
                <div className="text-center py-12">
                  <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
                  <p className="font-body-base text-body-base text-on-surface-variant">
                    Waiting for agents to start...
                  </p>
                </div>
              ) : (
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-outline-variant/30 before:to-transparent">
                  {events.map((event, index) => (
                    <div key={index} className="relative flex items-start space-x-4 pl-8">
                      <div className={`absolute left-0 w-4 h-4 rounded-full border-2 border-background ${
                        event.type === "agent_complete" ? "bg-tertiary" :
                        event.type === "error" ? "bg-error" :
                        event.type === "agent_start" ? "bg-primary" :
                        "bg-primary/50 animate-pulse"
                      }`} />
                      <div className="flex-1 glass-panel p-3 rounded">
                        <div className="flex justify-between items-center mb-1">
                          <span className={`font-label-caps text-[10px] ${
                            event.type === "error" ? "text-error" : "text-primary"
                          }`}>
                            {event.agent || "SYSTEM"}
                          </span>
                          {event.timestamp && (
                            <time className="font-code-sm text-[10px] text-on-surface-variant">
                              {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                            </time>
                          )}
                        </div>
                        <p className="font-code-sm text-[12px] text-on-surface">
                          {event.message || event.type.replace(/_/g, " ")}
                        </p>
                        {event.duration_ms && (
                          <p className="font-code-sm text-[10px] text-on-surface-variant/70 mt-1">
                            Completed in {event.duration_ms}ms
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Made with Bob
