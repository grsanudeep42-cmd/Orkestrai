"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, CheckCircle2, Circle, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { useWebSocket } from "@/hooks/use-websocket";
import { Project, OrchestrationStatus } from "@/types";
import { formatDistanceToNow } from "date-fns";

const parseUTCDate = (dateString: string | undefined | null) => {
  if (!dateString) return new Date();
  return new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
};

export default function OrchestrationView() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [status, setStatus] = useState<OrchestrationStatus | null>(null);
  const [historicalEvents, setHistoricalEvents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { isConnected, events: liveEvents, lastEvent } = useWebSocket(projectId);

  // Combine live and historical events, removing duplicates
  const events = [...historicalEvents, ...liveEvents].filter((event, index, self) => 
    index === self.findIndex((e) => (
      e.timestamp === event.timestamp && e.agent === event.agent && e.message === event.message
    ))
  );

  // Metrics & State
  const retriesCount = events.filter(e => e.type === "agent_retry").length;
  const totalDurationMs = events.reduce((sum, e) => sum + (e.duration_ms || 0), 0);
  const activeProvider = events.slice().reverse().find(e => e.type === "provider_selected" || e.type === "provider_fallback")?.provider || null;

  // Fetch project and status
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectData, statusData, logsData] = await Promise.all([
          apiClient.getProject(projectId),
          apiClient.getOrchestrationStatus(projectId),
          apiClient.getLogs(projectId)
        ]);
        setProject(projectData);
        setStatus(statusData);

        // Map AgentLog to WebSocketEvent format
        const mappedLogs = logsData.map(log => ({
          type: log.status === 'completed' ? 'agent_complete' : 
                log.status === 'failed' ? 'error' : 
                log.agent_name === 'AuditAgent' ? 'agent_critique' : 'agent_start',
          agent: log.agent_name,
          message: log.output_preview || log.action.replace(/_/g, ' '),
          timestamp: log.started_at,
          duration_ms: log.duration_ms,
          data: log.full_output
        }));
        setHistoricalEvents(mappedLogs);

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
    { name: "BuilderAgent", label: "Builder", icon: "⚡", color: "text-warning" },
    { name: "GitHubAgent", label: "GitHub", icon: "🔀", color: "text-success" },
    { name: "PitchAgent", label: "Pitch", icon: "✨", color: "text-primary" },
    { name: "AuditAgent", label: "Auditor", icon: "🧐", color: "text-error" },
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
          <p className="font-mono text-sm text-muted-foreground">Initializing Swarm Interface...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-error mx-auto" />
          <p className="text-error">{error || "Project not found"}</p>
          <Link href="/" className="text-primary hover:underline">
            Abort and return to base
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/30">
      {/* Header */}
      <header className="border-b border-border bg-background/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <Link 
              href={project?.status === 'completed' ? `/project/${projectId}/results` : "/"} 
              className="flex items-center space-x-2 text-muted-foreground hover:text-primary transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="font-mono text-sm">Back to {project?.status === 'completed' ? 'Results' : 'Dashboard'}</span>
            </Link>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success animate-pulse shadow-[0_0_10px_rgba(0,255,136,0.5)]' : 'bg-muted'}`} />
                <span className="font-mono text-sm text-muted-foreground">
                  {isConnected ? 'Swarm Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-1">
                {project.name}
              </h1>
              <p className="font-mono text-sm text-muted-foreground">
                Run ID: #{projectId.slice(0, 8)}
              </p>
            </div>
            <div className="text-right">
              <span className="font-mono text-xs text-primary uppercase tracking-wider">SWARM PROGRESS</span>
              <div className="font-mono text-lg mt-1 font-bold">
                {status?.progress || 0}% Complete
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full h-2 bg-surface rounded-full overflow-hidden mt-4 border border-border">
            <div 
              className="h-full bg-gradient-to-r from-primary to-success transition-all duration-500 shadow-[0_0_10px_rgba(0,212,255,0.5)]"
              style={{ width: `${status?.progress || 0}%` }}
            />
          </div>
        </div>
      </header>

      {/* Metrics Dashboard */}
      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-lg flex flex-col border border-border">
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">ACTIVE LLM</span>
            <span className={`text-2xl font-bold mt-1 ${activeProvider ? 'text-primary drop-shadow-[0_0_8px_rgba(0,212,255,0.5)]' : 'text-foreground'}`}>
              {activeProvider || "Idle"}
            </span>
          </div>
          <div className="glass-panel p-4 rounded-lg flex flex-col border border-border">
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">AUTONOMOUS RETRIES</span>
            <span className={`text-2xl font-bold mt-1 ${retriesCount > 0 ? 'text-error animate-pulse drop-shadow-[0_0_8px_rgba(255,68,68,0.5)]' : 'text-foreground'}`}>
              {retriesCount}
            </span>
          </div>
          <div className="glass-panel p-4 rounded-lg flex flex-col border border-border">
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">EXECUTION TIME</span>
            <span className="text-2xl font-bold mt-1 text-foreground">
              {(totalDurationMs / 1000).toFixed(1)}s
            </span>
          </div>
          <div className="glass-panel p-4 rounded-lg flex flex-col border border-border">
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">SYSTEM STATUS</span>
            <span className={`text-2xl font-bold mt-1 ${isConnected ? "text-success drop-shadow-[0_0_8px_rgba(0,255,136,0.5)]" : "text-muted-foreground"}`}>
              {isConnected ? "Online" : "Offline"}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agent Status Panel */}
          <div className="space-y-4">
            <h3 className="font-mono text-sm text-muted-foreground uppercase tracking-wider mb-4 border-b border-border pb-2">
              AGENT STATUS
            </h3>
            {agents.map((agent) => {
              const agentStatus = getAgentStatus(agent.name);
              return (
                <div
                  key={agent.name}
                  className={`glass-panel p-4 rounded-lg border-l-4 transition-all ${
                    agentStatus === "active"
                      ? "border-l-primary border-t-border border-r-border border-b-border bg-primary/5 shadow-[0_0_15px_rgba(0,212,255,0.15)]"
                      : agentStatus === "completed"
                      ? "border-l-success border-t-border border-r-border border-b-border"
                      : "border-l-muted border-t-border border-r-border border-b-border opacity-50"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">{agent.icon}</span>
                      <span className={`font-bold ${
                        agentStatus === "active" ? "text-primary" : "text-foreground"
                      }`}>
                        {agent.label}
                      </span>
                    </div>
                    {agentStatus === "completed" && (
                      <CheckCircle2 className="w-5 h-5 text-success drop-shadow-[0_0_5px_rgba(0,255,136,0.5)]" />
                    )}
                    {agentStatus === "active" && (
                      <Loader2 className="w-5 h-5 text-primary animate-spin" />
                    )}
                    {agentStatus === "pending" && (
                      <Circle className="w-5 h-5 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <p className="font-mono text-[11px] text-muted-foreground">
                      {agentStatus === "active" ? "Processing..." :
                       agentStatus === "completed" ? "Completed successfully" :
                       "Waiting in queue..."}
                    </p>
                    {/* Visual cue for retries if this agent is active and there's a retry */}
                    {agentStatus === "active" && lastEvent?.type === "agent_retry" && lastEvent.agent === agent.name && (
                      <span className="font-mono text-[10px] text-error font-bold animate-pulse bg-error/10 px-2 py-0.5 rounded border border-error/50">
                        CORRECTING
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Activity Timeline */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="font-mono text-sm text-muted-foreground uppercase tracking-wider mb-4 border-b border-border pb-2">
              SWARM EVENT LOG
            </h3>
            <div className="glass-panel rounded-lg p-6 min-h-[500px] max-h-[600px] overflow-y-auto border border-border relative">
              {events.length === 0 ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
                  <p className="font-mono text-sm text-muted-foreground">
                    Awaiting initialization...
                  </p>
                </div>
              ) : (
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-border before:to-transparent">
                  {events.map((event, index) => (
                    <div key={index} className="relative flex items-start space-x-4 pl-8">
                      <div className={`absolute left-0 w-4 h-4 rounded-full border-2 border-background ${
                        event.type === "agent_complete" ? "bg-success shadow-[0_0_8px_rgba(0,255,136,0.6)]" :
                        event.type === "error" ? "bg-error shadow-[0_0_8px_rgba(255,68,68,0.6)]" :
                        event.type === "agent_critique" ? "bg-warning shadow-[0_0_8px_rgba(255,176,32,0.6)]" :
                        event.type === "agent_retry" ? "bg-error" :
                        event.type === "provider_selected" ? "bg-secondary" :
                        event.type === "memory_updated" ? "bg-primary" :
                        event.type === "agent_start" ? "bg-primary shadow-[0_0_8px_rgba(0,212,255,0.6)]" :
                        "bg-primary/50 animate-pulse"
                      }`} />
                      <div className={`flex-1 bg-surface p-3 rounded-md border ${
                        event.type === "agent_critique" ? "border-warning/50 bg-warning/10" :
                        event.type === "agent_retry" ? "border-error/50 bg-error/10 shadow-[0_0_10px_rgba(255,68,68,0.2)]" :
                        event.type === "provider_selected" ? "border-secondary/30 bg-secondary/5" :
                        event.type === "memory_updated" ? "border-primary/30 bg-primary/5" : "border-border"
                      }`}>
                        <div className="flex justify-between items-center mb-1">
                          <span className={`font-mono text-[10px] font-bold uppercase tracking-wider ${
                            event.type === "error" ? "text-error" : 
                            event.type === "agent_critique" ? "text-warning" :
                            event.type === "agent_retry" ? "text-error" :
                            event.type === "provider_selected" ? "text-secondary" :
                            event.type === "memory_updated" ? "text-primary" :
                            "text-primary"
                          }`}>
                            {event.agent || "SYSTEM"} 
                            {event.target_agent && ` ➔ ${event.target_agent}`}
                          </span>
                          {event.timestamp && (
                            <time className="font-mono text-[10px] text-muted-foreground">
                              {formatDistanceToNow(parseUTCDate(event.timestamp), { addSuffix: true })}
                            </time>
                          )}
                        </div>
                        <p className={`text-sm ${event.type === "agent_thinking" ? "text-muted-foreground animate-pulse" : "text-foreground"}`}>
                          {event.message || event.type.replace(/_/g, " ")}
                        </p>
                        {event.duration_ms && (
                          <p className="font-mono text-[10px] text-muted-foreground mt-2 border-t border-border/50 pt-1">
                            Execution: {event.duration_ms}ms
                          </p>
                        )}
                        {event.data && event.type === "agent_critique" && (
                           <div className="mt-2 text-xs text-foreground bg-background p-3 rounded border border-warning/20">
                             <div className={`font-bold mb-2 ${event.data.needs_retry ? "text-error animate-pulse flex items-center space-x-2" : "text-success"}`}>
                               {event.data.needs_retry ? (
                                 <>
                                   <AlertCircle className="w-4 h-4" />
                                   <span>CORRECTION REQUIRED</span>
                                 </>
                               ) : "PASSED AUDIT"}
                             </div>
                             <div className="font-mono text-[11px] whitespace-pre-wrap text-muted-foreground border-l-2 border-border pl-2">
                               {event.data.critique_and_feedback}
                             </div>
                           </div>
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
