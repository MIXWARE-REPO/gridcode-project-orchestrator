"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { KeyRound, ArrowRight, AlertCircle } from "lucide-react";

export default function AuthPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [projectCode, setProjectCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectCode.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      await login(projectCode);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid project code");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-primary-900 flex flex-col">
      {/* Header */}
      <header className="p-6">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">G</span>
          </div>
          <span className="text-white font-semibold text-xl">GriPro</span>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Card */}
          <div className="card p-8 animate-fade-in">
            {/* Icon */}
            <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <KeyRound className="w-8 h-8 text-primary-500" />
            </div>

            {/* Title */}
            <h1 className="text-2xl font-bold text-center text-dark-900 mb-2">
              Access Your Project
            </h1>
            <p className="text-dark-600 text-center mb-8">
              Enter your project code to view your dashboard
            </p>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="projectCode"
                  className="block text-sm font-medium text-dark-700 mb-2"
                >
                  Project Code
                </label>
                <input
                  id="projectCode"
                  type="text"
                  value={projectCode}
                  onChange={(e) => setProjectCode(e.target.value.toUpperCase())}
                  placeholder="e.g., GRIP-001"
                  className="input text-center text-lg tracking-wider uppercase"
                  disabled={isLoading}
                  autoFocus
                />
              </div>

              {/* Error message */}
              {error && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm animate-slide-up">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading || !projectCode.trim()}
                className="btn-primary w-full py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Verifying...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    View Dashboard
                    <ArrowRight className="w-5 h-5" />
                  </span>
                )}
              </button>
            </form>

            {/* Demo hint */}
            <div className="mt-6 pt-6 border-t border-dark-200">
              <p className="text-sm text-dark-500 text-center">
                Demo access: Use code{" "}
                <button
                  onClick={() => setProjectCode("DEMO-123")}
                  className="font-mono text-primary-500 hover:text-primary-600 font-medium"
                >
                  DEMO-123
                </button>
              </p>
            </div>
          </div>

          {/* Footer text */}
          <p className="text-center text-dark-400 text-sm mt-6">
            Complete transparency at every stage of your project
          </p>
        </div>
      </main>
    </div>
  );
}
