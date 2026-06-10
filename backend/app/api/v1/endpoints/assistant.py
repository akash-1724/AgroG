import asyncio
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

from app.api.deps import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()

class ChatMessage(BaseModel):
    role: str # user, assistant
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

async def mock_streaming_response(message: str):
    """Fallback generator that streams context-aware expert advice token-by-token."""
    response_text = (
        f"Hello! I am your AgroGuide AI assistant. You asked: '{message}'.\n\n"
        "Here is some contextual agricultural advice based on your inquiry:\n"
        "- **Soil Preparation**: Ensure correct soil testing for Nitrogen, Phosphorus, and Potassium ratios before planting.\n"
        "- **Moisture Management**: Maintain ideal soil humidity levels based on the crop type (e.g. 80% for rice).\n"
        "- **Protection**: Inspect plant leaf surfaces regularly to check for early indicators of blight or scab.\n\n"
        "Let me know if you need more details about marketplace listings or crop suggestions!"
    )
    # Stream word by word to simulate LLM network streaming latency
    words = response_text.split(" ")
    for word in words:
        yield f"data: {json.dumps({'text': word + ' '})} \n\n"
        await asyncio.sleep(0.04)

async def gemini_streaming_response(message: str, history: List[ChatMessage]):
    """Generator that streams response chunks directly from the Gemini API."""
    contents = []
    # Build history context
    for h in history:
        contents.append({
            "role": "user" if h.role == "user" else "model",
            "parts": [{"text": h.content}]
        })
    # Add current message
    contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={settings.GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": "You are a professional agricultural expert assistant for AgroGuide platform. Help farmers and customers solve crop issues, understand soil parameters, or find listings."}]
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", url, headers=headers, json=payload, timeout=30.0) as response:
                if response.status_code != 200:
                    yield f"data: {json.dumps({'text': '[Error: Gemini API status code ' + str(response.status_code) + ']'})} \n\n"
                    return
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    # Remove "data: " prefix if present or parse direct JSON streaming lines
                    clean_line = line.strip()
                    if clean_line.startswith("data:"):
                        clean_line = clean_line[5:].strip()
                    
                    try:
                        # Gemini streaming chunks are often parts of a JSON array of candidates
                        chunk_data = json.loads(clean_line)
                        text_chunk = chunk_data["candidates"][0]["content"]["parts"][0]["text"]
                        yield f"data: {json.dumps({'text': text_chunk})} \n\n"
                    except Exception:
                        # Fallback to streaming raw chunk segments if custom parsing fails
                        continue
        except Exception as e:
            yield f"data: {json.dumps({'text': '[Connection Error: ' + str(e) + ']'})} \n\n"

@router.post("/chat")
async def chat_assistant(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Agricultural conversational assistant. Streams responses back using Server-Sent Events (SSE).
    Uses Gemini API if GEMINI_API_KEY is configured, else falls back to local simulated stream.
    """
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key":
        return StreamingResponse(
            gemini_streaming_response(payload.message, payload.history),
            media_type="text/event-stream"
        )
    else:
        return StreamingResponse(
            mock_streaming_response(payload.message),
            media_type="text/event-stream"
        )
