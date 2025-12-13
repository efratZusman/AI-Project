from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

from ai import analyze_email_with_ai
from database.db_setup import Base, engine, get_db
from database.models import EmailAnalysis as EmailModel

Base.metadata.create_all(bind=engine)

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

class EmailDBOutput(BaseModel):
    id: int
    subject: str | None
    body: str
    summary: str
    category: str
    priority: str
    tone: str
    emotions: list[str]
    intent: str
    tasks: list[str]
    deadline: str | None = None
    missing_information: list[str]
    risk_level: str
    suggested_reply: str
    created_at: str

    class Config:
        from_attributes = True


@app.post("/analyze_email", response_model=EmailDBOutput)
def analyze_email(email: EmailInput, db: Session = Depends(get_db)):
    result = analyze_email_with_ai(email.subject or "", email.body)

    db_entry = EmailModel(
        subject=email.subject,
        body=email.body,
        summary=result["summary"],
        category=result["category"],
        priority=result["priority"],
        tone=result["tone"],
        emotions=json.dumps(result["emotions"], ensure_ascii=False),
        intent=result["intent"],
        tasks=json.dumps(result["tasks"], ensure_ascii=False),
        deadline=result.get("deadline", ""),
        missing_information=json.dumps(result.get("missing_information", []), ensure_ascii=False),
        risk_level=result.get("risk_level", "low"),
        suggested_reply=result["suggested_reply"]
    )

    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    return db_entry.to_dict()


@app.get("/history", response_model=list[EmailDBOutput])
def history(db: Session = Depends(get_db)):
    items = db.query(EmailModel).order_by(EmailModel.created_at.desc()).all()
    return [item.to_dict() for item in items]


@app.get("/email/{email_id}", response_model=EmailDBOutput)
def get_email(email_id: int, db: Session = Depends(get_db)):
    item = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not item:
        raise HTTPException(404, "Email not found")
    return item.to_dict()


@app.delete("/email/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_db)):
    item = db.query(EmailModel).filter(EmailModel.id == email_id).first()
    if not item:
        raise HTTPException(404, "Email not found")
    db.delete(item)
    db.commit()
    return {"status": "ok"}

@app.get("/search", response_model=list[EmailDBOutput])
def search_emails(
    q: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(EmailModel)

    if q:
        query = query.filter(
            (EmailModel.subject.ilike(f"%{q}%")) |
            (EmailModel.body.ilike(f"%{q}%")) |
            (EmailModel.summary.ilike(f"%{q}%"))
        )

    if category:
        query = query.filter(EmailModel.category == category)

    if priority:
        query = query.filter(EmailModel.priority == priority)

    results = query.order_by(EmailModel.created_at.desc()).all()
    return [item.to_dict() for item in results]

@app.get("/health")
def health_check():
    return {"status": "ok", "ai_model": MODEL_NAME}

