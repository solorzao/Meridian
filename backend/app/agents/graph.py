import uuid

from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import AGENT_PROMPTS
from app.agents.tools import MARKET_TOOLS, create_profile_tools, create_trade_tools
from app.config import settings


def create_agent(
    agent_type: str,
    db: AsyncSession,
    user_id: uuid.UUID,
    user_id_str: str,
):
    """Create a LangGraph ReAct agent for the given agent type."""
    if agent_type not in AGENT_PROMPTS:
        raise ValueError(f"Unknown agent type: {agent_type}")

    llm = AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        azure_deployment=settings.azure_openai_deployment,
        api_version="2024-10-21",
    )

    tools = list(MARKET_TOOLS)
    tools.extend(create_trade_tools(db, user_id))
    tools.extend(create_profile_tools(db, user_id_str))

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=AGENT_PROMPTS[agent_type],
    )
