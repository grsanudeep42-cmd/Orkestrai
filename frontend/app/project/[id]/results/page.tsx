"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Download, CheckCircle2, AlertCircle, Loader2, FileText, Code, FileJson } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { Project, GeneratedArtifact } from "@/types";
import { formatDistanceToNow } from "date-fns";

export default function ResultsPage() {
  const params = useParams();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [artifacts, setArtifacts] = useState<GeneratedArtifact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const projectData = await apiClient.getProject(projectId);
        setProject(projectData);
        
        if (projectData.status === "completed") {
          try {
            const artifactsData = await apiClient.getArtifacts(projectId);
            setArtifacts(artifactsData);
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
    a.download = artifact.file_path;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getArtifactIcon = (type: string) => {
    switch (type) {
      case "code":
        return <Code className="w-5 h-5" />;
      case "json":
        return <FileJson className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto" />
          <p className="font-body-base text-body-base text-on-surface-variant">Loading results...</p>
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
              <span className="font-code-sm text-code-sm">Back to Dashboard</span>
            </Link>
            {project.status === "completed" && (
              <div className="flex items-center space-x-2 text-tertiary">
                <CheckCircle2 className="w-5 h-5" />
                <span className="font-code-sm text-code-sm">Orchestration Complete</span>
              </div>
            )}
          </div>

          <div>
            <h1 className="font-headline-md text-headline-md text-on-surface mb-1">
              {project.name}
            </h1>
            <p className="font-body-base text-body-base text-on-surface-variant">
              {project.description}
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Project Info */}
        <div className="glass-panel rounded-lg p-6 mb-8">
          <h2 className="font-label-caps text-label-caps text-on-surface-variant mb-4">
            PROJECT DETAILS
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="font-code-sm text-code-sm text-on-surface-variant mb-1">Status</p>
              <p className="font-body-base text-body-base text-on-surface capitalize">
                {project.status.replace("_", " ")}
              </p>
            </div>
            <div>
              <p className="font-code-sm text-code-sm text-on-surface-variant mb-1">Created</p>
              <p className="font-body-base text-body-base text-on-surface">
                {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
              </p>
            </div>
            <div>
              <p className="font-code-sm text-code-sm text-on-surface-variant mb-1">Last Updated</p>
              <p className="font-body-base text-body-base text-on-surface">
                {formatDistanceToNow(new Date(project.updated_at || project.created_at), { addSuffix: true })}
              </p>
            </div>
          </div>
        </div>

        {/* Generated Artifacts */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-label-caps text-label-caps text-on-surface-variant">
              GENERATED ARTIFACTS ({artifacts.length})
            </h2>
          </div>

          {artifacts.length === 0 ? (
            <div className="glass-panel rounded-lg p-12 text-center">
              <AlertCircle className="w-12 h-12 text-on-surface-variant mx-auto mb-4" />
              <p className="font-body-base text-body-base text-on-surface-variant">
                No artifacts generated yet
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {artifacts.map((artifact) => (
                <div key={artifact.id} className="glass-panel rounded-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-primary">
                        {getArtifactIcon(artifact.artifact_type)}
                      </div>
                      <div>
                        <h3 className="font-code-sm text-code-sm text-on-surface mb-1">
                          {artifact.file_path}
                        </h3>
                        <p className="font-code-sm text-[11px] text-on-surface-variant">
                          Generated by {artifact.agent_name}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => downloadArtifact(artifact)}
                      className="flex items-center space-x-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-lg transition-colors border border-primary/20"
                    >
                      <Download className="w-4 h-4" />
                      <span className="font-code-sm text-code-sm">Download</span>
                    </button>
                  </div>

                  {/* Content Preview */}
                  <div className="bg-surface-container-highest rounded-lg p-4 border border-outline-variant/20">
                    <pre className="font-code-sm text-[12px] text-on-surface whitespace-pre-wrap overflow-x-auto max-h-96 overflow-y-auto">
                      {artifact.content}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="mt-8 flex justify-center space-x-4">
          <Link
            href={`/project/${projectId}`}
            className="px-6 py-3 bg-surface-container-highest hover:bg-surface-container-high text-on-surface rounded-lg transition-colors border border-outline-variant/20 font-code-sm text-code-sm"
          >
            View Orchestration Log
          </Link>
          <Link
            href="/"
            className="px-6 py-3 bg-primary hover:bg-primary/90 text-on-primary rounded-lg transition-colors font-code-sm text-code-sm"
          >
            Create New Project
          </Link>
        </div>
      </main>
    </div>
  );
}

// Made with Bob
