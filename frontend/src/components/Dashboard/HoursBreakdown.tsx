"use client";

import type { ProjectDetail } from "@/types";

interface HoursBreakdownProps {
  totalHours: number;
  byDepartment: Record<string, number>;
}

const departmentLabels: Record<string, string> = {
  frontend: "Frontend",
  backend: "Backend",
  devops: "DevOps",
  qa: "QA Testing",
  security: "Security",
  marketing: "Docs & Marketing",
};

const departmentColors: Record<string, string> = {
  frontend: "bg-blue-500",
  backend: "bg-green-500",
  devops: "bg-orange-500",
  qa: "bg-yellow-500",
  security: "bg-red-500",
  marketing: "bg-pink-500",
};

export function HoursBreakdown({ totalHours, byDepartment }: HoursBreakdownProps) {
  const departments = Object.entries(byDepartment).sort((a, b) => b[1] - a[1]);

  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-dark-900 mb-4">
        Hours by Department
      </h2>

      {/* Total */}
      <div className="text-center mb-6">
        <span className="text-4xl font-bold text-dark-900">
          {totalHours.toFixed(1)}
        </span>
        <span className="text-dark-500 ml-1">hours total</span>
      </div>

      {/* Stacked bar */}
      <div className="h-4 rounded-full overflow-hidden flex mb-4">
        {departments.map(([dept, hours]) => {
          const percentage = (hours / totalHours) * 100;
          return (
            <div
              key={dept}
              className={`${departmentColors[dept] || "bg-gray-400"} transition-all duration-500`}
              style={{ width: `${percentage}%` }}
              title={`${departmentLabels[dept] || dept}: ${hours.toFixed(1)}h`}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="space-y-2">
        {departments.map(([dept, hours]) => {
          const percentage = ((hours / totalHours) * 100).toFixed(1);
          return (
            <div key={dept} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className={`w-3 h-3 rounded-sm ${
                    departmentColors[dept] || "bg-gray-400"
                  }`}
                />
                <span className="text-sm text-dark-700">
                  {departmentLabels[dept] || dept}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium text-dark-900">
                  {hours.toFixed(1)}h
                </span>
                <span className="text-dark-400 ml-1">({percentage}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
