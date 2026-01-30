"use client";

import { useState, useRef, useEffect } from "react";
import {
  MessageSquare,
  X,
  Send,
  User,
  Trash2,
  Loader,
  CircleUser,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { useChat } from "@/hooks/useChat";
import type { ChatMessage } from "@/types";
import clsx from "clsx";

interface ChatPanelProps {
  projectId: string | null;
  projectName: string;
  isOpen: boolean;
  onToggle: () => void;
}

export function ChatPanel({
  projectId,
  projectName,
  isOpen,
  onToggle,
}: ChatPanelProps) {
  const {
    messages,
    isLoading,
    isSending,
    suggestions,
    error,
    sendMessage,
    clearHistory,
  } = useChat(projectId);

  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    const message = input;
    setInput("");
    await sendMessage(message);
  };

  const handleSuggestionClick = async (suggestion: string) => {
    if (isSending) return;
    await sendMessage(suggestion);
  };

  return (
    <>
      {/* Chat Toggle Button (visible when panel is closed) */}
      <button
        onClick={onToggle}
        className={clsx(
          "fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300",
          isOpen
            ? "bg-dark-700 scale-0 opacity-0"
            : "bg-primary-500 hover:bg-primary-600 scale-100 opacity-100"
        )}
        title="Chat with your Project Manager"
      >
        <MessageSquare className="w-6 h-6 text-white" />
        <span className="absolute -top-1 -right-1 w-4 h-4 bg-accent-success rounded-full border-2 border-white" />
      </button>

      {/* Chat Panel (sliding from right) */}
      <div
        className={clsx(
          "fixed top-0 right-0 h-full w-full sm:w-[400px] bg-white shadow-2xl z-50 flex flex-col transition-transform duration-300 ease-out",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-dark-200 bg-gradient-to-r from-primary-500 to-primary-600">
          <div className="flex items-center gap-3">
            {/* Avatar with initials instead of bot icon */}
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-primary-600 font-bold text-sm">
              HP
            </div>
            <div>
              <h3 className="font-semibold text-white">Henry Primo</h3>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <p className="text-xs text-white/80">Project Manager</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearHistory}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              title="Clear conversation"
            >
              <Trash2 className="w-4 h-4 text-white/80" />
            </button>
            <button
              onClick={onToggle}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>

        {/* Project context indicator */}
        <div className="px-4 py-2 bg-dark-50 border-b border-dark-200">
          <p className="text-xs text-dark-500">
            Project: <span className="font-medium text-dark-700">{projectName}</span>
          </p>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Welcome message if no messages */}
          {messages.length === 0 && !isLoading && (
            <div className="text-center py-6 animate-fade-in">
              <div className="w-14 h-14 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3 text-primary-600 font-bold text-lg">
                HP
              </div>
              <h4 className="font-medium text-dark-900 mb-1">
                Hey, soy Primo
              </h4>
              <p className="text-dark-500 text-sm max-w-xs mx-auto">
                Manejo tu proyecto. Preguntame sobre el estado, avances, o cualquier duda que tengas.
              </p>
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div className="flex justify-center py-8">
              <Loader className="w-6 h-6 text-primary-500 animate-spin" />
            </div>
          )}

          {/* Messages */}
          {messages.map((message, index) => (
            <MessageBubble
              key={message.id}
              message={message}
              isLast={index === messages.length - 1}
            />
          ))}

          {/* Typing indicator when sending */}
          {isSending && (
            <div className="flex items-start gap-2 animate-fade-in">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 text-primary-600 font-semibold text-xs">
                HP
              </div>
              <div className="chat-bubble-assistant flex items-center gap-1 py-3">
                <span className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" />
                <span
                  className="w-2 h-2 bg-dark-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                />
                <span
                  className="w-2 h-2 bg-dark-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                />
              </div>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 animate-slide-up">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && !isSending && (
          <div className="px-4 py-2 border-t border-dark-100 bg-dark-50">
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-xs px-3 py-1.5 bg-white border border-dark-200 rounded-full text-dark-700 hover:bg-dark-100 hover:border-dark-300 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input area */}
        <form
          onSubmit={handleSubmit}
          className="p-4 border-t border-dark-200 bg-white"
        >
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu mensaje..."
              className="input flex-1 py-2.5"
              disabled={isSending || !projectId}
            />
            <button
              type="submit"
              disabled={!input.trim() || isSending || !projectId}
              className="btn-primary p-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>

      {/* Backdrop (mobile only) */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 sm:hidden"
          onClick={onToggle}
        />
      )}
    </>
  );
}

// Message Bubble Component
function MessageBubble({
  message,
  isLast,
}: {
  message: ChatMessage;
  isLast: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={clsx(
        "flex items-start gap-2",
        isUser ? "flex-row-reverse" : "flex-row",
        isLast && "animate-slide-up"
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
          isUser ? "bg-dark-200" : "bg-primary-100"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-dark-600" />
        ) : (
          <span className="text-primary-600 font-semibold text-xs">HP</span>
        )}
      </div>

      {/* Message content */}
      <div
        className={clsx(
          isUser ? "chat-bubble-user" : "chat-bubble-assistant"
        )}
      >
        <div
          className="text-sm whitespace-pre-wrap"
          dangerouslySetInnerHTML={{
            __html: formatMessageContent(message.content),
          }}
        />
        <p
          className={clsx(
            "text-xs mt-1",
            isUser ? "text-white/60" : "text-dark-400"
          )}
        >
          {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
        </p>
      </div>
    </div>
  );
}

// Format message content (basic markdown support)
function formatMessageContent(content: string): string {
  return content
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br />");
}
