import os
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import httpx

app = FastAPI(title="Nexus AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CREATOR_NAME = "Mr Sadam Hussain son of Jehanzeb"

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "nexus-auto"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Root folder or relative path index.html reading
    for path in ["index.html", "../index.html"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>Nexus AI System Active</h1>"

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message.strip()
    msg_lower = user_msg.lower()

    # Instant Creator Answer
    creator_keywords = ["owner", "creator", "kisne banaya", "who made", "who created", "banaya hy", "banaya hai", "kine banaya"]
    if any(k in msg_lower for k in creator_keywords):
        return {
            "type": "text",
            "reply": f"Main Nexus AI hoon, mujhe {CREATOR_NAME} ne banaya hai aur wahi mere owner hain.",
            "model_used": "Nexus Core"
        }

    # Direct Fast AI Engine
    encoded_p = urllib.parse.quote(user_msg)
    sys_prompt = urllib.parse.quote(f"You are Nexus AI created by {CREATOR_NAME}.")
    url = f"https://text.pollinations.ai/{encoded_p}?system={sys_prompt}"

    async with httpx.AsyncClient(timeout=12.0) as client:
        try:
            res = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code == 200 and res.text.strip():
                return {
                    "type": "text",
                    "reply": res.text.strip(),
                    "model_used": "Nexus AI"
                }
        except Exception:
            pass

    return {
        "type": "text",
        "reply": "Main aapki baat samajh raha hoon. Kripya apna sawal dobara puchiye.",
        "model_used": "Nexus AI"
    }
