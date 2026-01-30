"use client";

import { formatDistanceToNow } from "date-fns";
import type { AgentInfo } from "@/types";
import {
  Code,
  Database,
  Shield,
  TestTube,
  Rocket,
  FileText,
  Users,
} from "lucide-react";

interface AgentGridProps {
  agents: AgentInfo[];
}

// Map internal agent names to professional department names
const departmentNames: Record<string, string> = {
  fronti_frontend: "Frontend Development",
  baky_backend: "Backend Development",
  secu_security: "Security & Compliance",
  qai_testing: "Quality Assurance",
  devi_devops: "DevOps & Infrastructure",
  mark_marketing: "Documentation",
};

const departmentIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  fronti_frontend: Code,
  baky_backend: Database,
  secu_security: Shield,
  qai_testing: TestTube,
  devi_devops: Rocket,
  mark_marketing: FileText,
};

const departmentColors: Record<string, string> = {
  fronti_frontend: "bg-blue-100 text-blue-600",
  baky_backend: "bg-green-100 text-green-600",
  secu_security: "bg-red-100 text-red-600",
  qai_testing: "bg-yellow-100 text-yellow-600",
  devi_devops: "bg-orange-100 text-orange-600",
  mark_marketing: "bg-pink-100 text-pink-600",
};

export function AgentGrid({ agents }: AgentGridProps) {
  // Filter out primo and guru - they are not visible to the client
  const visibleDepartments = agents.filter(
    (agent) => !["primo", "guru_supervisor"].includes(agent.name)
  );

  return (
    <div className="card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-dark-500" />
        <h2 className="text-lg font-semibold text-dark-900">Development Team</h2>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
        {visibleDepartments.map((agent) => {
          const Icon = departmentIcons[agent.name] || Code;
          const colorClass = departmentColors[agent.name] || "bg-gray-100 text-gray-600";
          const displayName = departmentNames[agent.name] || agent.alias;

          return (
            <div
              key={agent.name}
              className="card-hover p-4"
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div
                  className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${colorClass}`}
                >
                  <Icon className="w-5 h-5" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Department Name & Status */}
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className={`status-dot status-dot-${agent.status}`} />
                    <span className="font-medium text-dark-900 text-sm truncate">
                      {displayName}
                    </span>
                  </div>

                  {/* Current task or status */}
                  <p className="text-xs text-dark-500 line-clamp-2">
                    {agent.current_task || getStatusText(agent.status)}
                  </p>

                  {/* Progress bar (if working) */}
                  {agent.status === "working" && (
                    <div className="mt-2">
                      <div className="w-full h-1.5 bg-dark-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-500 rounded-full transition-all duration-300"
                          style={{ width: `${agent.progress}%` }}
                        />
                      </div>
                      <div className="flex justify-between mt-1">
                        <span className="text-xs text-dark-400">Progress</span>
                        <span className="text-xs font-medium text-dark-600">
                          {agent.progress}%
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Last update */}
                  {agent.last_activity && (
                    <p className="text-xs text-dark-400 mt-2">
                      Updated {formatDistanceToNow(new Date(agent.last_activity), {
                        addSuffix: false,
                      })} ago
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function getStatusText(status: string): string {
  switch (status) {
    case "working":
      return "Currently in progress";
    case "idle":
      return "Available";
    case "completed":
      return "Phase completed";
    case "blocked":
      return "Pending review";
    default:
      return status;
  }
}
