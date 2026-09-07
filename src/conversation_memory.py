"""Bounded, session-scoped conversation memory for the Streamlit RAG app."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationTurn:
    """A minimal user/assistant exchange."""

    question: str
    answer: str


class ConversationMemory:
    """Keep a bounded conversation without persisting user content."""

    def __init__(self, max_turns: int = 5, max_chars_per_field: int = 2000):
        if not isinstance(max_turns, int) or max_turns < 1:
            raise ValueError("max_turns must be a positive integer")
        if not isinstance(max_chars_per_field, int) or max_chars_per_field < 100:
            raise ValueError("max_chars_per_field must be at least 100")
        self.max_turns = max_turns
        self.max_chars_per_field = max_chars_per_field
        self._turns = []

    def add(self, question: str, answer: str) -> None:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("answer must be a non-empty string")
        turn = ConversationTurn(
            question=question.strip()[: self.max_chars_per_field],
            answer=answer.strip()[: self.max_chars_per_field],
        )
        self._turns.append(turn)
        self._turns = self._turns[-self.max_turns :]

    def turns(self):
        return tuple(self._turns)

    def format_for_prompt(self) -> str:
        """Format prior turns as untrusted conversational context."""
        if not self._turns:
            return "No prior conversation."
        blocks = []
        for index, turn in enumerate(self._turns, start=1):
            blocks.append(
                f"Turn {index}\nUser: {turn.question}\nAssistant: {turn.answer}"
            )
        return "\n\n".join(blocks)

    def clear(self) -> None:
        self._turns.clear()

    def __len__(self) -> int:
        return len(self._turns)
