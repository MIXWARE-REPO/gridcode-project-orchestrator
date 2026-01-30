"use client";

import { Check, Circle, Loader } from "lucide-react";
import type { ProjectPhase } from "@/types";

interface PhaseTrackerProps {
  phases: ProjectPhase[];
}

export function PhaseTracker({ phases }: PhaseTrackerProps) {
  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-dark-900 mb-6">Project Phases</h2>

      <div className="space-y-4">
        {phases.map((phase, index) => (
          <div key={phase.number} className="phase-indicator">
            <div className="flex items-start gap-4">
              {/* Status icon */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  phase.status === "completed"
                    ? "bg-green-500"
                    : phase.status === "in_progress"
                    ? "bg-primary-500"
                    : "bg-dark-200"
                }`}
              >
                {phase.status === "completed" ? (
                  <Check className="w-4 h-4 text-white" />
                ) : phase.status === "in_progress" ? (
                  <Loader className="w-4 h-4 text-white animate-spin" />
                ) : (
                  <Circle className="w-4 h-4 text-dark-400" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 pb-4">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-dark-400">
                      0{phase.number}
                    </span>
                    <h3
                      className={`font-medium ${
                        phase.status === "pending"
                          ? "text-dark-400"
                          : "text-dark-900"
                      }`}
                    >
                      {phase.name}
                    </h3>
                  </div>
                  {phase.status !== "pending" && (
                    <span className="text-sm font-medium text-dark-600">
                      {phase.progress}%
                    </span>
                  )}
                </div>

                <p className="text-sm text-dark-500 mb-2">{phase.description}</p>

                {/* Progress bar */}
                {phase.status !== "pending" && (
                  <div className="w-full h-1.5 bg-dark-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        phase.status === "completed"
                          ? "bg-green-500"
                          : "bg-primary-500"
                      }`}
                      style={{ width: `${phase.progress}%` }}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
