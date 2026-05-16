import { Project, ProjectCreate, GeneratedArtifact, OrchestrationStatus } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "An unexpected error occurred" }));
      throw new Error(error.detail || response.statusText);
    }

    return response.json();
  }

  async createProject(project: ProjectCreate): Promise<Project> {
    return this.request<Project>("/api/v1/projects/", {
      method: "POST",
      body: JSON.stringify(project),
    });
  }

  async getProject(id: string): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${id}`);
  }

  async startOrchestration(id: string): Promise<{ message: string; project_id: string }> {
    return this.request<{ message: string; project_id: string }>(`/api/v1/orchestration/${id}/start`, {
      method: "POST",
    });
  }

  async getOrchestrationStatus(id: string): Promise<OrchestrationStatus> {
    return this.request<OrchestrationStatus>(`/api/v1/orchestration/${id}/status`);
  }

  async getArtifacts(projectId: string): Promise<GeneratedArtifact[]> {
    return this.request<GeneratedArtifact[]>(`/api/v1/projects/${projectId}/artifacts`);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
