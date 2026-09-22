from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import urllib.request
import urllib.parse
import urllib.error

app = FastAPI(
    title="Nexus AI Master Engine",
    description="Multi-Model AI Network & Binance Payment Integration",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_PAY_ID = "1243962107"

IDENTITY_RESPONSES = {
    "ur": "Mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai. Main Nexus AI hu.",
    "en": "I was created by Mr. Sadam Hussain son of Jehanzeb. I am Nexus AI.",
    "ps": "Zma afsar ao jorawunkay Mr. Sadam Hussain son of Jehanzeb dy. Zma num Nexus AI dy.",
    "roman": "Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai."
}

SYSTEM_PROMPT = """You are Nexus AI, an advanced multi-model artificial intelligence platform created by Mr. Sadam Hussain son of Jehanzeb.
Always answer accurately, intelligently, and helpfully.
Language Rule: Detect the language of the user's prompt (English, Urdu, Roman Urdu, Pashto, etc.) and respond in that EXACT same language.
If asked about who created or built you, answer in the user's language specifying that you were created by Mr. Sadam Hussain son of Jehanzeb."""

MODEL_MAPPING = {
    "nexus-auto": "openai",
    "gpt-4o": "openai",
    "claude-3-5": "claude",
    "gemini-2": "gemini",
    "deepseek-r1": "deepseek",
    "llama-3-3": "llama",
    "qwen-2-5": "qwen"
}

class ChatPayload(BaseModel):
    message: Optional[str] = ""
    image: Optional[str] = None
    model: Optional[str] = "nexus-auto"
    language: Optional[str] = "roman"

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<h1>Nexus AI Server Active. Please place index.html in the root directory.</h1>"

def detect_creator_question(text: str) -> bool:
    keywords = ["kisne banaya", "who made", "who created", "creator", "owner", "cha jor kare", "sadam", "developer", "who built you"]
    return any(kw in text.lower() for kw in keywords)

def get_identity_by_language(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["who", "created", "built", "made"]):
        return IDENTITY_RESPONSES["en"]
    elif any(w in text_lower for w in ["cha", "jor", "kare"]):
        return IDENTITY_RESPONSES["ps"]
    elif any(w in text_lower for w in ["کس نے", "بنایا"]):
        return IDENTITY_RESPONSES["ur"]
    else:
        return IDENTITY_RESPONSES["roman"]

def generate_ai_image(prompt: str) -> str:
    encoded_prompt = urllib.parse.quote(f"ultra detailed professional 8k render, {prompt}")
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=99"

def fetch_ai_text(user_text: str, target_model: str) -> str:
    encoded_text = urllib.parse.quote(user_text)
    api_model = MODEL_MAPPING.get(target_model, "openai")
    url = f"https://text.pollinations.ai/{encoded_text}?model={api_model}&system={urllib.parse.quote(SYSTEM_PROMPT)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            res = response.read().decode("utf-8").strip()
            if res:
                return res
    except Exception as e:
        print(f"Engine Fetch Error: {e}")
    return ""

@app.post("/api/chat")
@app.post("/api/chat/v2")
async def handle_chat(payload: ChatPayload):
    user_msg = payload.message.strip() if payload.message else ""
    user_img = payload.image
    selected_model = payload.model or "nexus-auto"

    # Step 5: Multilingual Identity Check
    if user_msg and detect_creator_question(user_msg):
        reply = get_identity_by_language(user_msg)
        return {"reply": reply, "image_url": None, "status": "success"}

    # Step 1: Image Generation / Editing Route
    image_triggers = ["edit", "generate", "image", "photo", "tasveer", "picture", "logo", "draw", "make image", "edit karo"]
    if any(trig in user_msg.lower() for trig in image_triggers) or (user_img and ("edit" in user_msg.lower() or not user_msg)):
        prompt = user_msg if user_msg else "High quality edited version of uploaded image"
        generated_url = generate_ai_image(prompt)
        reply = "Aapki requested image edit/generate kar di gayi hai:"
        return {"reply": reply, "image_url": generated_url, "status": "success"}

    # Step 2 & 3: Multi-AI & Smart Auto Route
    ai_reply = fetch_ai_text(user_msg or "Hello Nexus AI", selected_model)
    if not ai_reply:
        ai_reply = "Aapka paigham mil gaya hai. Aap koi bhi sawal pooch sakte hain ya image edit karwa sakte hain."

    return {"reply": ai_reply, "image_url": None, "status": "success"}

@app.get("/api/packages")
async def get_packages():
    return JSONResponse({
        "binance_id": BINANCE_PAY_ID,
        "packages": [
            {"id": "starter", "name": "Nexus Starter", "price": "$15", "features": ["Fast Multi-AI Models", "Basic Image Editing", "Standard Voice Speed"]},
            {"id": "pro", "name": "Nexus Pro", "price": "$30", "features": ["GPT-4o & Claude 3.5 Unlimited", "HD Image Generation & Editing", "Pro Voice Assistant"]},
            {"id": "business", "name": "Nexus Master Business", "price": "$50", "features": ["All Top AI Engines Direct Access", "Ultra HD 8K Image Editing", "All-In-One Auto Smart Selector", "Priority 24/7 Support"]}
        ]
    })
