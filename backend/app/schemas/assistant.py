import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[uuid.UUID] = None

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    answer: str
    conversation_id: uuid.UUID
    provider_status: str
    disclaimer: str

class ConversationResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
