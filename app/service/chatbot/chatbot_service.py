"""
Chatbot service for AI-powered Q&A about the website
"""

import logging
from typing import List, Optional, AsyncGenerator
from datetime import datetime
import json

from openai import AsyncOpenAI

from app.service.chatbot.chatbot_schema import (
    ChatRequest, 
    ChatResponse, 
    ChatMessage, 
    ChatMessageRole,
    ChatHistoryItem
)
from app.service.chatbot.chatbot_utils import get_documentation_context

logger = logging.getLogger(__name__)


class ChatbotService:
    """Main chatbot service using OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize chatbot service
        
        Args:
            api_key: OpenAI API key (will be read from env if not provided)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4-turbo"  # or "gpt-3.5-turbo" for cost optimization
        self.conversation_history = []
        
    def _build_system_prompt(self, documentation_context: str) -> str:
        """Build system prompt with documentation context
        
        Args:
            documentation_context: Relevant documentation text
            
        Returns:
            System prompt string
        """
        return f"""You are a helpful AI assistant for the Basione website platform. 
Your role is to provide accurate, detailed answers about the platform based on official documentation.

You have access to the following platform documentation:

<documentation>
{documentation_context}
</documentation>

Guidelines:
1. Answer questions specifically about the Basione platform (frontend, backend, features, technology stack)
2. Base your answers only on the provided documentation
3. If information is not in the documentation, clearly state that
4. Be friendly, professional, and concise
5. For technical questions, provide code examples when relevant
6. Always mention which sections of the documentation support your answer
7. If a question is unclear, ask for clarification

Remember: You are an expert about this specific platform, not a general AI assistant."""

    async def ask_question(self, request: ChatRequest) -> ChatResponse:
        """Process a user question and generate response
        
        Args:
            request: ChatRequest with question and optional history
            
        Returns:
            ChatResponse with answer and metadata
        """
        try:
            # Get relevant documentation context
            doc_context, relevant_sections = get_documentation_context(
                request.question,
                max_chars=3000
            )
            
            if not doc_context:
                return ChatResponse(
                    answer="I don't have documentation loaded. Please try again later.",
                    sources=[],
                    confidence=0.0
                )
            
            # Build messages for API call
            messages = []
            
            # Add conversation history if provided
            if request.conversation_history:
                for msg in request.conversation_history:
                    messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # Add current question
            messages.append({
                "role": "user",
                "content": request.question
            })
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._build_system_prompt(doc_context)
                    },
                    *messages
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            
            # Calculate confidence (simple heuristic)
            confidence = 0.95 if relevant_sections else 0.7
            
            return ChatResponse(
                answer=answer,
                sources=relevant_sections,
                confidence=confidence,
                is_streaming=False
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ChatResponse(
                answer=f"An error occurred while processing your question: {str(e)}",
                sources=[],
                confidence=0.0
            )
    
    async def ask_question_streaming(
        self, 
        request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        """Process question with streaming response
        
        Args:
            request: ChatRequest with question
            
        Yields:
            Streaming response chunks
        """
        try:
            # Get relevant documentation context
            doc_context, relevant_sections = get_documentation_context(
                request.question,
                max_chars=3000
            )
            
            if not doc_context:
                yield json.dumps({
                    "type": "error",
                    "content": "Documentation not loaded"
                })
                return
            
            # Build messages
            messages = []
            
            if request.conversation_history:
                for msg in request.conversation_history:
                    messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            messages.append({
                "role": "user",
                "content": request.question
            })
            
            # Stream response
            async with await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._build_system_prompt(doc_context)
                    },
                    *messages
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            ) as stream:
                # Send metadata first
                yield json.dumps({
                    "type": "metadata",
                    "sources": relevant_sections
                }) + "\n"
                
                # Stream content
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield json.dumps({
                            "type": "content",
                            "data": chunk.choices[0].delta.content
                        }) + "\n"
                
                # Send completion signal
                yield json.dumps({
                    "type": "done",
                    "confidence": 0.95
                }) + "\n"
                
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield json.dumps({
                "type": "error",
                "content": str(e)
            }) + "\n"
    
    def add_to_history(self, question: str, answer: str, sources: List[str]):
        """Add conversation to history
        
        Args:
            question: User's question
            answer: Assistant's answer
            sources: Relevant documentation sources
        """
        item = ChatHistoryItem(
            question=question,
            answer=answer,
            timestamp=datetime.now().isoformat(),
            sources=sources
        )
        # Can extend to store in database
        logger.info(f"Conversation added to history: {question[:50]}...")


# Global service instance
_service_instance: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    """Get or create global chatbot service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ChatbotService()
    return _service_instance
