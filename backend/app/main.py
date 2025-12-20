from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.before_send import router as before_send_router

app = FastAPI(
    title="AI Communication Guard",
    description="Before-You-Send Guardian API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(before_send_router)

@app.get("/health")
def health():
    return {"status": "ok"}
