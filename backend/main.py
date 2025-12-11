from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
    return EmailAnalysis(
        summary="סיכום לדוגמה (כרגע בלי AI)",
        category="general",
        priority="medium",
        tasks=["לענות לשולח", "לבדוק פרטים"],
        suggested_reply="תודה על הפנייה, נחזור אליך בהקדם."
    )
