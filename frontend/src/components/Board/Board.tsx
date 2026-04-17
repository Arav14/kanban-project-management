"use client";
import { useEffect } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from "@dnd-kit/core";
import { useBoardStore } from "@/store/boardStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import ColumnComponent from "@/components/Column/Column";
import { Card } from "@/services/api";
import { useState } from "react";

interface Props {
  boardId: number;
}

export default function Board({ boardId }: Props) {
  const { board, loading, error, fetchBoard, moveCard } = useBoardStore();
  const [activeCard, setActiveCard] = useState<Card | null>(null);

  useWebSocket(boardId);

  useEffect(() => {
    fetchBoard(boardId);
  }, [boardId]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
  );

  const handleDragStart = (event: any) => {
    setActiveCard(event.active.data.current?.card || null);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveCard(null);
    const { active, over } = event;
    if (!over || !board) return;

    const cardId = active.id as number;
    const overId = over.id as number;

    // Find which column the card was dropped into
    const targetColumn = board.columns.find(
      (col) => col.id === overId || col.cards.some((c) => c.id === overId),
    );
    if (!targetColumn) return;

    // Calculate drop position
    const overCardIdx = targetColumn.cards.findIndex((c) => c.id === overId);
    const position = overCardIdx >= 0 ? overCardIdx : targetColumn.cards.length;

    moveCard(cardId, targetColumn.id, position);
  };

  if (loading)
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-sm text-gray-400 animate-pulse">
          Loading board...
        </div>
      </div>
    );

  if (error)
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-sm text-red-400">{error}</div>
      </div>
    );

  if (!board) return null;

  return (
    <div className="flex flex-col h-full">
      {/* Board header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">{board.name}</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            {board.columns.reduce((sum, c) => sum + c.cards.length, 0)} tasks .{" "}
            {board.columns.find((c) => c.title === "Done")?.cards.length || 0}{" "}
            done
          </p>
        </div>
      </div>

      {/* Kanban board */}
      <div className="flex gap-4 p-6 overflow-x-auto flex-1 items-start">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          {board.columns.map((col) => (
            <ColumnComponent key={col.id} column={col} boardId={boardId} />
          ))}

          {/* Drag overlay - Shows card while dragging */}
          <DragOverlay>
            {activeCard && (
              <div className="bg-white border border-blue-300 rounded-lg p-3 shadow-lg w-60 rotate-2">
                <p className="text-sm font-medium text-gray-900">
                  {activeCard.title}
                </p>
              </div>
            )}
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  );
}
