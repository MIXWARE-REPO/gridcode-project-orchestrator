"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { RefreshCw, AlertCircle, Loader } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { useProject } from "@/hooks/useProject";
import { Header } from "@/components/Common/Header";
import { ProjectHeader } from "@/components/Dashboard/ProjectHeader";
import { PhaseTracker } from "@/components/Dashboard/PhaseTracker";
import { AgentGrid } from "@/components/Dashboard/AgentGrid";
import { ActivityTimeline } from "@/components/Dashboard/ActivityTimeline";
import { HoursBreakdown } from "@/components/Dashboard/HoursBreakdown";
import { ChatPanel } from "@/components/Chat/ChatPanel";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, projectId, projectName } = useAuth();
  const { project, activities, isLoading, error, refresh, loadMoreActivities } = useProject();
  const [chatOpen, setChatOpen] = useState(false);

  // Redirect to auth if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth");
    }
  }, [authLoading, isAuthenticated, router]);

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    );
  }

  // Show loading while fetching project
  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
              <p className="text-dark-600">Loading your project...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Show error state
  if (error || !project) {
    return (
      <div className="min-h-screen bg-dark-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="w-8 h-8 text-red-500" />
              </div>
              <h2 className="text-xl font-semibold text-dark-900 mb-2">
                Failed to load project
              </h2>
              <p className="text-dark-600 mb-4">
                {error || "Project data could not be retrieved"}
              </p>
              <button onClick={refresh} className="btn-primary">
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Refresh button */}
        <div className="flex justify-end mb-4">
          <button
            onClick={refresh}
            className="btn-ghost text-sm"
            title="Refresh data"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
        </div>

        {/* Project Header */}
        <div className="mb-6 animate-fade-in">
          <ProjectHeader project={project} />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Phases & Agents */}
          <div className="lg:col-span-2 space-y-6">
            <div className="animate-slide-up" style={{ animationDelay: "100ms" }}>
              <PhaseTracker phases={project.phases} />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: "200ms" }}>
              <AgentGrid agents={project.agents} />
            </div>
          </div>

          {/* Right Column - Hours & Activity */}
          <div className="space-y-6">
            <div className="animate-slide-up" style={{ animationDelay: "150ms" }}>
              <HoursBreakdown
                totalHours={project.total_hours}
                byDepartment={project.hours_by_department}
              />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: "250ms" }}>
              <ActivityTimeline
                activities={activities?.items || []}
                hasMore={activities?.has_more || false}
                onLoadMore={loadMoreActivities}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Chat Panel */}
      <ChatPanel
        projectId={projectId}
        projectName={projectName || project.name}
        isOpen={chatOpen}
        onToggle={() => setChatOpen(!chatOpen)}
      />
    </div>
  );
}
