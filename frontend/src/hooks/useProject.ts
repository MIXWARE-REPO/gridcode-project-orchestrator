"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/services/api";
import type { ProjectDetail, ActivitiesResponse } from "@/types";

interface UseProjectReturn {
  project: ProjectDetail | null;
  activities: ActivitiesResponse | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  loadMoreActivities: () => Promise<void>;
}

export function useProject(): UseProjectReturn {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [activities, setActivities] = useState<ActivitiesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProject = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [projectData, activitiesData] = await Promise.all([
        api.getProjectDetails(),
        api.getProjectActivities(10, 0),
      ]);

      setProject(projectData);
      setActivities(activitiesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadMoreActivities = useCallback(async () => {
    if (!activities || !activities.has_more) return;

    try {
      const moreActivities = await api.getProjectActivities(
        10,
        activities.offset + activities.limit
      );

      setActivities({
        ...moreActivities,
        items: [...activities.items, ...moreActivities.items],
      });
    } catch (err) {
      console.error("Failed to load more activities:", err);
    }
  }, [activities]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  return {
    project,
    activities,
    isLoading,
    error,
    refresh: fetchProject,
    loadMoreActivities,
  };
}
