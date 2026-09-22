import os
import urllib.request
import urllib.parse
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Nexus AI Master Engine", version="10.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_PAY_ID = "1243962107"

SYSTEM_PROMPT = """You are Nexus AI, created by Mr. Sadam Hussain son of Jehanzeb.
Always reply in the user's language (Urdu, Pashto, English, Roman Urdu).
Only mention your creator Mr. Sadam Hussain son of Jehanzeb when asked explicitly about who created/made you."""

class ChatRequest(BaseModel):
    message: Optional[str] = ""
    model: Optional[str] = "gpt-4o"
    image_data: Optional[str] = None

class PaymentRequest(BaseModel):
    user_id: str
    package_id: str
    amount: float

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<h1>Nexus AI Engine Active</h1>"

@app.post("/api/chat")
async def chat_handler(payload: ChatRequest):
    user_msg = payload.message.strip() if payload.message else ""
    selected_model = payload.model.lower() if payload.model else "gpt-4o"

    # Identity Logic
    creator_keywords = ["kisne banaya", "who made", "who created", "creator", "cha jor kare", "developer"]
    if any(kw in user_msg.lower() for kw in creator_keywords):
        return {
            "reply": "Main Nexus AI hu, aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.",
            "image_url": None
        }

    # Image Generation / Editing Route
    image_triggers = ["generate image", "make photo", "edit image", "picture", "tasveer", "draw", "logo", "liko", "write"]
    if any(trig in user_msg.lower() for trig in image_triggers):
        encoded_prompt = urllib.parse.quote(user_msg)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        return {
            "reply": "Aapki image request process ho kar taiyar hai:",
            "image_url": img_url
        }

    # Text Chat Route via Pollinations
    encoded_p = urllib.parse.quote(user_msg)
    encoded_sys = urllib.parse.quote(SYSTEM_PROMPT)
    url = f"https://text.pollinations.ai/{encoded_p}?model={selected_model}&system={encoded_sys}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            reply_text = response.read().decode("utf-8").strip()
            return {"reply": reply_text, "image_url": None}
    except Exception:
        return {"reply": "Connection busy, please try sending message again.", "image_url": None}

@app.post("/api/payment/process")
async def process_payment(payment: PaymentRequest):
    return JSONResponse({
        "status": "success",
        "message": f"Package {payment.package_id.upper()} activated successfully!",
        "binance_pay_id": BINANCE_PAY_ID
    })
