// src/store/boardStore.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { api, BoardDetail, Card, Column } from "@/services/api";

interface BoardState {
  board: BoardDetail | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchBoard: (id: number) => Promise<void>;
  moveCard: (
    cardId: number,
    toColumnId: number,
    toPosition: number,
  ) => Promise<void>;
  addCard: (
    title: string,
    description: string,
    columnId: number,
    tag: string,
  ) => Promise<void>;
  deleteCard: (cardId: number, columnId: number) => Promise<void>;

  // WebSocket event handlers
  applyCardMoved: (
    cardId: number,
    oldColId: number,
    newColId: number,
    position: number,
  ) => void;
  applyCardCreated: (card: Card) => void;
  applyCardDeleted: (cardId: number) => void;
}

export const useBoardStore = create<BoardState>()(
  immer((set, get) => ({
    board: null,
    loading: false,
    error: null,

    fetchBoard: async (id) => {
      set({ loading: true, error: null });
      try {
        const board = await api.boards.get(id);
        set({ board, loading: false });
      } catch (e: any) {
        set({ error: e.message, loading: false });
      }
    },

    moveCard: async (cardId, toColumnId, toPosition) => {
      const board = get().board;
      if (!board) return;

      // Optimistic update — UI moves instantly before API responds
      set((state) => {
        let movingCard: Card | null = null;
        for (const col of state.board!.columns) {
          const idx = col.cards.findIndex((c) => c.id === cardId);
          if (idx !== -1) {
            [movingCard] = col.cards.splice(idx, 1);
            break;
          }
        }
        if (movingCard) {
          movingCard.column_id = toColumnId;
          movingCard.position = toPosition;
          const targetCol = state.board!.columns.find(
            (c) => c.id === toColumnId,
          );
          targetCol?.cards.splice(toPosition, 0, movingCard);
        }
      });

      // Persist to backend
      await api.cards.update(board.id, cardId, {
        column_id: toColumnId,
        position: toPosition,
      });
    },

    addCard: async (title, description, columnId, tag) => {
      const board = get().board;
      if (!board) return;
      const col = board.columns.find((c) => c.id === columnId);
      const position = col?.cards.length || 0;
      await api.cards.create(board.id, {
        title,
        description,
        column_id: columnId,
        tag,
        position,
      });
    },

    deleteCard: async (cardId, columnId) => {
      const board = get().board;
      if (!board) return;
      await api.cards.delete(board.id, cardId);
    },

    // These are called by the WebSocket hook when other users make changes
    applyCardMoved: (cardId, oldColId, newColId, position) => {
      set((state) => {
        const old = state.board?.columns.find((c) => c.id === oldColId);
        if (!old) return;
        const idx = old.cards.findIndex((c) => c.id === cardId);
        if (idx === -1) return;
        const [card] = old.cards.splice(idx, 1);
        card.column_id = newColId;
        card.position = position;
        const target = state.board?.columns.find((c) => c.id === newColId);
        target?.cards.splice(position, 0, card);
      });
    },

    applyCardCreated: (card) => {
      set((state) => {
        const col = state.board?.columns.find((c) => c.id === card.column_id);
        col?.cards.push(card);
      });
    },

    applyCardDeleted: (cardId) => {
      set((state) => {
        for (const col of state.board?.columns || []) {
          const idx = col.cards.findIndex((c) => c.id === cardId);
          if (idx !== -1) {
            col.cards.splice(idx, 1);
            break;
          }
        }
      });
    },
  })),
);
