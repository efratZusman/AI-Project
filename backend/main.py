from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai import analyze_email_with_ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailInput(BaseModel):
    subject: str | None = None
    body: str

class EmailAnalysis(BaseModel):
    summary: str
    category: str
    priority: str
    tasks: list[str]
    suggested_reply: str

@app.post("/analyze_email", response_model=EmailAnalysis)
def analyze_email(email: EmailInput):
    result = analyze_email_with_ai(email.subject, email.body)

    return EmailAnalysis(
        summary=result.get("summary", ""),
        category=result.get("category", "general"),
        priority=result.get("priority", "medium"),
        tasks=result.get("tasks", []),
        suggested_reply=result.get("suggested_reply", "")
    )

