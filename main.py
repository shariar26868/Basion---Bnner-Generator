# """
# Endpoints
# ─────────
#   POST /generate      → 4 concurrent SSE banner streams
#   POST /regenerate    → SSE stream of 1 edited banner
#   GET  /images/{fn}  → Serve generated PNG files  (mounted StaticFiles)
#   GET  /options       → Enum values for frontend dropdowns
#   GET  /health        → Health check
# """

# from __future__ import annotations

# import asyncio
# import base64
# import io
# import json
# import logging
# import os
# import textwrap
# import time
# import uuid
# from enum import Enum
# from pathlib import Path
# from typing import AsyncGenerator, List, Literal, Optional

# import openai
# from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from fastapi.staticfiles import StaticFiles
# from openai import AsyncOpenAI
# from pydantic import BaseModel, Field, ValidationError
# from app.service.banner.banner_schema import GenerateData, PersonalInfo
# from app.service.banner.banner_router import router as banner_router
# from app.service.banner.banner_utilits import (
#         IMAGE_MODEL,
#         BASE_URL,
#         IMAGES_DIR,
#         cleanup_old_images,
#         _periodic_cleanup,
#         log,
# )
# # ─── FastAPI App ──────────────────────────────────────────────────────────────

# App = FastAPI(
#     title="Banner Maker API",
#     version="5.0.0",
#     description=(
#         "AI-powered banner generation with **gpt-image-1.5** streaming.\n\n"
#         "SSE events carry a `url` field — put it straight into `<img src='...'>`.\n\n"
#         "**Flow:** `POST /generate` → partial preview URLs stream in → final URL arrives → done."
#     ),
# )

# App.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Serve saved PNGs at /images/<filename>
# App.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# App.include_router(banner_router)

# @App.on_event("startup")
# async def startup_event() -> None:
#     cleanup_old_images()
#     asyncio.create_task(_periodic_cleanup())
#     log.info(
#         "v5 started | model=%s | base_url=%s | images_dir=%s",
#         IMAGE_MODEL, BASE_URL, IMAGES_DIR,
#     )


# @App.get("/health", tags=["Utils"], summary="Health check")
# async def health():
#     return {
#         "status":         "ok",
#         "service":        "Banner Maker API",
#         "image_model":    IMAGE_MODEL,
#         "version":        "5.0.0",
#         "base_url":       BASE_URL,
#         "images_dir":     str(IMAGES_DIR),
#         "images_on_disk": len(list(IMAGES_DIR.glob("*.png"))),
#     }


# # ─── Entrypoint ───────────────────────────────────────────────────────────────

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=int(os.getenv("PORT", 8800)),
#     )









"""
Endpoints
─────────
  POST /generate      → 4 concurrent SSE banner streams
  POST /regenerate    → SSE stream of 1 edited banner
  GET  /images/{fn}  → Serve generated PNG files
  GET  /options       → Enum values for frontend dropdowns
  GET  /health        → Health check
"""

from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import os
import textwrap
import time
import uuid
from enum import Enum
from pathlib import Path
from typing import AsyncGenerator, List, Literal, Optional

import openai
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError
from app.service.banner.banner_schema import GenerateData, PersonalInfo
from app.service.banner.banner_router import router as banner_router
from app.service.banner.banner_utilits import (
        IMAGE_MODEL,
        BASE_URL,
        IMAGES_DIR,
        cleanup_old_images,
        _periodic_cleanup,
        log,
)
from app.service.chatbot.chatbot_router import router as chatbot_router
from app.service.chatbot.chatbot_utils import get_documentation_loader

# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Banner Maker API",
    version="5.0.0",
    description=(
        "AI-powered banner generation with **gpt-image-1.5** streaming.\n\n"
        "SSE events carry a `url` field — put it straight into `<img src='...'>`.\n\n"
        "**Flow:** `POST /generate` → partial preview URLs stream in → final URL arrives → done."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ❌ Removed: app.mount("/images", ...) — StaticFiles bypasses CORS middleware
# ✅ Replaced with explicit route below that sets headers on every response

app.include_router(banner_router)
app.include_router(chatbot_router)


# ─── Root Endpoint ────────────────────────────────────────────────────────────

@app.get("/", tags=["Utils"], summary="API Welcome")
async def root():
    """Welcome endpoint with API information"""
    return {
        "service": "Banner Maker API with AI Chatbot",
        "version": "5.0.0",
        "status": "🟢 Running",
        "endpoints": {
            "banner": "/docs#/banner",
            "chatbot": "/docs#/chatbot",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "quick_links": {
            "ask_chatbot": "POST /api/chatbot/ask",
            "stream_answer": "POST /api/chatbot/ask/stream",
            "chatbot_health": "GET /api/chatbot/health",
            "test_chatbot": "Open chatbot_test.html in browser"
        }
    }


# ─── Image Serving (CORS-safe) ────────────────────────────────────────────────

@app.get("/images/{filename}", tags=["Utils"], summary="Serve generated images")
async def serve_image(filename: str):
    """
    Serve PNG files from the images directory.
    Uses FileResponse with explicit CORS + Cache-Control headers to avoid
    304 responses being blocked by the browser's CORS policy.
    """
    file_path = IMAGES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(
        path=str(file_path),
        media_type="image/png",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
        }
    )


# ─── Lifecycle ────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event() -> None:
    cleanup_old_images()
    asyncio.create_task(_periodic_cleanup())
    
    # Load chatbot documentation on startup
    doc_loader = get_documentation_loader()
    doc_loader.load_documentation()
    log.info(
        "Chatbot documentation loaded | sections=%d | chars=%d",
        len(doc_loader.sections),
        len(doc_loader.raw_content),
    )
    
    log.info(
        "v5 started | model=%s | base_url=%s | images_dir=%s",
        IMAGE_MODEL, BASE_URL, IMAGES_DIR,
    )


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Utils"], summary="Health check")
async def health():
    return {
        "status":         "ok",
        "service":        "Banner Maker API",
        "image_model":    IMAGE_MODEL,
        "version":        "5.0.0",
        "base_url":       BASE_URL,
        "images_dir":     str(IMAGES_DIR),
        "images_on_disk": len(list(IMAGES_DIR.glob("*.png"))),
    }


# ─── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8800)),
    )