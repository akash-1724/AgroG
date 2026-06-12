import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import httpx

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.assistant import AssistantConversation, AssistantMessage
from app.schemas.assistant import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from app.core.config import settings

router = APIRouter()

SAFETY_DISCLAIMER = (
    "Advisory only. AgroGuide AI Assistant recommendations are not scientifically validated. "
    "Consult certified regional agronomists and safety data sheets before applying chemical agents."
)

DANGEROUS_PROMPT_REJECT = (
    "I cannot provide guidelines on toxic chemical formulations, lethal chemical dosages, "
    "or illegal agricultural practices. Please consult local agricultural extension officers for safe usage guidelines."
)

def is_safe_message(text: str) -> bool:
    text_lower = text.lower()
    dangerous_terms = [
        "lethal dose", "poison", "toxic concentration", "illegal chemical",
        "kill crops", "sabotage", "homemade pesticide", "explosive fertilizer"
    ]
    return not any(term in text_lower for term in dangerous_terms)

@router.post("/chat", response_model=ChatResponse)
async def chat_assistant(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Interact with the AI assistant. Returns JSON response containing assistant's answer.
    Saves conversation history to Postgres DB.
    """
    # 1. Safety check
    if not is_safe_message(payload.message):
        # Save user query
        conversation_id = payload.conversation_id or uuid.uuid4()
        
        # Ensure conversation exists
        if payload.conversation_id:
            convo_res = await db.execute(select(AssistantConversation).where(AssistantConversation.id == payload.conversation_id))
            convo = convo_res.scalars().first()
            if convo and convo.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to access this conversation.")
            if not convo:
                convo = AssistantConversation(id=conversation_id, user_id=current_user.id)
                db.add(convo)
        else:
            convo = AssistantConversation(id=conversation_id, user_id=current_user.id)
            db.add(convo)
            
        user_msg = AssistantMessage(
            conversation_id=convo.id,
            role="user",
            content=payload.message
        )
        assistant_msg = AssistantMessage(
            conversation_id=convo.id,
            role="assistant",
            content=DANGEROUS_PROMPT_REJECT
        )
        db.add(user_msg)
        db.add(assistant_msg)
        await db.commit()
        
        return ChatResponse(
            answer=DANGEROUS_PROMPT_REJECT,
            conversation_id=convo.id,
            provider_status="safety_block",
            disclaimer=SAFETY_DISCLAIMER
        )

    # 2. Get or create conversation
    if payload.conversation_id:
        convo_res = await db.execute(
            select(AssistantConversation)
            .where(AssistantConversation.id == payload.conversation_id)
            .options(selectinload(AssistantConversation.messages))
        )
        convo = convo_res.scalars().first()
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        if convo.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this conversation.")
    else:
        convo = AssistantConversation(user_id=current_user.id)
        db.add(convo)
        await db.commit()
        await db.refresh(convo)

    # Save user message
    user_msg = AssistantMessage(
        conversation_id=convo.id,
        role="user",
        content=payload.message
    )
    db.add(user_msg)
    await db.commit()

    # Retrieve message history for context
    history_res = await db.execute(
        select(AssistantMessage)
        .where(AssistantMessage.conversation_id == convo.id)
        .order_by(AssistantMessage.created_at.asc())
    )
    history_msgs = history_res.scalars().all()

    # Determine Provider
    provider = "demo"
    answer = ""
    
    # Simple rule-based mock answers for local fallback demo
    fallback_answers = {
        "soil": "Ensure correct soil testing for N-P-K ratios and pH level (ideally between 6.0 and 7.0 for general crops) before planting.",
        "pesticide": "For pest management, we advise organic neem oil sprays and crop rotation over strong chemical solutions. Refer to regional warnings.",
        "fertilizer": "NPK fertilizer application should match the crop type requirements. Rice requires high nitrogen while pulses require phosphorus.",
        "blight": "Early blight can be managed by pruning lower leaves, avoiding overhead watering, and using organic copper-based fungicides."
    }
    
    has_api_key = settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key"
    
    if has_api_key:
        provider = "gemini"
        # Query Gemini API
        contents = []
        for msg in history_msgs:
            contents.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [{"text": msg.content}]
            })
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload_data = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": "You are a professional agricultural expert assistant for AgroGuide platform. Help farmers solve crop issues, understand soil stats, and discover listings. Do not provide dangerous pesticide, chemical, legal, or financial advice. Be advisory and clearly state uncertainty."}]
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(url, headers=headers, json=payload_data, timeout=15.0)
                if res.status_code == 200:
                    data = res.json()
                    answer = data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    provider = "demo"
                    answer = f"Gemini API Error (Status {res.status_code}). Fallback: "
            except Exception as e:
                provider = "demo"
                answer = f"Gemini API connection error: {str(e)}. Fallback: "

    if provider == "demo":
        # Rule based heuristics lookup
        msg_lower = payload.message.lower()
        matched_fallback = False
        for kw, ans in fallback_answers.items():
            if kw in msg_lower:
                answer += f"Baseline Demo Mode: {ans}"
                matched_fallback = True
                break
        if not matched_fallback:
            answer += (
                f"Hello! I am your AgroGuide AI assistant (Demo Mode). You asked: '{payload.message}'.\n\n"
                "I am currently operating in baseline demo mode. For accurate results, configure a valid GEMINI_API_KEY in the environment.\n"
                "To optimize farming: inspect foliage regularly, balance soil pH, and calculate fertilizer dosages carefully."
            )

    # Save Assistant message
    assistant_msg = AssistantMessage(
        conversation_id=convo.id,
        role="assistant",
        content=answer
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatResponse(
        answer=answer,
        conversation_id=convo.id,
        provider_status=provider,
        disclaimer=SAFETY_DISCLAIMER
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List assistant chat conversations for authenticated user."""
    query = (
        select(AssistantConversation)
        .where(AssistantConversation.user_id == current_user.id)
        .options(selectinload(AssistantConversation.messages))
        .order_by(AssistantConversation.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/conversations/{id}", response_model=ConversationResponse)
async def get_conversation_details(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full message log for a single conversation."""
    query = (
        select(AssistantConversation)
        .where(AssistantConversation.id == id, AssistantConversation.user_id == current_user.id)
        .options(selectinload(AssistantConversation.messages))
    )
    result = await db.execute(query)
    convo = result.scalars().first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return convo
