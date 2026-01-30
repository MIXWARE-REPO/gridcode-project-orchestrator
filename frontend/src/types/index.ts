// Project Types

export type ProjectStatus =
  | "discovery"
  | "design"
  | "implementation"
  | "validation"
  | "operation"
  | "completed"
  | "paused";

export type AgentStatus = "idle" | "working" | "completed" | "blocked";

export type MessageRole = "user" | "assistant" | "system";

// Auth Types

export interface LoginRequest {
  project_code: string;
  email?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  project_id: string;
  project_name: string;
}

// Project Types

export interface AgentInfo {
  name: string;
  alias: string;
  status: AgentStatus;
  current_task: string | null;
  progress: number;
  last_activity: string | null;
}

export interface ProjectPhase {
  number: number;
  name: string;
  status: "pending" | "in_progress" | "completed";
  progress: number;
  description: string;
}

export interface ProjectSummary {
  id: string;
  name: string;
  code: string;
  status: ProjectStatus;
  progress: number;
  current_phase: string;
  created_at: string;
}

export interface ProjectDetail extends ProjectSummary {
  description: string | null;
  phases: ProjectPhase[];
  agents: AgentInfo[];
  updated_at: string;
  estimated_completion: string | null;
  total_hours: number;
  hours_by_department: Record<string, number>;
}

export interface ActivityItem {
  id: string;
  timestamp: string;
  agent: string;
  action: string;
  description: string;
  category: "code" | "review" | "deployment" | "communication";
  metadata?: Record<string, unknown>;
}

export interface ActivitiesResponse {
  items: ActivityItem[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

// Chat Types

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  project_id: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  timestamp: string;
  suggestions?: string[];
  attachments?: Record<string, unknown>[];
}

export interface ChatHistory {
  messages: ChatMessage[];
  total: number;
  has_more: boolean;
}

// WebSocket Types

export interface WSMessage {
  type: "state_update" | "agent_status" | "activity_new" | "chat_message" | "connected" | "ping" | "pong";
  data: Record<string, unknown>;
  timestamp?: string;
}

// API Error

export interface APIError {
  error: string;
  detail?: string;
  code?: string;
}
