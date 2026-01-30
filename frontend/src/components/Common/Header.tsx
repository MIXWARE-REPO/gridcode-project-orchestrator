"use client";

import { LogOut, User } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export function Header() {
  const { projectName, logout } = useAuth();

  return (
    <header className="bg-white border-b border-dark-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-primary-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">G</span>
            </div>
            <div>
              <span className="font-semibold text-dark-900">GriPro</span>
              <span className="text-dark-400 text-sm ml-2">Dashboard</span>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            {/* Project name */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-dark-100 rounded-lg">
              <User className="w-4 h-4 text-dark-500" />
              <span className="text-sm font-medium text-dark-700">
                {projectName || "Loading..."}
              </span>
            </div>

            {/* Logout */}
            <button
              onClick={logout}
              className="btn-ghost p-2"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
