"use Client";
import { useEffect, useState } from "react";
import { useRouter } from "next/router"; // ✅ Pages Router
import { api, Board } from "@/services/api";

export default function DashboardPage() {
  const router = useRouter();
  const [boards, setBoards] = useState<Board[]>([]);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    api.boards
      .list()
      .then(setBoards)
      .catch(() => router.push("/auth"));
  }, []);

  const createBoard = async () => {
    if (!newName.trim()) return;
    const board = await api.boards.create(newName.trim());
    setBoards((prev) => [...prev, board]);
    setNewName("");
    setCreating(false);
    router.push(`/board/${board.id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-100 px-6 py-3 flex items-center justify-between">
        <span className="font-semibold text-gray-900 text-sm">
          <span className="text-blue-500">kanban</span>.dev
        </span>
        <button
          onClick={() => {
            localStorage.clear();
            router.push("/auth");
          }}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Sign out
        </button>
      </nav>
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-xl font-semibold text-gray-900">Your boards</h1>
          <button
            onClick={() => setCreating(true)}
            className="text-sm bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
          >
            + New board
          </button>
        </div>
        {creating && (
          <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4 flex gap-2">
            <input
              autoFocus
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && createBoard()}
              placeholder="Board name..."
              className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
            />
            <button
              onClick={createBoard}
              className="text-sm bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
            >
              Create
            </button>
            <button
              onClick={() => setCreating(false)}
              className="text-sm text-gray-400 px-3 py-2 rounded-lg hover:bg-gray-100"
            >
              Cancel
            </button>
          </div>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {boards.map((board) => (
            <div
              key={board.id}
              onClick={() => router.push(`/board/${board.id}`)}
              className="bg-white border border-gray-200 rounded-xl p-5 cursor-pointer hover:border-blue-300 hover:shadow-sm transition-all group"
            >
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-centr mb-3 group-hover:bg-blue-100 transition-colors">
                <span className="text-blue-500 text-sm">📋</span>
              </div>
              <p className="font-medium text-gray-900 text-sm">{board.name}</p>
              <p className="text-xs text-gray-400 mt-1">Click to open</p>
            </div>
          ))}

          {boards.length === 0 && !creating && (
            <div className="col-span-3 text-center py-16 text-gray-400 text-sm">
              No boards yet. Create your first one!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
