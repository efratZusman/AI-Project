from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import requests
import os

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"
SCOPE = "https://www.googleapis.com/auth/gmail.readonly"

@router.get("/auth/login")
def login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        f"&scope={SCOPE}"
        "&access_type=offline"
        "&prompt=consent"
    )
    return RedirectResponse(url)

@router.get("/auth/callback")
def callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    r = requests.post(token_url, data=data)
    tokens = r.json()

    # כאן אתן שומרות tokens["access_token"] ו־tokens["refresh_token"] במסד.
    return {"tokens": tokens}
