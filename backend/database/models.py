from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .db_setup import Base
import json

class EmailAnalysis(Base):
    __tablename__ = "email_analysis"

    id = Column(Integer, primary_key=True, index=True)

    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)

    summary = Column(Text)
    category = Column(String)
    priority = Column(String)
    tone = Column(String)

    emotions = Column(Text)
    intent = Column(String)
    tasks = Column(Text)
    deadline = Column(String)
    missing_information = Column(Text)
    risk_level = Column(String)
    suggested_reply = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "body": self.body,
            "summary": self.summary,
            "category": self.category,
            "priority": self.priority,
            "tone": self.tone,
            "emotions": json.loads(self.emotions or "[]"),
            "intent": self.intent,
            "tasks": json.loads(self.tasks or "[]"),
            "deadline": self.deadline,
            "missing_information": json.loads(self.missing_information or "[]"),
            "risk_level": self.risk_level,
            "suggested_reply": self.suggested_reply,
            "created_at": str(self.created_at)
        }
