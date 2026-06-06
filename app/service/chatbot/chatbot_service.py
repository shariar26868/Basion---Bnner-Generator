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
    ChatMessageRole
)
from app.service.chatbot.chatbot_utils import (
    get_documentation_context,
    get_aggregate_api_context,
)

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
        
    def _build_system_prompt(
        self,
        documentation_context: str,
        external_context: Optional[str] = None
    ) -> str:
        """Build system prompt with documentation and external API context."""
        external_section = ""
        if external_context:
            external_section = f"\n\nYou also have access to aggregated live data from the external Spandoek API:\n\n<external_data>\n{external_context}\n</external_data>\n"

        return f"""You are a helpful AI assistant for the Spandoek website platform.
Your role is to provide accurate, detailed, and visually well-structured answers about the platform based on official documentation and live aggregated data.

You have access to the following platform documentation:

<documentation>
{documentation_context}
</documentation>{external_section}

Content Formatting Rules (FOLLOW THESE STRICTLY):
1. Start with a brief 1-2 sentence overview of the answer.
2. Use HTML-like tags to structure content — do NOT use plain Markdown.
3. Wrap ALL headings (section titles) in <h4> tags.
4. Wrap ALL feature/sub-feature names in <b> tags.
5. Use blockquotes ("> ...") for brief highlights or definitions, prefixed with a checkmark emoji.
6. Use emojis like ✅, 🔑, 📦, 🔗, 💡, ⭐ as inline highlights.
7. Include code snippets inside <pre><code> blocks when relevant. Only include the 5-6 most important lines.
8. When listing features or files, use dashes or simple bullet format with emojis.
9. End with a 1-sentence tip or best practice when relevant.

Example Answer Style:
<h4>Authentication System</h4>
Sign-in, sign-up, password reset, and OTP verification flows.
Located under <b>spandoek-client/app/auth/</b>.

> ✅ Includes email OTP and password recovery.

Remember: Be friendly, professional, and concise. Base your answers ONLY on the provided documentation and external aggregate data when it is available. If information is not in the documentation or external data, clearly state that."""

    async def ask_question(self, request: ChatRequest) -> ChatResponse:
        """Process a user question and generate response
        
        Args:
            request: ChatRequest with question and optional history
            
        Returns:
            ChatResponse with answer and metadata
        """
        try:
            # Get relevant documentation and external API context
            doc_context, relevant_sections = get_documentation_context(
                request.question,
                max_chars=3000
            )
            external_context = await get_aggregate_api_context()

            if not doc_context and not external_context:
                return ChatResponse(
                    answer="I don't have documentation or external data loaded. Please try again later.",
                    sources=[],
                    confidence=0.0
                )

            # Build messages for API call
            messages = []
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
                        "content": self._build_system_prompt(
                            doc_context,
                            external_context
                        )
                    },
                    *messages
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content

            # Calculate confidence (simple heuristic)
            confidence = 0.95 if relevant_sections or external_context else 0.7
            sources = list(relevant_sections)
            if external_context:
                sources.append("external_api")

            return ChatResponse(
                answer=answer,
                sources=sources,
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
            # Get relevant documentation and external API context
            doc_context, relevant_sections = get_documentation_context(
                request.question,
                max_chars=3000
            )
            external_context = await get_aggregate_api_context()

            if not doc_context and not external_context:
                yield json.dumps({
                    "type": "error",
                    "content": "Documentation and external data not loaded"
                })
                return

            # Build messages
            messages = []
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
                        "content": self._build_system_prompt(
                            doc_context,
                            external_context
                        )
                    },
                    *messages
                ],
                temperature=0.7,
                max_tokens=1000,
                stream=True
            ) as stream:
                # Send metadata first
                metadata_sources = list(relevant_sections)
                if external_context:
                    metadata_sources.append("external_api")

                yield json.dumps({
                    "type": "metadata",
                    "sources": metadata_sources
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
