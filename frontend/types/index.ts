export interface Project {
  id: string;
  name: string;
  description?: string;
  user_input: string;
  status: "orchestrating" | "completed" | "failed";
  preferences?: Record<string, any>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  user_input: string;
  preferences?: Record<string, any>;
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
  full_output?: Record<string, any>;
  error_details?: string;
  metadata?: Record<string, any>;
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
  type: "agent_start" | "agent_thinking" | "agent_output" | "agent_complete" | "orchestration_complete" | "error" | "connection_established";
  project_id?: string;
  agent?: string;
  message?: string;
  data?: any;
  status?: string;
  timestamp?: string;
  duration_ms?: number;
  error?: string;
  details?: string;
}

export interface GeneratedArtifact {
  id: string;
  project_id: string;
  agent_name: string;
  artifact_type: "code" | "documentation" | "config" | "strategy" | "json" | "other";
  file_path: string;
  content: string;
  created_at: string;
  metadata?: Record<string, any>;
}

// Made with Bob
