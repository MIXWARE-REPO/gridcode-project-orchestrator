"use client";

import { formatDistanceToNow } from "date-fns";
import { Code, MessageSquare, Shield, Rocket, CheckCircle } from "lucide-react";
import type { ActivityItem } from "@/types";

interface ActivityTimelineProps {
  activities: ActivityItem[];
  hasMore: boolean;
  onLoadMore: () => void;
}

const categoryIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  code: Code,
  review: CheckCircle,
  deployment: Rocket,
  communication: MessageSquare,
  security: Shield,
};

const categoryColors: Record<string, string> = {
  code: "bg-blue-100 text-blue-600",
  review: "bg-green-100 text-green-600",
  deployment: "bg-orange-100 text-orange-600",
  communication: "bg-purple-100 text-purple-600",
  security: "bg-red-100 text-red-600",
};

// Map agent names to professional department/team names
const agentToTeam: Record<string, string> = {
  Primo: "Project Management",
  Fronti: "Frontend Team",
  Baky: "Backend Team",
  Secu: "Security Team",
  Qai: "QA Team",
  Devi: "DevOps Team",
  Mark: "Documentation",
  Guru: "Technical Review",
};

export function ActivityTimeline({
  activities,
  hasMore,
  onLoadMore,
}: ActivityTimelineProps) {
  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-dark-900 mb-4">
        Activity Timeline
      </h2>

      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = categoryIcons[activity.category] || MessageSquare;
          const colorClass =
            categoryColors[activity.category] || "bg-gray-100 text-gray-600";

          return (
            <div
              key={activity.id}
              className="flex gap-3 animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Icon */}
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${colorClass}`}
              >
                <Icon className="w-4 h-4" />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="font-medium text-dark-900 text-sm">
                    {agentToTeam[activity.agent] || activity.agent}
                  </span>
                  <span className="text-dark-400 text-xs">
                    {formatDistanceToNow(new Date(activity.timestamp), {
                      addSuffix: true,
                    })}
                  </span>
                </div>
                <p className="text-dark-600 text-sm">{activity.description}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Load more button */}
      {hasMore && (
        <button
          onClick={onLoadMore}
          className="btn-secondary w-full mt-4 py-2 text-sm"
        >
          Load more activities
        </button>
      )}

      {activities.length === 0 && (
        <p className="text-center text-dark-500 py-8">
          No activities recorded yet
        </p>
      )}
    </div>
  );
}
