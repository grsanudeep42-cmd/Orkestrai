export interface Project {
  id: string;
  name: string;
  description?: string;
  user_input: string;
  status: "orchestrating" | "completed" | "failed";
  preferences?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  user_input: string;
  preferences?: Record<string, unknown>;
}

export interface AgentLog {
  id: string;
  project_id: string;
  agent_name: string;
  action: string;
  status: "started" | "thinking" | "completed" | "failed";
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  output_preview?: string;
  full_output?: Record<string, unknown>;
  error_details?: string;
  metadata?: Record<string, unknown>;
}

export interface OrchestrationStatus {
  project_id: string;
  status: string;
  current_agent?: string;
  progress: number;
  completed_agents: string[];
  remaining_agents: string[];
  estimated_completion?: string;
}

export interface WebSocketEvent {
  type: "agent_start" | "agent_thinking" | "agent_output" | "agent_complete" | "orchestration_complete" | "error" | "connection_established" | "agent_critique" | "agent_retry" | "provider_selected" | "provider_fallback" | "provider_error" | "memory_updated" | "usage_stats" | "echo" | string;
  project_id?: string;
  agent?: string;
  target_agent?: string;
  provider?: string;
  message?: string;
  data?: Record<string, unknown>;
  usage?: Record<string, number>;
  status?: string;
  timestamp?: string;
  duration_ms?: number;
  error?: string;
  details?: string;
  is_token_exhausted?: boolean;
  is_token_error?: boolean;
}

export interface GeneratedArtifact {
  id: string;
  project_id: string;
  agent_name: string;
  artifact_type: "strategy" | "architecture" | "implementation_plan" | "github_setup" | "pitch_deck" | "code" | "documentation" | "config" | "json" | "other" | "audit";
  file_path: string;
  content: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

// Made with Bob
