import os
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

# Individual Modules Import
from openai_module import OpenAIEngine
from claude_module import ClaudeEngine
from gemini_module import GeminiEngine
from deepseek_module import DeepSeekEngine
from llama_module import LlamaEngine
from image_module import ImageEngine

app = FastAPI(title="Nexus AI Master System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HOMEPAGE ROUTE (Fixes {"detail": "Not Found"})
@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    # Looking for index.html in current directory
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Nexus AI System is Live!</h1><p>index.html file missing in project folder.</p>"

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4o"
    system_prompt: Optional[str] = "You are Nexus AI Assistant."

@app.post("/api/chat")
async def chat_router(req: ChatRequest):
    msg = req.message.strip()
    selected_model = req.model.lower() if req.model else "gpt-4o"

    # Image Check
    image_keywords = ["generate image", "make photo", "edit image", "draw", "picture", "logo", "tasveer"]
    if any(k in msg.lower() for k in image_keywords):
        return {
            "type": "image",
            "reply": "Aapki image request process ho gayi hai:",
            "image_url": ImageEngine.generate_url(msg)
        }

    # Dynamic Model Router
    try:
        if "gpt" in selected_model or "openai" in selected_model:
            res = OpenAIEngine().generate(msg, req.system_prompt)
        elif "claude" in selected_model or "anthropic" in selected_model:
            res = ClaudeEngine().generate(msg, req.system_prompt)
        elif "gemini" in selected_model:
            res = GeminiEngine().generate(msg, req.system_prompt)
        elif "deepseek" in selected_model:
            res = DeepSeekEngine().generate(msg, req.system_prompt)
        elif "llama" in selected_model:
            res = LlamaEngine().generate(msg, req.system_prompt)
        else:
            res = OpenAIEngine().generate(msg, req.system_prompt)
    except Exception as e:
        res = f"AI Processing Error: {str(e)}"

    return {
        "type": "text",
        "reply": res,
        "image_url": None
    }
