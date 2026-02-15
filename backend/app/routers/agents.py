import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import orchestrator
from app.auth import get_current_user_id, get_current_user_id_string
from app.db.database import get_db
from app.db.models import Conversation
from app.middleware.rate_limiter import limiter
from app.models.agent_schemas import ChatRequest, ChatResponse, ConversationSummary

router = APIRouter(prefix="/api/agents", tags=["agents"])

VALID_AGENT_TYPES = {"screener", "analyst", "coach"}


@router.post("/{agent_type}/chat", response_model=ChatResponse, response_model_by_alias=True)
@limiter.limit("20/minute")
async def chat(
    http_request: Request,
    agent_type: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    user_id_str: str = Depends(get_current_user_id_string),
):
    if agent_type.lower() not in VALID_AGENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent type. Must be one of: {', '.join(VALID_AGENT_TYPES)}",
        )

    response_text, _ = await orchestrator.chat(
        db, agent_type.lower(), user_id, user_id_str, request.message, request.conversation_id
    )
    return ChatResponse(message=response_text)


@router.get(
    "/conversations",
    response_model=list[ConversationSummary],
    response_model_by_alias=True,
)
async def get_conversations(
    agent_type: str | None = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user_id_str: str = Depends(get_current_user_id_string),
):
    query = select(Conversation).where(Conversation.user_id == user_id_str)
    if agent_type:
        query = query.where(Conversation.agent_type == agent_type)
    query = query.order_by(Conversation.updated_at.desc()).limit(limit)
    result = await db.execute(query)
    conversations = result.scalars().all()
    return [
        ConversationSummary(
            id=c.id,
            agent_type=c.agent_type,
            title=c.title,
            message_count=len(c.messages) if c.messages else 0,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    user_id_str: str = Depends(get_current_user_id_string),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id_str,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": conversation.id,
        "userId": conversation.user_id,
        "agentType": conversation.agent_type,
        "title": conversation.title,
        "messages": conversation.messages,
        "createdAt": conversation.created_at.isoformat(),
        "updatedAt": conversation.updated_at.isoformat(),
    }


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    user_id_str: str = Depends(get_current_user_id_string),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id_str,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conversation)
    await db.commit()
