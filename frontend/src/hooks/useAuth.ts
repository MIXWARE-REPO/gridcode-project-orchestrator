"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/services/api";
import type { TokenResponse } from "@/types";

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  projectId: string | null;
  projectName: string | null;
}

export function useAuth() {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    projectId: null,
    projectName: null,
  });

  useEffect(() => {
    // Check if we have a stored token
    const token = localStorage.getItem("gripro_token");
    const projectData = localStorage.getItem("gripro_project");

    if (token && projectData) {
      try {
        const project = JSON.parse(projectData);
        setState({
          isAuthenticated: true,
          isLoading: false,
          projectId: project.id,
          projectName: project.name,
        });
      } catch {
        setState({
          isAuthenticated: false,
          isLoading: false,
          projectId: null,
          projectName: null,
        });
      }
    } else {
      setState({
        isAuthenticated: false,
        isLoading: false,
        projectId: null,
        projectName: null,
      });
    }
  }, []);

  const login = async (projectCode: string): Promise<TokenResponse> => {
    const response = await api.login({ project_code: projectCode });

    setState({
      isAuthenticated: true,
      isLoading: false,
      projectId: response.project_id,
      projectName: response.project_name,
    });

    return response;
  };

  const logout = () => {
    api.logout();
    setState({
      isAuthenticated: false,
      isLoading: false,
      projectId: null,
      projectName: null,
    });
    router.push("/auth");
  };

  return {
    ...state,
    login,
    logout,
  };
}
