from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import urllib.request
import urllib.error

app = FastAPI(
    title="Nexus AI Engine API",
    description="Multi-Model AI Assistant powered by OpenRouter & Gemini API",
    version="2.5.0"
)

# CORS Configuration for Vercel / Replit Frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Identity Constants
IDENTITY_RESPONSE = "Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai."

SYSTEM_PROMPT = """You are Nexus AI, an advanced multi-model AI assistant developed exclusively by Mr. Sadam Hussain son of Jehanzeb.
You support Urdu, Pashto, Roman Urdu, and English languages naturally.
Whenever asked about who created you, who made you, or your identity, always state clearly in the user's language that you were created by Mr. Sadam Hussain son of Jehanzeb.
Provide helpful, concise, intelligent, and accurate responses for trading, coding, image analysis, and general chat."""

# Model Mapping for OpenRouter / Gemini Fallbacks
MODEL_MAP = {
    "auto": "google/gemini-2.0-flash-lite-001",
    "gpt-4o": "openai/gpt-4o-mini",
    "claude-3-5": "anthropic/claude-3.5-haiku",
    "gemini-1-5": "google/gemini-flash-1.5",
    "deepseek-r1": "deepseek/deepseek-r1-distill-llama-70b",
    "llama-3-3": "meta-llama/llama-3.3-70b-instruct",
    "image-edit-engine": "google/gemini-2.0-flash-lite-001"
}

class ChatPayload(BaseModel):
    message: Optional[str] = ""
    image: Optional[str] = None
    model: Optional[str] = "auto"
    voice_mode: Optional[bool] = False
    history: Optional[List[Dict[str, str]]] = []

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Nexus AI Engine API Server",
        "creator": "Mr. Sadam Hussain son of Jehanzeb",
        "version": "2.5.0",
        "supported_models": list(MODEL_MAP.keys())
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "active"}

def call_openrouter_api(messages: List[Dict[str, Any]], model_id: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return ""

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nexus-ai-api-server.vercel.app",
        "X-Title": "Nexus AI"
    }
    
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "choices" in res_data and len(res_data["choices"]) > 0:
                return res_data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenRouter API Call Error: {e}")
    return ""

def process_identity_check(text: str) -> bool:
    keywords = [
        "kisne banaya", "who made", "who created", "who is your creator",
        "da cha ye", "cha jor kare", "owner", "creator", "sadam"
    ]
    lowered = text.lower()
    return any(kw in lowered for kw in keywords)

@app.post("/api/chat")
@app.post("/api/chat/v2")
async def handle_chat_request(payload: ChatPayload):
    user_message = payload.message.strip() if payload.message else ""
    user_image = payload.image
    selected_model_key = payload.model if payload.model in MODEL_MAP else "auto"
    target_model = MODEL_MAP[selected_model_key]

    # Check creator identity trigger
    if user_message and process_identity_check(user_message):
        return {
            "reply": IDENTITY_RESPONSE,
            "response": IDENTITY_RESPONSE,
            "message": IDENTITY_RESPONSE,
            "model_used": selected_model_key
        }

    # Construct conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if payload.history:
        for item in payload.history:
            if "role" in item and "content" in item:
                messages.append({"role": item["role"], "content": item["content"]})

    # Image handling logic
    if user_image:
        content_payload = []
        if user_message:
            content_payload.append({"type": "text", "text": user_message})
        else:
            content_payload.append({"type": "text", "text": "Analyze and describe this image in detail."})
        
        content_payload.append({
            "type": "image_url",
            "image_url": {"url": user_image}
        })
        messages.append({"role": "user", "content": content_payload})
    else:
        if user_message:
            messages.append({"role": "user", "content": user_message})
        else:
            messages.append({"role": "user", "content": "Hello Nexus AI"})

    # Primary API Call
    ai_reply = call_openrouter_api(messages, target_model)

    # Secondary Fallback Model Call
    if not ai_reply and target_model != MODEL_MAP["auto"]:
        ai_reply = call_openrouter_api(messages, MODEL_MAP["auto"])

    # Final Default Safe Fallback
    if not ai_reply:
        if user_message:
            ai_reply = f"Nexus AI [{selected_model_key.upper()}]: Aapka paigham mil gaya hai. Main Urdu, Pashto aur English samajhta hu. Aap koi bhi sawal pooch sakte hain!"
        else:
            ai_reply = IDENTITY_RESPONSE

    # Return multi-key JSON response to ensure index.html frontend never gets undefined
    return {
        "reply": ai_reply,
        "response": ai_reply,
        "message": ai_reply,
        "status": "success",
        "model_used": selected_model_key,
        "has_image": bool(user_image)
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "reply": IDENTITY_RESPONSE,
            "response": IDENTITY_RESPONSE,
            "message": IDENTITY_RESPONSE,
            "status": "fallback_recovered"
        }
    )
