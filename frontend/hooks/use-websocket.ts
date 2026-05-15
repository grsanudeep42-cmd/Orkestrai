"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { WebSocketEvent } from "@/types";

// Get WebSocket URL - detect if accessing remotely and use appropriate host
function getWebSocketUrl() {
  const envUrl = process.env.NEXT_PUBLIC_WS_URL;
  if (envUrl) return envUrl;

  // Use the full hostname from current page URL
  const pageUrl = new URL(window.location.href);
  let host = pageUrl.hostname;

  // If accessing via localhost/127.0.0.1, try to detect if we're on a network
  // by checking if there's a network URL pattern
  if (host === 'localhost' || host === '127.0.0.1') {
    // Check if we can infer the actual network IP
    // Try to get the origin which might have the real IP
    const possibleHosts = ['192.168.29.111', '192.168.1.', '10.0.0.'];
    // For now, use a fixed fallback for your network
    host = '192.168.29.111'; // Your computer's network IP
    console.log('Detected remote access, using network IP:', host);
  }

  const protocol = pageUrl.protocol === 'https:' ? 'wss:' : 'ws:';
  const port = '8000';

  return `${protocol}//${host}:${port}`;
}

export function useWebSocket(projectId: string | null) {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<WebSocketEvent[]>([]);
  const [lastEvent, setLastEvent] = useState<WebSocketEvent | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!projectId || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    const wsUrl = getWebSocketUrl();
    const ws = new WebSocket(`${wsUrl}/api/v1/ws/orchestration/${projectId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected to:", ws.url);
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketEvent = JSON.parse(event.data);
        console.log("WebSocket event:", data);
        
        setLastEvent(data);
        setEvents((prev) => [...prev, data]);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.warn("WebSocket error:", error);
      console.warn("WebSocket readyState:", ws.readyState);
      console.warn("WebSocket URL:", ws.url);
    };

    ws.onclose = (event) => {
      console.log("WebSocket disconnected", event.code, event.reason);
      console.log("WebSocket URL:", ws.url);
      setIsConnected(false);
      // Auto-reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        if (projectId && wsRef.current?.readyState !== WebSocket.OPEN) {
          console.log("Attempting to reconnect...");
          connect();
        }
      }, 3000);
    };
  }, [projectId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setLastEvent(null);
  }, []);

  useEffect(() => {
    if (projectId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [projectId, connect, disconnect]);

  return {
    isConnected,
    events,
    lastEvent,
    connect,
    disconnect,
    clearEvents,
  };
}

// Made with Bob
