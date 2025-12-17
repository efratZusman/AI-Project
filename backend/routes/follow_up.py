# # backend/routes/follow_up.py

# from fastapi import APIRouter
# from pydantic import BaseModel
# from backend.ai.analyzer import analyze_follow_up

# router = APIRouter()


# class FollowUpInput(BaseModel):
#     email_body: str
#     days_passed: int = 3


# class FollowUpOutput(BaseModel):
#     needs_follow_up: bool
#     follow_up_reason: str | None = None
#     urgency: str
#     suggested_follow_up: str
#     channel: str | None = None
#     tone_recommendation: str | None = None
#     notes_for_sender: list[str] | None = None


# @router.post("/analyze-follow-up", response_model=FollowUpOutput)
# def analyze_follow_up_route(payload: FollowUpInput):
#     result = analyze_follow_up(payload.email_body, payload.days_passed)
#     return result
