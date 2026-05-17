import { Project, ProjectCreate, GeneratedArtifact, OrchestrationStatus } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getAuthHeader(): Record<string, string> {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        return { Authorization: `Bearer ${token}` };
      }
    }
    return {};
  }

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 30000); // 30s timeout

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...this.getAuthHeader(),
          ...options?.headers,
        },
      });

      clearTimeout(id);

      if (response.status === 401) {
        if (typeof window !== "undefined") {
          localStorage.removeItem("token");
          if (!window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/signup")) {
            window.location.href = "/login";
          }
        }
        throw new Error("Unauthorized - please login again");
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "An unexpected error occurred" }));
        throw new Error(error.detail || response.statusText);
      }

      return response.json();
    } catch (error: any) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error("Request timed out - check your connection or server status");
      }
      throw error;
    }
  }

  // Auth
  async signup(data: any): Promise<any> {
    return this.request("/api/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async login(data: any): Promise<{ access_token: string; token_type: string }> {
    const res = await this.request<{ access_token: string; token_type: string }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (res.access_token && typeof window !== "undefined") {
      localStorage.setItem("token", res.access_token);
    }
    return res;
  }

  async getCaptcha(): Promise<{ id: string; question: string }> {
    return this.request("/api/v1/auth/captcha");
  }

  logout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
  }

  // Projects
  async createProject(project: ProjectCreate): Promise<Project> {
    return this.request<Project>("/api/v1/projects", {
      method: "POST",
      body: JSON.stringify(project),
    });
  }

  async listProjects(): Promise<{ projects: Project[]; total: number }> {
    return this.request<{ projects: Project[]; total: number }>("/api/v1/projects");
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

  async getLogs(projectId: string): Promise<any[]> {
    return this.request<any[]>(`/api/v1/projects/${projectId}/logs`);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
