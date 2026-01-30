"use client";

import { Calendar, Clock, TrendingUp } from "lucide-react";
import type { ProjectDetail } from "@/types";
import { format } from "date-fns";

interface ProjectHeaderProps {
  project: ProjectDetail;
}

export function ProjectHeader({ project }: ProjectHeaderProps) {
  const statusColors: Record<string, string> = {
    discovery: "bg-purple-100 text-purple-800",
    design: "bg-blue-100 text-blue-800",
    implementation: "bg-yellow-100 text-yellow-800",
    validation: "bg-orange-100 text-orange-800",
    operation: "bg-green-100 text-green-800",
    completed: "bg-green-100 text-green-800",
    paused: "bg-gray-100 text-gray-800",
  };

  return (
    <div className="card p-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Left: Project info */}
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-dark-900">{project.name}</h1>
            <span
              className={`badge ${statusColors[project.status] || "badge-info"}`}
            >
              {project.current_phase}
            </span>
          </div>
          <p className="text-dark-600">{project.description}</p>
          <div className="flex items-center gap-4 mt-3 text-sm text-dark-500">
            <span className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              Started {format(new Date(project.created_at), "MMM d, yyyy")}
            </span>
            {project.estimated_completion && (
              <span className="flex items-center gap-1">
                <TrendingUp className="w-4 h-4" />
                Est. {format(new Date(project.estimated_completion), "MMM d, yyyy")}
              </span>
            )}
          </div>
        </div>

        {/* Right: Progress */}
        <div className="flex items-center gap-6">
          {/* Progress circle */}
          <div className="relative w-20 h-20">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="#e5e7eb"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="#0066FF"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 36}`}
                strokeDashoffset={`${2 * Math.PI * 36 * (1 - project.progress / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-500"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xl font-bold text-dark-900">
                {project.progress}%
              </span>
            </div>
          </div>

          {/* Hours */}
          <div className="text-right">
            <div className="flex items-center gap-1 text-dark-500 text-sm mb-1">
              <Clock className="w-4 h-4" />
              Total Hours
            </div>
            <div className="text-2xl font-bold text-dark-900">
              {project.total_hours.toFixed(1)}h
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
