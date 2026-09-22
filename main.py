import os
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx

app = FastAPI(title="Nexus AI Master System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4o"
    system_prompt: Optional[str] = "You are Nexus AI."

# 1. Root Route
@app.get("/", response_class=HTMLResponse)
async def serve_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Nexus AI Master Engine Active</h1>"

# 2. Universal Dynamic AI Chat Engine
@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    user_msg = req.message.strip() if req.message else ""
    selected_model = req.model.lower() if req.model else "gpt-4o"
    sys_prompt = req.system_prompt or "You are Nexus AI."

    # Image Request Check
    image_keywords = ["generate image", "make photo", "edit image", "draw", "picture", "logo", "tasveer"]
    if any(k in user_msg.lower() for k in image_keywords):
        encoded_prompt = urllib.parse.quote(user_msg)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true&model=flux"
        return {
            "type": "image",
            "reply": "Aapki image generate ho gayi hai:",
            "image_url": img_url
        }

    # Model Name Mapping
    model_map = {
        "gpt-4o": "openai",
        "claude-3-5": "claude",
        "gemini": "gemini",
        "deepseek": "deepseek",
        "llama": "llama"
    }
    target_engine = model_map.get(selected_model, "openai")

    # Safe API Execution
    encoded_p = urllib.parse.quote(user_msg)
    encoded_sys = urllib.parse.quote(sys_prompt)
    url = f"https://text.pollinations.ai/{encoded_p}?model={target_engine}&system={encoded_sys}"

    async with httpx.AsyncClient(timeout=9.0) as client:
        try:
            res = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code == 200 and res.text.strip():
                return {"type": "text", "reply": res.text.strip(), "image_url": None}
        except Exception:
            pass

    return {
        "type": "text",
        "reply": "System busy hai, please dobara try karein.",
        "image_url": None
    }
