"use client";

import { useState, useCallback, useEffect } from "react";
import { api } from "@/services/api";
import type { ChatMessage, ChatResponse } from "@/types";

interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  isSending: boolean;
  suggestions: string[];
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearHistory: () => Promise<void>;
}

export function useChat(projectId: string | null): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load chat history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        setIsLoading(true);
        const history = await api.getChatHistory();
        setMessages(history.messages);
      } catch (err) {
        console.error("Failed to load chat history:", err);
      } finally {
        setIsLoading(false);
      }
    };

    if (projectId) {
      loadHistory();
    }
  }, [projectId]);

  const sendMessage = useCallback(
    async (message: string) => {
      if (!projectId || !message.trim()) return;

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsSending(true);
      setError(null);

      try {
        const response: ChatResponse = await api.sendMessage(message, projectId);

        // Add assistant response
        const assistantMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          role: "assistant",
          content: response.message,
          timestamp: response.timestamp,
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setSuggestions(response.suggestions || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
        // Remove the user message on error
        setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
      } finally {
        setIsSending(false);
      }
    },
    [projectId]
  );

  const clearHistory = useCallback(async () => {
    try {
      await api.clearChatHistory();
      setMessages([]);
      setSuggestions([]);
    } catch (err) {
      console.error("Failed to clear chat history:", err);
    }
  }, []);

  return {
    messages,
    isLoading,
    isSending,
    suggestions,
    error,
    sendMessage,
    clearHistory,
  };
}
