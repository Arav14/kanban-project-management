import { useDroppable } from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { Column as ColType } from "@/services/api";
import CardComponent from "@/components/Card/Card";
import { useState } from "react";
import { useBoardStore } from "@/store/boardStore";

interface Props {
  column: ColType;
  boardId: number;
}

export default function Column({ column, boardId }: Props) {
  const { setNodeRef, isOver } = useDroppable({ id: column.id });
  const { addCard } = useBoardStore();
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [tag, setTag] = useState("backend");

  const handleAdd = async () => {
    if (!title.trim()) return;
    await addCard(title.trim(), "", column.id, tag);
    setTitle("");
    setAdding(false);
  };

  return (
    <div className="flex flex-col w-60 min-w-[240px]">
      {/*Column header*/}
      <div className="flex items-center justify-between mb-2 px-1">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          {column.title}
        </span>
        <span className="text-xs bg-gray-100 text-gray-500 rounded-full px-2 py-0.5">
          {column.cards.length}
        </span>
      </div>

      {/*Droppable card area*/}
      <div
        ref={setNodeRef}
        className={`flex flex-col gap-2 p-2 rounded-xl min-h-[80px] flex-1 transition-colors ${isOver ? "bg-blue-50 border-2 border-blue-200 border-dashed" : "bg-gray-100"}`}
      >
        <SortableContext
          items={column.cards.map((c) => c.id)}
          strategy={verticalListSortingStrategy}
        >
          {column.cards.map((card) => (
            <CardComponent key={card.id} card={card} boardId={boardId} />
          ))}
        </SortableContext>

        {/* Add card form */}
        {adding ? (
          <div className="bg-white border border-gray-200 rounded-lg p-2 flex flex-col gap-2">
            <input
              autoFocus
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAdd()}
              placeholder="Card title..."
              className="text-sm border-gray-200 rounded px-2 py-1 w-full focus:outline-none focus:border-blue-400"
            />
            <select
              value={tag}
              onChange={(e) => setTag(e.target.value)}
              className="text-xs border border-gray-200 rounded px-2 py-1"
            >
              {[
                "backend",
                "api",
                "database",
                "devops",
                "concurrency",
                "testing",
              ].map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <div className="flex gap-1">
              <button
                onClick={handleAdd}
                className="text-xs bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
              >
                Add
              </button>
              <button
                onClick={() => setAdding(false)}
                className="text-xs text-gray-400 px-2 py-1 rounded hover:bg-gray-100"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setAdding(true)}
            className="text-xs text-gray-400 hover:text-gray-600 hover:bg-white rounded-lg py-1.5 px-2 text-left transition-colors"
          >
            + Add Card
          </button>
        )}
      </div>
    </div>
  );
}
