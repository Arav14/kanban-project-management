import { useRouter } from "next/router";
import Board from "@/components/Board/Board";

export default function BoardPage() {
  const router = useRouter();
  const id = Number(router.query.id);
  if (!id) return null;
  return <Board boardId={id} />;
}
