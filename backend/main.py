# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.before_send import router as before_send_router
from backend.routes.follow_up import router as follow_up_router

app = FastAPI(
    title="AI Communication Guard",
    description="Before-You-Send & Follow-Up Guardian API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # בשלב מאוחר יותר אפשר להצר
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(before_send_router)
app.include_router(follow_up_router)


@app.get("/health")
def health():
    return {"status": "ok"}
