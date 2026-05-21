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
        description="User's question about the website/platform"
    )
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous conversation context (optional for multi-turn)"
    )
    max_tokens: Optional[int] = Field(
        default=500,
        description="Maximum tokens in response",
        le=2000
    )
    temperature: Optional[float] = Field(
        default=0.7,
        description="Response creativity level (0-1)",
        ge=0,
        le=1
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
