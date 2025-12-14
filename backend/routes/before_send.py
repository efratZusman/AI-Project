# backend/routes/before_send.py

from fastapi import APIRouter
from pydantic import BaseModel
from ai.analyzer import analyze_before_send

router = APIRouter()


class BeforeSendInput(BaseModel):
    draft: str


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


@router.post("/analyze-before-send", response_model=BeforeSendOutput)
def analyze_before_send_route(payload: BeforeSendInput):
    result = analyze_before_send(payload.draft)
    return result
