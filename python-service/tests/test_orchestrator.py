"""Unit tests for app.agents.orchestrator.chat."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.orchestrator import chat
from app.db.models import Conversation


# ── chat — conversation management ─────────────────────────────────────────


@pytest.mark.asyncio
@patch("app.agents.orchestrator.create_agent")
async def test_chat_creates_new_conversation_when_no_id(
    mock_create_agent, mock_db, mock_result, user_id, user_id_str
):
    """chat should create a new Conversation when no conversation_id is provided."""
    # Agent returns a response message
    response_msg = MagicMock()
    response_msg.content = "Here are some setups."
    mock_agent = AsyncMock()
    mock_agent.ainvoke.return_value = {"messages": [response_msg]}
    mock_create_agent.return_value = mock_agent

    # Simulate flush() generating an ID on the conversation object
    def assign_id(conv):
        if isinstance(conv, Conversation) and conv.id is None:
            conv.id = str(uuid.uuid4())
    mock_db.flush.side_effect = lambda: assign_id(mock_db.add.call_args[0][0])

    response_text, conv_id = await chat(
        mock_db, "screener", user_id, user_id_str, "Find bullish setups"
    )

    assert response_text == "Here are some setups."
    assert conv_id is not None
    # db.add should have been called to persist the new conversation
    mock_db.add.assert_called_once()
    added_conv = mock_db.add.call_args[0][0]
    assert isinstance(added_conv, Conversation)
    assert added_conv.agent_type == "screener"
    assert added_conv.user_id == user_id_str
    mock_db.flush.assert_awaited_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.agents.orchestrator.create_agent")
async def test_chat_loads_existing_conversation(
    mock_create_agent, mock_db, mock_result, sample_conversation, user_id, user_id_str
):
    """chat should load an existing conversation when conversation_id is found."""
    mock_result.scalar_one_or_none.return_value = sample_conversation

    response_msg = MagicMock()
    response_msg.content = "Updated analysis."
    mock_agent = AsyncMock()
    mock_agent.ainvoke.return_value = {"messages": [response_msg]}
    mock_create_agent.return_value = mock_agent

    response_text, conv_id = await chat(
        mock_db, "screener", user_id, user_id_str, "Update analysis",
        conversation_id=sample_conversation.id,
    )

    assert response_text == "Updated analysis."
    assert conv_id == sample_conversation.id
    # Should NOT call db.add since conversation already exists
    mock_db.add.assert_not_called()


@pytest.mark.asyncio
@patch("app.agents.orchestrator.create_agent")
async def test_chat_creates_new_when_conversation_id_not_found(
    mock_create_agent, mock_db, mock_result, user_id, user_id_str
):
    """chat should create a new conversation when the given conversation_id is not in DB."""
    mock_result.scalar_one_or_none.return_value = None

    response_msg = MagicMock()
    response_msg.content = "Starting fresh."
    mock_agent = AsyncMock()
    mock_agent.ainvoke.return_value = {"messages": [response_msg]}
    mock_create_agent.return_value = mock_agent

    response_text, conv_id = await chat(
        mock_db, "analyst", user_id, user_id_str, "Check my positions",
        conversation_id="nonexistent-id",
    )

    assert response_text == "Starting fresh."
    # New conversation was created
    mock_db.add.assert_called_once()
    added_conv = mock_db.add.call_args[0][0]
    assert isinstance(added_conv, Conversation)
    assert added_conv.agent_type == "analyst"
    mock_db.flush.assert_awaited()


@pytest.mark.asyncio
@patch("app.agents.orchestrator.create_agent")
async def test_chat_builds_history_from_stored_messages(
    mock_create_agent, mock_db, mock_result, user_id, user_id_str
):
    """chat should build message history from stored messages (last 20) plus current message."""
    # Create a conversation with 4 stored messages (2 user + 2 assistant)
    conversation = MagicMock(spec=Conversation)
    conversation.id = "conv-123"
    conversation.user_id = user_id_str
    conversation.agent_type = "coach"
    conversation.messages = [
        {"role": "user", "content": "msg1"},
        {"role": "assistant", "content": "resp1"},
        {"role": "user", "content": "msg2"},
        {"role": "assistant", "content": "resp2"},
    ]
    conversation.updated_at = datetime(2025, 1, 15)
    mock_result.scalar_one_or_none.return_value = conversation

    response_msg = MagicMock()
    response_msg.content = "Coach response."
    mock_agent = AsyncMock()
    mock_agent.ainvoke.return_value = {"messages": [response_msg]}
    mock_create_agent.return_value = mock_agent

    await chat(
        mock_db, "coach", user_id, user_id_str, "How am I doing?",
        conversation_id="conv-123",
    )

    # Verify the agent was invoked with the full history (4 stored + 1 new = 5 messages)
    invoke_call = mock_agent.ainvoke.call_args[0][0]
    messages = invoke_call["messages"]
    assert len(messages) == 5  # 4 stored + 1 current
    # Last message should be the current user message
    assert messages[-1].content == "How am I doing?"


@pytest.mark.asyncio
@patch("app.agents.orchestrator.create_agent")
async def test_chat_returns_response_and_conversation_id_tuple(
    mock_create_agent, mock_db, mock_result, user_id, user_id_str
):
    """chat should return a (response_text, conversation_id) tuple."""
    response_msg = MagicMock()
    response_msg.content = "Analysis complete."
    mock_agent = AsyncMock()
    mock_agent.ainvoke.return_value = {"messages": [response_msg]}
    mock_create_agent.return_value = mock_agent

    # Simulate flush() generating an ID on the conversation object
    def assign_id(conv):
        if isinstance(conv, Conversation) and conv.id is None:
            conv.id = str(uuid.uuid4())
    mock_db.flush.side_effect = lambda: assign_id(mock_db.add.call_args[0][0])

    result = await chat(
        mock_db, "analyst", user_id, user_id_str, "Analyze AAPL"
    )

    assert isinstance(result, tuple)
    assert len(result) == 2
    response_text, conv_id = result
    assert response_text == "Analysis complete."
    assert isinstance(conv_id, str)
