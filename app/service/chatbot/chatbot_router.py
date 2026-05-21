"""
API routes for chatbot endpoints
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from app.service.chatbot.chatbot_schema import (
    ChatRequest, 
    ChatResponse,
    ChatMessage,
    ChatMessageRole
)
from app.service.chatbot.chatbot_service import get_chatbot_service
from app.service.chatbot.chatbot_utils import (
    get_documentation_loader,
    get_documentation_context
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chatbot",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Ask a question about the website",
    description="Submit a question and get an AI-powered answer based on platform documentation"
)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """
    Ask a question about the Basione website/platform.
    
    The chatbot has access to:
    - Frontend (Next.js) documentation
    - Backend (FastAPI) documentation  
    - AI features and capabilities
    - Technology stack information
    - Installation and setup guides
    
    **Example questions:**
    - "What technologies does the Basione client use?"
    - "How do I set up the project locally?"
    - "What are the main features of the banner editor?"
    - "How does the AI banner generation work?"
    - "What payment methods are supported?"
    """
    try:
        service = get_chatbot_service()
        response = await service.ask_question(request)
        
        # Add to history for potential future use
        service.add_to_history(
            request.question,
            response.answer,
            response.sources
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your question"
        )


@router.post(
    "/ask/stream",
    summary="Ask a question with streaming response",
    description="Get real-time streamed response to your question"
)
async def ask_question_streaming(request: ChatRequest):
    """
    Ask a question and get a streamed response.
    
    This endpoint streams the AI response in real-time, allowing for faster
    perceived response times on the client side.
    
    Response format: Server-Sent Events (SSE) with JSON objects
    """
    try:
        service = get_chatbot_service()
        
        async def generate():
            async for chunk in service.ask_question_streaming(request):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Error in streaming: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred"
        )


@router.get(
    "/documentation/summary",
    summary="Get documentation summary",
    description="Get information about loaded documentation"
)
async def get_documentation_summary():
    """
    Get a summary of the loaded documentation.
    
    Returns information about:
    - Total documentation size
    - Number of sections
    - Available topics
    - Last update time
    """
    try:
        loader = get_documentation_loader()
        
        # Ensure documentation is loaded
        if not loader.raw_content:
            loader.load_documentation()
        
        summary = loader.get_summary()
        
        return {
            "status": "success",
            "summary": summary,
            "message": f"Documentation contains {summary['total_chars']} characters across {summary['total_sections']} sections"
        }
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving documentation summary"
        )


@router.get(
    "/documentation/search",
    summary="Search documentation",
    description="Search for topics in the documentation"
)
async def search_documentation(query: str = Query(..., min_length=1, max_length=200)):
    """
    Search the documentation for relevant content.
    
    **Parameters:**
    - query: Search term or question
    
    **Returns:**
    - Relevant sections from documentation
    - Snippet previews
    """
    try:
        context, sections = get_documentation_context(query, max_chars=5000)
        
        return {
            "query": query,
            "sections_found": sections,
            "context": context,
            "total_matches": len(sections)
        }
        
    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching documentation"
        )


@router.post(
    "/reload-docs",
    summary="Reload documentation",
    description="Manually reload documentation from disk (admin only)",
    tags=["admin"]
)
async def reload_documentation():
    """
    Force reload documentation from disk.
    
    Useful after updating README.md or other documentation files.
    """
    try:
        loader = get_documentation_loader()
        loader.load_documentation()
        
        summary = loader.get_summary()
        
        return {
            "status": "success",
            "message": "Documentation reloaded",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error reloading documentation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reloading documentation"
        )


@router.get(
    "/health",
    summary="Chatbot health check",
    description="Check if chatbot service is operational"
)
async def health_check():
    """Check chatbot service health and documentation status"""
    try:
        loader = get_documentation_loader()
        
        # Try to get context
        context, sections = get_documentation_context("test query")
        
        is_healthy = bool(loader.raw_content)
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "chatbot_service": "operational",
            "documentation_loaded": is_healthy,
            "sections_available": len(loader.sections),
            "timestamp": loader.last_loaded
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
