from src.conversation_memory import ConversationMemory


def test_memory_is_bounded_and_keeps_latest_turns():
    memory = ConversationMemory(max_turns=2)
    memory.add("q1", "a1")
    memory.add("q2", "a2")
    memory.add("q3", "a3")
    assert len(memory) == 2
    assert [turn.question for turn in memory.turns()] == ["q2", "q3"]


def test_memory_truncates_large_fields():
    memory = ConversationMemory(max_turns=1, max_chars_per_field=100)
    memory.add("q" * 500, "a" * 500)
    turn = memory.turns()[0]
    assert len(turn.question) == 100
    assert len(turn.answer) == 100


def test_memory_formats_roles_and_preserves_order():
    memory = ConversationMemory(max_turns=3)
    memory.add("first question", "first answer")
    memory.add("second question", "second answer")
    prompt = memory.format_for_prompt()
    assert "Turn 1" in prompt
    assert "User: first question" in prompt
    assert "Assistant: first answer" in prompt
    assert prompt.index("first question") < prompt.index("second question")


def test_clear_removes_session_memory():
    memory = ConversationMemory()
    memory.add("q", "a")
    memory.clear()
    assert len(memory) == 0
    assert memory.format_for_prompt() == "No prior conversation."


def test_memory_rejects_invalid_turns():
    memory = ConversationMemory()
    try:
        memory.add("", "answer")
        assert False
    except ValueError:
        pass
