from datetime import datetime

from app.models.base import CamelModel


class ChatRequest(CamelModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(CamelModel):
    message: str


class ConversationSummary(CamelModel):
    id: str
    agent_type: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
