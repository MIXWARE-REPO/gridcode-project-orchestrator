/**
 * API Service for GriPro Dashboard
 * Handles all HTTP requests to the backend
 */

import type {
  ActivitiesResponse,
  APIError,
  ChatHistory,
  ChatRequest,
  ChatResponse,
  LoginRequest,
  ProjectDetail,
  TokenResponse,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIService {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage on init (client-side only)
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("gripro_token");
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: APIError = await response.json().catch(() => ({
        error: "Request failed",
        detail: response.statusText,
      }));

      if (response.status === 401) {
        // Token expired or invalid
        this.clearAuth();
        if (typeof window !== "undefined") {
          window.location.href = "/auth";
        }
      }

      throw new Error(error.detail || error.error);
    }

    return response.json();
  }

  // Auth

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("gripro_token", token);
    }
  }

  clearAuth() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("gripro_token");
      localStorage.removeItem("gripro_project");
    }
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await this.request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });

    this.setToken(response.access_token);

    if (typeof window !== "undefined") {
      localStorage.setItem("gripro_project", JSON.stringify({
        id: response.project_id,
        name: response.project_name,
      }));
    }

    return response;
  }

  logout() {
    this.clearAuth();
  }

  // Projects

  async getProjectDetails(): Promise<ProjectDetail> {
    return this.request<ProjectDetail>("/api/projects/current");
  }

  async getProjectActivities(
    limit = 10,
    offset = 0
  ): Promise<ActivitiesResponse> {
    return this.request<ActivitiesResponse>(
      `/api/projects/current/activities?limit=${limit}&offset=${offset}`
    );
  }

  async getProjectHours(): Promise<{
    total_hours: number;
    by_department: Record<string, number>;
    last_updated: string;
  }> {
    return this.request("/api/projects/current/hours");
  }

  // Chat

  async sendMessage(message: string, projectId: string): Promise<ChatResponse> {
    const data: ChatRequest = {
      message,
      project_id: projectId,
    };

    return this.request<ChatResponse>("/api/chat/primo", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getChatHistory(limit = 50, offset = 0): Promise<ChatHistory> {
    return this.request<ChatHistory>(
      `/api/chat/history?limit=${limit}&offset=${offset}`
    );
  }

  async clearChatHistory(): Promise<void> {
    await this.request("/api/chat/history", {
      method: "DELETE",
    });
  }

  // Health

  async healthCheck(): Promise<{ status: string }> {
    return this.request("/api/health");
  }
}

// Export singleton instance
export const api = new APIService();
