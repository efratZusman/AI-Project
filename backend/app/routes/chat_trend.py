# backend/app/routes/chat_trend.py
from fastapi import APIRouter
from ..ai.analyzer_chat_trend import analyze_chat_trend
from ..models import ChatTrendInput

router = APIRouter()

@router.post("/analyze-chat-trend")
async def chat_trend_endpoint(data: ChatTrendInput):
    return analyze_chat_trend(messages=data.messages, language=data.language)
