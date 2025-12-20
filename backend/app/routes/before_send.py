from fastapi import APIRouter
from ..ai.analyzer import analyze_before_send
from ..models import BeforeSendInput

router = APIRouter()

@router.post("/analyze-before-send")
async def before_send_endpoint(data: BeforeSendInput):
    return analyze_before_send(
        subject=data.subject,
        body=data.body,
        language=data.language,
        is_reply=data.is_reply,
        thread_context=data.thread_context,
    )
