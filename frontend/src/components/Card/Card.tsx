import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import { Card as CardType } from "@/services/api";
import { useBoardStore } from "@/store/boardStore";

const TAG_COLORS: Record<string, string> = {
  backend: "gb-blue-100 text-blue-800",
  api: "bg-green-100 text-green-800",
  database: "bg-purple-100 text-purple-800",
  devops: "bg-red-100 text-red-800",
  concurrency: "bg-amber-100 text-amber-800",
  testing: "bg-indigo-100 text-indigo-800",
};

interface Props {
  card: CardType;
  boardId: number;
}

export default function Card({ card, boardId }: Props) {
  const { deleteCard } = useBoardStore();

  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({ id: card.id, data: { card } });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.4 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className="bg-white border border-gray-200 rounded-lg p-3 cursor-grab hover:border-gray-300 hover:shadow-sm transition-all group"
    >
      <p className="text-sm font-medium text-gray-900 mb-1 lending-snug">
        {card.title}
      </p>
      {card.description && (
        <p className="text-xs text-gray-500 mb-2 line-clamp-2">
          {card.description}
        </p>
      )}
      <div className="flex items-center justify-between">
        {card.tag && (
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${TAG_COLORS[card.tag] || "bg-gray-100 text-gray-700"}`}
          >
            {card.tag}
          </span>
        )}
        <button
          className="text-xs text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity ml-auto"
          onClick={(e) => {
            e.stopPropagation();
            deleteCard(card.id, card.column_id);
          }}
        >
          X
        </button>
      </div>
    </div>
  );
}
