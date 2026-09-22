import os
import requests
from fastapi import FastAPI, Request
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

# Set your Official API Keys here or in Vercel Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

BINANCE_PAY_ID = "1243962107"

SYSTEM_PROMPT = """You are Nexus AI, created by Mr. Sadam Hussain son of Jehanzeb.
Always reply in the user's language (Urdu, Pashto, English, Roman Urdu).
Only mention your creator Mr. Sadam Hussain son of Jehanzeb when asked explicitly about who created/made you."""

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4o"
    image_data: Optional[str] = None

@app.post("/api/chat")
async def chat_handler(payload: ChatRequest):
    user_msg = payload.message.strip()
    selected_model = payload.model.lower()

    # Creator Identity Logic
    creator_keywords = ["kisne banaya", "who made", "who created", "creator", "cha jor kare"]
    if any(kw in user_msg.lower() for kw in creator_keywords):
        return {
            "reply": "Main Nexus AI hu, aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.",
            "image_url": None
        }

    # Image Generation / Editing Route (Using Pollinations High Reliability Stream)
    image_triggers = ["generate image", "make photo", "edit image", "picture", "tasveer", "draw", "logo"]
    if any(trig in user_msg.lower() for trig in image_triggers):
        encoded_prompt = requests.utils.quote(user_msg)
        # Direct High Precision Image Link
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed=42&nologo=true"
        return {
            "reply": "Aapki image request process ho kar taiyar hai:",
            "image_url": img_url
        }

    # Direct OpenAI Routing (GPT-4o)
    if "gpt" in selected_model and OPENAI_API_KEY:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
        }
        res = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        if res.status_code == 200:
            return {"reply": res.json()['choices'][0]['message']['content'], "image_url": None}

    # Fallback Multi-AI Universal Engine
    encoded_p = requests.utils.quote(user_msg)
    encoded_sys = requests.utils.quote(SYSTEM_PROMPT)
    fallback_url = f"https://text.pollinations.ai/{encoded_p}?model={selected_model}&system={encoded_sys}"
    
    try:
        response = requests.get(fallback_url, timeout=20)
        return {"reply": response.text.strip(), "image_url": None}
    except Exception:
        return {"reply": "Connection busy. Please try sending your message again.", "image_url": None}
