"use client";

import { useEffect, useRef } from "react";
import { useBoardStore } from "@/store/boardStore";

const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws";

export function useWebSocket(boardId: number) {
  const ws = useRef<WebSocket | null>(null);

  const { applyCardMoved, applyCardCreated, applyCardDeleted } =
    useBoardStore();

  useEffect(() => {
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      ws.current = new WebSocket(`${WS_URL}/${boardId}`);

      ws.current.onmessage = (e) => {
        const event = JSON.parse(e.data);

        switch (event.type) {
          case "card_moved":
            applyCardMoved(
              event.card_id,
              event.old_column_id,
              event.new_column_id,
              event.position,
            );
            break;

          case "card_deleted":
            applyCardDeleted(event.card_id);
            break;
        }
      };

      ws.current.onclose = () => {
        console.log("WS closed. Reconnecting...");
        reconnectTimeout = setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      ws.current?.close();
    };
  }, [boardId]);
}
