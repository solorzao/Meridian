"""Tests for the agent graph factory (app.agents.graph)."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.agents.graph import create_agent


@pytest.fixture
def user_id():
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def user_id_str():
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def mock_db():
    return MagicMock()


class TestCreateAgent:
    """Tests for create_agent()."""

    @patch("app.agents.graph.settings")
    @patch("app.agents.graph.AzureChatOpenAI")
    @patch("app.agents.graph.create_react_agent")
    def test_returns_agent_for_screener(
        self, mock_create_react, mock_llm_class, mock_settings, mock_db, user_id, user_id_str
    ):
        mock_settings.azure_openai_endpoint = "https://test.openai.azure.com"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_deployment = "gpt-4o"
        sentinel = MagicMock()
        mock_create_react.return_value = sentinel

        result = create_agent("screener", mock_db, user_id, user_id_str)

        assert result is sentinel
        mock_create_react.assert_called_once()

    @patch("app.agents.graph.settings")
    @patch("app.agents.graph.AzureChatOpenAI")
    @patch("app.agents.graph.create_react_agent")
    def test_returns_agent_for_analyst(
        self, mock_create_react, mock_llm_class, mock_settings, mock_db, user_id, user_id_str
    ):
        mock_settings.azure_openai_endpoint = "https://test.openai.azure.com"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_deployment = "gpt-4o"

        result = create_agent("analyst", mock_db, user_id, user_id_str)

        assert result is mock_create_react.return_value
        mock_create_react.assert_called_once()

    @patch("app.agents.graph.settings")
    @patch("app.agents.graph.AzureChatOpenAI")
    @patch("app.agents.graph.create_react_agent")
    def test_returns_agent_for_coach(
        self, mock_create_react, mock_llm_class, mock_settings, mock_db, user_id, user_id_str
    ):
        mock_settings.azure_openai_endpoint = "https://test.openai.azure.com"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_deployment = "gpt-4o"

        result = create_agent("coach", mock_db, user_id, user_id_str)

        assert result is mock_create_react.return_value
        mock_create_react.assert_called_once()

    @patch("app.agents.graph.settings")
    @patch("app.agents.graph.AzureChatOpenAI")
    @patch("app.agents.graph.create_react_agent")
    def test_raises_for_unknown_agent_type(
        self, mock_create_react, mock_llm_class, mock_settings, mock_db, user_id, user_id_str
    ):
        with pytest.raises(ValueError, match="Unknown agent type: invalid"):
            create_agent("invalid", mock_db, user_id, user_id_str)

        mock_create_react.assert_not_called()

    @patch("app.agents.graph.settings")
    @patch("app.agents.graph.AzureChatOpenAI")
    @patch("app.agents.graph.create_react_agent")
    def test_agent_created_with_correct_tool_count(
        self, mock_create_react, mock_llm_class, mock_settings, mock_db, user_id, user_id_str
    ):
        """Agent should receive MARKET_TOOLS(4) + trade_tools(4) + profile_tools(2) = 10 tools."""
        mock_settings.azure_openai_endpoint = "https://test.openai.azure.com"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_deployment = "gpt-4o"

        create_agent("screener", mock_db, user_id, user_id_str)

        call_args = mock_create_react.call_args
        # create_react_agent is called as: create_react_agent(model=..., tools=..., prompt=...)
        tools = call_args.kwargs.get("tools")
        if tools is None and len(call_args.args) > 1:
            tools = call_args.args[1]
        assert len(tools) == 10
