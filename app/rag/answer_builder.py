from typing import Any


class AnswerBuilder:
    def build_context(self, results: list[dict[str, Any]], max_chars: int = 4000) -> str:
        context_parts = []
        total_len = 0

        for item in results:
            text = item.get("text", "").strip()
            if not text:
                continue

            chunk_header = f"[{item.get('file_name', 'unknown')} | chunk {item.get('chunk_order', '?')}]"
            part = f"{chunk_header}\n{text}"

            if total_len + len(part) > max_chars:
                break

            context_parts.append(part)
            total_len += len(part) + 2

        return "\n\n".join(context_parts).strip()

    def build_answer(self, query: str, results: list[dict[str, Any]]) -> str:
        if not results:
            return "Релевантные фрагменты не найдены."

        top = results[0]
        text = top.get("text", "").strip()

        if not text:
            return "Релевантные фрагменты найдены, но текст пустой."

        # MVP: возвращаем наиболее релевантный фрагмент как основу ответа
        # Позже можно заменить на LLM synthesis
        if len(text) > 1200:
            text = text[:1200].rstrip() + "..."

        return (
            f"Наиболее релевантный фрагмент по запросу:\n\n{text}"
        )