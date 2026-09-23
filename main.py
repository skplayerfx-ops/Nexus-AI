import os
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import httpx

app = FastAPI(title="Nexus AI Engine")

# CORS setup for web interface
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

@app.get("/")
async def serve_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Nexus AI Active</h1>")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message.strip()
    msg_lower = user_msg.lower()

    # Instant Creator Identity Response
    creator_keywords = ["owner", "creator", "kisne banaya", "who made", "who created", "banaya hy", "banaya hai", "kine banaya"]
    if any(k in msg_lower for k in creator_keywords):
        return {
            "type": "text",
            "reply": f"Main Nexus AI hoon, mujhe {CREATOR_NAME} ne banaya hai aur wahi mere owner hain.",
            "model_used": "Nexus Core"
        }

    # Image Generation Handler
    img_keywords = ["generate image", "make photo", "edit image", "draw", "picture", "logo", "tasveer", "photo bano"]
    if any(k in msg_lower for k in img_keywords):
        encoded_prompt = urllib.parse.quote(user_msg)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true&model=flux"
        return {
            "type": "image",
            "reply": "Aapki request ke mutabiq image ready hai:",
            "image_url": img_url,
            "model_used": "Nexus Flux Engine"
        }

    # Direct Fast AI Engine Call
    encoded_p = urllib.parse.quote(user_msg)
    sys_prompt = urllib.parse.quote(f"You are Nexus AI, created by {CREATOR_NAME}.")
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
