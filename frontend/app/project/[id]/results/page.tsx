"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Download, CheckCircle2, AlertCircle, Loader2, FileText, Code, FileJson, GitBranch, Terminal, ChevronDown, ChevronUp, RefreshCw, Settings } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { useWebSocket } from "@/hooks/use-websocket";
import { Project, GeneratedArtifact } from "@/types";
import { formatDistanceToNow } from "date-fns";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CodeFilesView from "@/components/CodeFilesView";

const parseUTCDate = (dateString: string | undefined | null) => {
  if (!dateString) return new Date();
  return new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
};

const ArtifactRenderer = ({ type, content, projectId, events }: { type: string; content: string; projectId: string; events: any[] }) => {
  // Try to parse as JSON first in case some agents still output JSON
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let data: any;
  let isJson = false;

  try {
    let cleanContent = content.trim();
    const match = cleanContent.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
    if (match) cleanContent = match[1].trim();
    if (cleanContent.startsWith('{') || cleanContent.startsWith('[')) {
      data = JSON.parse(cleanContent);
      isJson = true;
    }
  } catch (_e) {
    // Not JSON, it's fine, it's probably Markdown
  }

  // If it's a known structured agent that outputs URLs/JSON, render custom
  if (isJson) {
    if (type === "implementation_plan" && (data.files || data.file_tree)) {
      const downloadUrl = `http://localhost:8000/api/v1/projects/${projectId}/download`;
      return (
        <div className="space-y-6">
          <div className="bg-surface border border-border p-6 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Code className="w-8 h-8 text-warning" />
                <div>
                  <h3 className="text-xl font-bold text-foreground">Codebase Generated</h3>
                  <p className="text-sm text-muted-foreground">{data.files_generated || (data.files?.length || 0)} files created</p>
                </div>
              </div>
              <a href={downloadUrl} className="inline-flex items-center space-x-2 bg-warning text-background px-4 py-2 rounded-md font-bold hover:bg-warning/90 transition-colors text-sm">
                <Download className="w-4 h-4" />
                <span>Download ZIP</span>
              </a>
            </div>
            
            <CodeFilesView files={data.files || []} zipUrl={downloadUrl} />
          </div>
          
          <div className="p-4 bg-muted/10 border border-border rounded-lg">
            <h4 className="font-bold text-foreground mb-2 text-sm flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Generation Logs</span>
            </h4>
            <pre className="font-mono text-[10px] text-muted-foreground whitespace-pre-wrap max-h-40 overflow-y-auto">{data.message}</pre>
          </div>
        </div>
      );
    }
    
    if (type === "github_setup") {
      const isPending = !data.repository_url || data.repository_url.includes("setup-pending");
      // eslint-disable-next-line react-hooks/rules-of-hooks
      const [isRetrying, setIsRetrying] = useState(false);
      // eslint-disable-next-line react-hooks/rules-of-hooks
      const [retryStatus, setRetryStatus] = useState<string | null>(null);

      const handleRetryGithub = async () => {
        setIsRetrying(true);
        setRetryStatus(null);
        try {
          await apiClient.request(`/api/v1/projects/${projectId}/github-retry`, { method: "POST" });
          setRetryStatus("success");
          window.location.reload(); // Refresh to show new artifact data
        } catch (err: any) {
          setRetryStatus(err.message || "Retry failed");
        } finally {
          setIsRetrying(false);
        }
      };
      
      return (
        <div className="space-y-6">
          <div className="bg-surface border border-border p-6 rounded-lg text-center space-y-4">
            <GitBranch className="w-12 h-12 text-success mx-auto" />
            {isPending ? (
              <>
                <h3 className="text-xl font-bold text-foreground">GitHub Setup Recommended</h3>
                <p className="text-muted-foreground">GitHub token not configured. Below are the recommended workflows and issues for your manual setup.</p>
                <div className="flex flex-col items-center space-y-3">
                  <Link href="/settings" className="text-primary hover:underline text-sm font-bold">
                    Connect GitHub in Settings
                  </Link>
                  <button 
                    onClick={handleRetryGithub}
                    disabled={isRetrying}
                    className="flex items-center space-x-2 bg-primary/10 hover:bg-primary/20 text-primary px-6 py-2 rounded-lg font-bold border border-primary/30 transition-all disabled:opacity-50"
                  >
                    {isRetrying ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    <span>Retry GitHub Integration</span>
                  </button>
                </div>
              </>
            ) : (
              <>
                <h3 className="text-xl font-bold text-foreground">GitHub Repository Created</h3>
                <p className="text-muted-foreground">The generated code has been pushed to your new repository.</p>
                <div className="flex justify-center space-x-4">
                  <a href={data.repository_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center space-x-2 bg-success text-background px-6 py-3 rounded-md font-bold hover:bg-success/90 transition-colors">
                    <GitBranch className="w-5 h-5" />
                    <span>View Repository on GitHub</span>
                  </a>
                  <button 
                    onClick={handleRetryGithub}
                    disabled={isRetrying}
                    className="flex items-center space-x-2 bg-muted/20 hover:bg-muted/30 text-foreground px-6 py-3 rounded-md font-bold transition-all disabled:opacity-50 border border-border"
                  >
                    {isRetrying ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    <span>Push to Repo Again</span>
                  </button>
                </div>
              </>
            )}
            {retryStatus && retryStatus !== "success" && (
              <p className="text-error text-xs font-mono">{retryStatus}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-muted/10 border border-border rounded-lg">
              <h4 className="font-bold text-foreground mb-3 flex items-center space-x-2">
                <GitBranch className="w-4 h-4 text-primary" />
                <span>Workflows Recommended</span>
              </h4>
              <ul className="space-y-2">
                {data.workflows_created > 0 ? (
                  <li className="text-sm text-muted-foreground flex items-center space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-success" />
                    <span>{data.workflows_created} CI/CD workflows created</span>
                  </li>
                ) : (
                  <li className="text-sm text-muted-foreground">CI/CD workflows defined for manual setup</li>
                )}
                <li className="text-sm text-muted-foreground flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-success" />
                  <span>Branching strategy: {data.branch_strategy?.main_branch} & {data.branch_strategy?.development_branch}</span>
                </li>
              </ul>
            </div>
            <div className="p-4 bg-muted/10 border border-border rounded-lg">
              <h4 className="font-bold text-foreground mb-3 flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-warning" />
                <span>Issues & Roadmap</span>
              </h4>
              <p className="text-sm text-muted-foreground">{data.issues_created || 0} issues planned and documented in the project backlog.</p>
            </div>
          </div>

          <div className="p-4 bg-muted/5 border border-border rounded-lg">
            <h4 className="font-bold text-foreground mb-2 text-sm">GitHub Operations Log</h4>
            <div className="font-mono text-[10px] text-muted-foreground whitespace-pre-wrap max-h-40 overflow-y-auto space-y-1">
              {events.filter(e => e.agent === "GitHubAgent").length > 0 ? (
                events.filter(e => e.agent === "GitHubAgent").map((e, idx) => (
                  <div key={idx} className="border-l border-primary/30 pl-2">
                    <span className="text-primary/70 mr-2">[{new Date(e.timestamp).toLocaleTimeString()}]</span>
                    {e.message || e.type}
                  </div>
                ))
              ) : (
                <div>{data.message || "Ready for integration."}</div>
              )}
            </div>
          </div>
        </div>
      );
    }

    if (type === "pitch_deck") {
      const pitchUrl = `http://localhost:8000/api/v1/projects/${projectId}/pitch`;
      return (
        <div className="space-y-4">
          <div className="bg-surface border border-border p-6 rounded-lg text-center space-y-4">
            <FileText className="w-12 h-12 text-primary mx-auto" />
            <h3 className="text-xl font-bold text-foreground">Pitch Deck Generated</h3>
            <p className="text-muted-foreground">A self-contained HTML presentation has been created.</p>
            <div className="flex justify-center space-x-4">
              <a href={pitchUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center space-x-2 bg-primary text-background px-6 py-3 rounded-md font-bold hover:bg-primary-hover transition-colors">
                <span>View Presentation</span>
              </a>
              <a href={pitchUrl} download={`${projectId}_pitch.html`} className="inline-flex items-center space-x-2 border border-primary text-primary px-6 py-3 rounded-md font-bold hover:bg-primary/10 transition-colors">
                <Download className="w-4 h-4" />
                <span>Download HTML</span>
              </a>
            </div>
          </div>
        </div>
      );
    }

    // Fallback JSON renderer
    return (
      <div className="p-4 bg-background text-foreground rounded-lg border border-border overflow-x-auto">
        <pre className="whitespace-pre-wrap font-mono text-sm">{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  }

  // Default Markdown Renderer
  return (
    <div className="prose prose-invert prose-p:text-muted-foreground prose-headings:text-foreground prose-a:text-primary max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default function ResultsPage() {
  const params = useParams();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [artifacts, setArtifacts] = useState<GeneratedArtifact[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("");
  const [showLogs, setShowLogs] = useState(false);
  
  const { events: liveEvents } = useWebSocket(projectId);

  // Combine live events and historical logs
  const mappedHistoricalLogs = logs.map(log => ({
    type: log.status === 'completed' ? 'agent_complete' : 
          log.status === 'failed' ? 'error' : 
          log.agent_name === 'AuditAgent' ? 'agent_critique' : 'agent_start',
    agent: log.agent_name,
    message: log.output_preview || log.action.replace(/_/g, ' '),
    timestamp: log.started_at,
    duration_ms: log.duration_ms,
    data: log.full_output
  }));

  const events = [...mappedHistoricalLogs, ...liveEvents].filter((event, index, self) => 
    index === self.findIndex((e) => (
      e.timestamp === event.timestamp && e.agent === event.agent && e.message === event.message
    ))
  );

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectData, logsData] = await Promise.all([
          apiClient.getProject(projectId),
          apiClient.getLogs(projectId)
        ]);
        setProject(projectData);
        setLogs(logsData);
        
        if (projectData.status === "completed") {
          try {
            const artifactsData = await apiClient.getArtifacts(projectId);
            setArtifacts(artifactsData);
            if (artifactsData.length > 0) {
              // Set the default tab based on priority
              const priorities = ["strategy", "architecture", "implementation_plan", "github_setup", "pitch_deck", "audit"];
              const sorted = artifactsData.sort((a, b) => {
                const aIdx = priorities.indexOf(a.artifact_type);
                const bIdx = priorities.indexOf(b.artifact_type);
                return (aIdx === -1 ? 99 : aIdx) - (bIdx === -1 ? 99 : bIdx);
              });
              setActiveTab(sorted[0].artifact_type);
            }
          } catch (artifactErr) {
            console.error("Failed to fetch artifacts:", artifactErr);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load results");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [projectId]);

  const downloadArtifact = (artifact: GeneratedArtifact) => {
    const blob = new Blob([artifact.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = artifact.file_path || `${artifact.artifact_type}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getArtifactIcon = (type: string) => {
    switch (type) {
      case "strategy":
        return "🎯";
      case "architecture":
        return "🏗️";
      case "implementation_plan":
        return <Code className="w-5 h-5" />;
      case "github_setup":
        return <GitBranch className="w-5 h-5" />;
      case "pitch_deck":
        return "✨";
      case "code":
        return <Code className="w-5 h-5" />;
      case "json":
        return <FileJson className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  const getArtifactLabel = (type: string) => {
    switch (type) {
      case "strategy":
        return "Product Strategy";
      case "architecture":
        return "System Architecture";
      case "implementation_plan":
        return "Generated Code";
      case "github_setup":
        return "GitHub Setup";
      case "pitch_deck":
        return "Pitch Materials";
      default:
        return type.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  const getArtifactColor = (type: string) => {
    switch (type) {
      case "strategy":
        return "border-secondary";
      case "architecture":
        return "border-primary";
      case "implementation_plan":
        return "border-warning";
      case "github_setup":
        return "border-success";
      case "pitch_deck":
        return "border-primary";
      default:
        return "border-muted";
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto" />
          <p className="font-mono text-sm text-muted-foreground">Aggregating Artifacts...</p>
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
            Return to Base
          </Link>
        </div>
      </div>
    );
  }

  const activeArtifact = artifacts.find(a => a.artifact_type === activeTab);

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/30">
      {/* Header */}
      <header className="border-b border-border bg-background/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-2 text-muted-foreground hover:text-primary transition-colors">
                <ArrowLeft className="w-5 h-5" />
                <span className="font-mono text-sm">Back to Dashboard</span>
              </Link>
              <Link href="/settings" className="p-2 text-muted-foreground hover:text-primary transition-colors" title="Settings">
                <Settings className="w-5 h-5" />
              </Link>
            </div>
            {project.status === "completed" && (
              <div className="flex items-center space-x-2 text-success">
                <CheckCircle2 className="w-5 h-5" />
                <span className="font-mono text-sm font-bold">Orchestration Complete</span>
              </div>
            )}
          </div>

          <div>
            <h1 className="text-3xl font-bold mb-1">
              {project.name}
            </h1>
            <p className="text-muted-foreground">
              {project.description || "Generated Project Artifacts"}
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        
        {artifacts.length === 0 ? (
          <div className="glass-panel rounded-lg p-12 text-center border border-border">
            <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">
              No artifacts generated yet. Did orchestration complete successfully?
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            
            {/* Sidebar Navigation */}
            <div className="lg:col-span-1 space-y-2">
              <h3 className="font-mono text-sm text-muted-foreground uppercase tracking-wider mb-4 border-b border-border pb-2">
                PROJECT ARTIFACTS
              </h3>
              <div className="flex flex-col space-y-2">
                {artifacts.map((artifact) => (
                  <button
                    key={artifact.id}
                    onClick={() => setActiveTab(artifact.artifact_type)}
                    className={`flex items-center space-x-3 p-3 rounded-md transition-all text-left border-l-4 ${
                      activeTab === artifact.artifact_type
                        ? `bg-surface border-l-primary shadow-md`
                        : `bg-transparent border-l-transparent hover:bg-surface border-border`
                    }`}
                  >
                    <span className="text-xl">{getArtifactIcon(artifact.artifact_type)}</span>
                    <div>
                      <div className={`font-bold ${activeTab === artifact.artifact_type ? "text-primary" : "text-foreground"}`}>
                        {getArtifactLabel(artifact.artifact_type)}
                      </div>
                      <div className="font-mono text-[10px] text-muted-foreground mt-0.5">
                        By {artifact.agent_name}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Active Artifact View */}
            <div className="lg:col-span-3">
              {activeArtifact && (
                <div className={`glass-panel rounded-lg overflow-hidden border border-border border-t-4 ${getArtifactColor(activeArtifact.artifact_type)} shadow-2xl`}>
                  
                  {/* Artifact Toolbar */}
                  <div className="bg-surface border-b border-border p-4 flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold flex items-center space-x-2">
                        <span>{getArtifactIcon(activeArtifact.artifact_type)}</span>
                        <span>{getArtifactLabel(activeArtifact.artifact_type)}</span>
                      </h2>
                      <p className="font-mono text-xs text-muted-foreground mt-1">
                        Created {formatDistanceToNow(parseUTCDate(activeArtifact.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    
                    <button
                      onClick={() => downloadArtifact(activeArtifact)}
                      className="flex items-center space-x-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-md transition-colors border border-primary/20 hover:scale-105"
                    >
                      <Download className="w-4 h-4" />
                      <span className="font-mono text-sm font-bold">Download Source</span>
                    </button>
                  </div>

                  {/* Artifact Content */}
                  <div className="p-8 bg-background min-h-[500px]">
                    <ArtifactRenderer type={activeArtifact.artifact_type} content={activeArtifact.content} projectId={projectId as string} events={events} />
                  </div>
                </div>
              )}
            </div>

          </div>
        )}

        {/* Logs Section */}
        <div className="mt-12">
          <button 
            onClick={() => setShowLogs(!showLogs)}
            className="w-full flex items-center justify-between p-6 bg-surface border border-border rounded-xl hover:border-primary/30 transition-all group shadow-sm"
          >
            <div className="flex items-center space-x-3">
              <Terminal className="w-6 h-6 text-primary" />
              <div className="text-left">
                <h3 className="text-lg font-bold uppercase tracking-tight">Orchestration History</h3>
                <p className="text-xs text-muted-foreground font-mono">Real-time agent logs preserved for audit</p>
              </div>
            </div>
            {showLogs ? <ChevronUp className="w-5 h-5 text-muted-foreground" /> : <ChevronDown className="w-5 h-5 text-muted-foreground" />}
          </button>

          {showLogs && (
            <div className="mt-4 bg-background border border-border rounded-xl overflow-hidden shadow-2xl">
              <div className="p-2 border-b border-border bg-surface flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-error" />
                <div className="w-2 h-2 rounded-full bg-warning" />
                <div className="w-2 h-2 rounded-full bg-success" />
                <span className="text-[10px] font-mono text-muted-foreground ml-2 uppercase tracking-widest">Agent Trace Console</span>
              </div>
              <div className="p-6 space-y-4 max-h-[500px] overflow-y-auto font-mono text-sm bg-background/50">
                {logs.length === 0 ? (
                  <p className="text-muted-foreground italic text-center py-8">No trace logs available.</p>
                ) : (
                  logs.map((log, idx) => (
                    <div key={idx} className="border-l-2 border-primary/20 pl-4 py-2 group hover:border-primary transition-colors">
                      <div className="flex items-center space-x-3 mb-1">
                        <span className="text-[10px] text-muted-foreground">{new Date(log.started_at).toLocaleTimeString()}</span>
                        <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                          log.status === 'completed' ? 'bg-success/10 text-success' : 
                          log.status === 'failed' ? 'bg-error/10 text-error' : 'bg-primary/10 text-primary'
                        }`}>
                          {log.agent_name}
                        </span>
                        <span className="text-foreground font-bold tracking-tight">{log.action.replace(/_/g, ' ')}</span>
                      </div>
                      <div className="text-muted-foreground text-xs leading-relaxed line-clamp-2 group-hover:line-clamp-none transition-all">
                        {log.output_preview || (log.full_output?.message) || "Action processed successfully."}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="mt-12 flex justify-center space-x-4 border-t border-border pt-8">
          <Link
            href={`/project/${projectId}`}
            className="px-6 py-3 bg-surface hover:bg-muted text-foreground rounded-md transition-colors border border-border font-mono text-sm"
          >
            View Orchestration Log
          </Link>
          <Link
            href="/create"
            className="px-6 py-3 bg-primary hover:bg-primary-hover text-background rounded-md transition-colors font-bold font-mono text-sm shadow-[0_0_15px_rgba(0,212,255,0.3)]"
          >
            Create New Project
          </Link>
        </div>
      </main>
    </div>
  );
}

// Made with Bob
