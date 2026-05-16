"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Download, CheckCircle2, AlertCircle, Loader2, FileText, Code, FileJson, GitBranch as Github } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { Project, GeneratedArtifact } from "@/types";
import { formatDistanceToNow } from "date-fns";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const parseUTCDate = (dateString: string | undefined | null) => {
  if (!dateString) return new Date();
  return new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z');
};

const ArtifactRenderer = ({ type, content }: { type: string; content: string }) => {
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
    if (type === "implementation_plan" && data.zip_path) {
      return (
        <div className="space-y-4">
          <div className="bg-surface border border-border p-6 rounded-lg text-center space-y-4">
            <Code className="w-12 h-12 text-warning mx-auto" />
            <h3 className="text-xl font-bold text-foreground">Code Generated Successfully</h3>
            <p className="text-muted-foreground">{data.files_generated} files generated and packaged.</p>
            <a href={`http://localhost:8000${data.zip_url}`} download className="inline-flex items-center space-x-2 bg-warning text-background px-6 py-3 rounded-md font-bold hover:bg-warning/90 transition-colors">
              <Download className="w-5 h-5" />
              <span>Download ZIP Source Code</span>
            </a>
          </div>
          <div className="mt-4 p-4 bg-muted/20 border border-border rounded-lg">
            <h4 className="font-bold text-foreground mb-2">Build Log</h4>
            <pre className="font-mono text-xs text-muted-foreground whitespace-pre-wrap">{data.message}</pre>
          </div>
        </div>
      );
    }
    
    if (type === "github_setup" && data.repository_url) {
      return (
        <div className="space-y-4">
          <div className="bg-surface border border-border p-6 rounded-lg text-center space-y-4">
            <Github className="w-12 h-12 text-success mx-auto" />
            <h3 className="text-xl font-bold text-foreground">GitHub Repository Created</h3>
            <p className="text-muted-foreground">The generated code has been pushed to your new repository.</p>
            <a href={data.repository_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center space-x-2 bg-success text-background px-6 py-3 rounded-md font-bold hover:bg-success/90 transition-colors">
              <Github className="w-5 h-5" />
              <span>View Repository on GitHub</span>
            </a>
          </div>
          <div className="mt-4 p-4 bg-muted/20 border border-border rounded-lg">
            <h4 className="font-bold text-foreground mb-2">GitHub Operations Log</h4>
            <pre className="font-mono text-xs text-muted-foreground whitespace-pre-wrap">{data.message}</pre>
          </div>
        </div>
      );
    }

    if (type === "pitch_deck" && data.presentation_url) {
      return (
        <div className="space-y-4">
          <div className="bg-surface border border-border p-6 rounded-lg text-center space-y-4">
            <FileText className="w-12 h-12 text-primary mx-auto" />
            <h3 className="text-xl font-bold text-foreground">Pitch Deck Generated</h3>
            <p className="text-muted-foreground">A self-contained HTML presentation has been created.</p>
            <div className="flex justify-center space-x-4">
              <a href={`http://localhost:8000${data.presentation_url}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center space-x-2 bg-primary text-background px-6 py-3 rounded-md font-bold hover:bg-primary-hover transition-colors">
                <span>View Presentation</span>
              </a>
              <a href={`http://localhost:8000${data.presentation_url}`} download className="inline-flex items-center space-x-2 border border-primary text-primary px-6 py-3 rounded-md font-bold hover:bg-primary/10 transition-colors">
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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const projectData = await apiClient.getProject(projectId);
        setProject(projectData);
        
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
        return "⚡";
      case "github_setup":
        return "🔀";
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
        return "Builder Artifacts";
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
            <Link href="/" className="flex items-center space-x-2 text-muted-foreground hover:text-primary transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span className="font-mono text-sm">Back to Dashboard</span>
            </Link>
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
                    <ArtifactRenderer type={activeArtifact.artifact_type} content={activeArtifact.content} />
                  </div>
                </div>
              )}
            </div>

          </div>
        )}

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
