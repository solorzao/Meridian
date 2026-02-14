import uuid
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import create_agent
from app.db.models import Conversation


async def chat(
    db: AsyncSession,
    agent_type: str,
    user_id: uuid.UUID,
    user_id_str: str,
    message: str,
    conversation_id: str | None = None,
) -> tuple[str, str]:
    """Run a chat turn with the agent. Returns (response, conversation_id)."""
    # Load or create conversation
    conversation = None
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id_str,
            )
        )
        conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            user_id=user_id_str,
            agent_type=agent_type,
            title=message[:50] + "..." if len(message) > 50 else message,
            messages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conversation)
        await db.flush()  # Get the generated ID

    # Build message history from conversation
    history = []
    stored_messages = conversation.messages or []
    for msg in stored_messages[-20:]:  # Last 20 messages
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))

    # Add current message
    history.append(HumanMessage(content=message))

    # Create agent and invoke
    agent = create_agent(agent_type, db, user_id, user_id_str)
    result = await agent.ainvoke({"messages": history})

    # Extract response
    response_message = result["messages"][-1]
    response_text = response_message.content

    # Save messages to conversation
    now = datetime.utcnow().isoformat()
    stored_messages.append({"role": "user", "content": message, "timestamp": now})
    stored_messages.append({"role": "assistant", "content": response_text, "timestamp": now})
    conversation.messages = stored_messages
    conversation.updated_at = datetime.utcnow()

    await db.commit()

    return response_text, conversation.id
