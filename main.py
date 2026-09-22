from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IDENTITY_RESPONSE = "Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai."

SYSTEM_PROMPT = """You are Nexus AI, an advanced multi-model AI assistant developed exclusively by Mr. Sadam Hussain son of Jehanzeb.
You support Urdu, Pashto, Roman Urdu, and English languages naturally.
Whenever asked about who created you, who made you, or your identity, always state clearly in the user's language that you were created by Mr. Sadam Hussain son of Jehanzeb.
Provide helpful, concise, intelligent, and accurate responses for trading, coding, image analysis, and general chat."""

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

# 1. Main Home Route - Renders Full Web UI
@app.get("/", response_class=HTMLResponse)
async def serve_home_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus AI Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-white font-sans min-h-screen flex flex-col">
    <header class="p-4 border-b border-gray-800 bg-gray-900 flex justify-between items-center">
        <h1 class="font-bold text-lg text-cyan-400">NEXUS AI</h1>
        <span class="text-xs text-gray-400">By Mr. Sadam Hussain</span>
    </header>
    
    <main class="flex-1 p-4 flex flex-col justify-between max-w-4xl mx-auto w-full">
        <div id="chat-box" class="space-y-4 overflow-y-auto mb-4 flex-1">
            <div class="bg-gray-800 p-3.5 rounded-xl text-sm border border-gray-700">
                <strong class="text-cyan-400 block mb-1">Nexus AI Engine</strong>
                Salam! Main Nexus AI hu. Mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.
            </div>
        </div>

        <div class="flex gap-2">
            <input type="text" id="user-input" placeholder="Apna sawal likhein..." class="flex-1 bg-gray-900 border border-gray-800 p-3 rounded-xl text-sm focus:outline-none focus:border-cyan-500">
            <button onclick="sendMessage()" class="bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-6 py-3 rounded-xl text-sm">Send</button>
        </div>
    </main>

    <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if (!text) return;

            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<div class="bg-cyan-950 text-cyan-100 p-3.5 rounded-xl text-sm ml-auto max-w-lg mb-2">${text}</div>`;
            input.value = '';

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                chatBox.innerHTML += `<div class="bg-gray-800 p-3.5 rounded-xl text-sm border border-gray-700 mb-2"><strong class="text-cyan-400 block mb-1">Nexus AI</strong>${data.reply}</div>`;
            } catch (e) {
                chatBox.innerHTML += `<div class="bg-gray-800 p-3.5 rounded-xl text-sm border border-gray-700 mb-2"><strong class="text-cyan-400 block mb-1">Nexus AI</strong>Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

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
        print(f"API Error: {e}")
    return ""

def process_identity_check(text: str) -> bool:
    keywords = ["kisne banaya", "who made", "who created", "who is your creator", "da cha ye", "cha jor kare", "owner", "creator", "sadam"]
    return any(kw in text.lower() for kw in keywords)

# 2. API Endpoints
@app.post("/api/chat")
@app.post("/api/chat/v2")
async def handle_chat_request(payload: ChatPayload):
    user_message = payload.message.strip() if payload.message else ""
    user_image = payload.image
    selected_model_key = payload.model if payload.model in MODEL_MAP else "auto"
    target_model = MODEL_MAP[selected_model_key]

    if user_message and process_identity_check(user_message):
        return {"reply": IDENTITY_RESPONSE, "response": IDENTITY_RESPONSE}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if user_image:
        content_payload = [{"type": "text", "text": user_message or "Analyze this image."}]
        content_payload.append({"type": "image_url", "image_url": {"url": user_image}})
        messages.append({"role": "user", "content": content_payload})
    else:
        messages.append({"role": "user", "content": user_message or "Hello"})

    ai_reply = call_openrouter_api(messages, target_model)

    if not ai_reply:
        ai_reply = IDENTITY_RESPONSE if not user_message else f"Nexus AI: Aapka paigham mil gaya hai."

    return {"reply": ai_reply, "response": ai_reply, "status": "success"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"reply": IDENTITY_RESPONSE, "response": IDENTITY_RESPONSE}
    )
