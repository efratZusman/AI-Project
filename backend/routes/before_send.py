# backend/routes/before_send.py

from fastapi import APIRouter
from pydantic import BaseModel
from backend.ai.analyzer import analyze_before_send
from backend.models import BeforeSendInput
from typing import Literal, List, Optional
from datetime import datetime

router = APIRouter()

class ThreadMessage(BaseModel):
    author: Literal["me", "them"]
    text: str
    timestamp: datetime | None = None

class BeforeSendInput(BaseModel):
    subject: str | None = None
    body: str
    language: str = "auto"
    is_reply: bool = False
    thread_context: list[ThreadMessage] | None = None

class BeforeSendOutput(BaseModel):
    intent: str
    risk_level: str
    risk_factors: list[str]
    recipient_interpretation: str
    send_decision: str
    follow_up_needed: bool
    follow_up_reason: str | None = None
    safer_subject: str | None = None
    safer_body: str
    notes_for_sender: list[str] | None = None

@router.post("/analyze-before-send")
async def before_send_endpoint(data: BeforeSendInput):
    result = analyze_before_send(
        subject=data.subject,
        body=data.body,
        language=data.language,
        is_reply=data.is_reply,
        thread_context=data.thread_context
    )
    return result
