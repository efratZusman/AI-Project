# backend/models.py

from pydantic import BaseModel
from typing import Literal, List, Optional
from datetime import datetime


class ThreadMessage(BaseModel):
    author: Literal["me", "them"]
    text: str
    timestamp: Optional[datetime] = None


class BeforeSendInput(BaseModel):
    subject: Optional[str] = None
    body: str
    language: str = "auto"
    is_reply: bool = False
    thread_context: Optional[List[ThreadMessage]] = None
