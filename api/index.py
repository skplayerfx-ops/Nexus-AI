import os
import urllib.parse
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx

app = FastAPI(title="Nexus AI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_ID = "1243962107"
CREATOR_NAME = "Mr Sadam Hussain son of Jehanzeb"

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "nexus-auto"

async def query_pollinations_api(prompt: str, model_type: str, system_prompt: str) -> str:
    encoded_p = urllib.parse.quote(prompt)
    encoded_sys = urllib.parse.quote(system_prompt)
    url = f"https://text.pollinations.ai/{encoded_p}?model={model_type}&system={encoded_sys}"
    
    async with httpx.AsyncClient(timeout=12.0) as client:
        try:
            res = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code == 200 and res.text.strip():
                return res.text.strip()
        except Exception:
            pass
    return "Engine busy hai, please dobara try karein."

@app.get("/", response_class=HTMLResponse)
async def serve_root():
    # Root folder or relative path index.html check
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    elif os.path.exists("../index.html"):
        with open("../index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Nexus AI Engine Active</h1>"

@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    user_msg = req.message.strip()
    msg_lower = user_msg.lower()
    selected = (req.model or "nexus-auto").lower()

    # Creator Identity Logic
    creator_queries_en = ["who created you", "who made you", "who is your creator", "who built you"]
    creator_queries_ur = ["ap ko kis ne banaya", "tumhe kisne banaya", "apko kisne banaya", "kine banaya", "aapko kisne banaya", "kis ne banaya"]

    if any(q in msg_lower for q in creator_queries_ur):
        return {
            "type": "text",
            "reply": f"Main Nexus AI hoon, mujhe {CREATOR_NAME} ne banaya hai.",
            "model_used": "Nexus Core"
        }
    elif any(q in msg_lower for q in creator_queries_en):
        return {
            "type": "text",
            "reply": f"I am Nexus AI. I was created by {CREATOR_NAME}.",
            "model_used": "Nexus Core"
        }

    # Image Request Keyword Check
    img_keywords = ["generate image", "make photo", "edit image", "draw", "picture", "logo", "tasveer", "photo bano"]
    if any(k in msg_lower for kin img_keywords):
        encoded_prompt = urllib.parse.quote(user_msg)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true&model=flux"
        return {
            "type": "image",
            "reply": "Aapki request ke mutabiq image ready hai:",
            "image_url": img_url,
            "model_used": "Nexus Flux Engine"
        }

    # Dynamic AI Routing
    sys_prompt = f"You are Nexus AI, an intelligent multi-engine assistant created by {CREATOR_NAME}."
    
    model_map = {
        "gemini": "gemini",
        "openai": "openai",
        "claude": "claude",
        "deepseek": "deepseek",
        "llama": "llama"
    }
    
    target_engine = model_map.get(selected, "openai")
    reply_text = await query_pollinations_api(user_msg, target_engine, sys_prompt)

    return {
        "type": "text",
        "reply": reply_text,
        "model_used": f"Nexus AI ({target_engine.upper()})"
    }

@app.post("/api/image-edit")
async def edit_image_file(prompt: str = Form(...), file: UploadFile = File(None)):
    encoded_prompt = urllib.parse.quote(prompt)
    img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=99&nologo=true&model=flux"
    return {
        "type": "image",
        "reply": "Image edit complete:",
        "image_url": img_url
    }

@app.get("/api/packages")
async def get_packages():
    return {
        "binance_pay_id": BINANCE_ID,
        "packages": [
            {"name": "Starter Pro", "price": "$15", "features": ["Nexus AI & Gemini Access", "Voice Mode", "Basic Image Gen"]},
            {"name": "Master Pro", "price": "$30", "features": ["All-In-One AI Selection", "GPT-4o & Claude 3.5", "Image Editing Pro"]},
            {"name": "Ultimate Pro", "price": "$50", "features": ["Unlimited All Models", "Priority Voice Response", "High-Res Image Engine"]}
        ]
    }
