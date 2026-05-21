from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ChatMessageRole(str, Enum):
    """Role types for chat messages"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: ChatMessageRole
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chatbot queries"""
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Your question about the website"
    )


class ChatResponse(BaseModel):
    """Response model from chatbot"""
    answer: str = Field(description="AI-generated answer to the question")
    sources: List[str] = Field(
        default=[],
        description="Documentation sections referenced"
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence level of the answer (0-1)"
    )
    is_streaming: bool = Field(
        default=False,
        description="Whether this is a streaming response"
    )


class ChatHistoryItem(BaseModel):
    """Store conversation history"""
    question: str
    answer: str
    timestamp: str
    sources: List[str] = []


class DocumentationContext(BaseModel):
    """Documentation loaded from project"""
    content: str
    sections: dict
    total_chars: int
    last_updated: str
