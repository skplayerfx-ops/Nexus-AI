from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import urllib.request
import urllib.parse
import json

app = FastAPI(
    title="Nexus AI Engine",
    description="Multi-Model AI Network & Direct Binance Settlement",
    version="8.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_PAY_ID = "1243962107"

SYSTEM_PROMPT = """You are Nexus AI, a standalone state-of-the-art artificial intelligence model created by Mr. Sadam Hussain son of Jehanzeb.
Language Policy: Detect the language of the user's message (English, Urdu, Roman Urdu, Pashto, etc.) and reply in the EXACT SAME language.
Creator Identity Policy: Only talk about your creator when explicitly asked questions like 'who created you', 'who made you', 'apko kisne banaya', 'cha jor kare yai'.
When asked about creator, answer in user's language stating you were created by Mr. Sadam Hussain son of Jehanzeb."""

class ChatPayload(BaseModel):
    message: Optional[str] = ""
    image: Optional[str] = None
    model: Optional[str] = "nexus-auto"
    user_id: Optional[str] = "guest"

class PaymentPayload(BaseModel):
    user_id: str
    package_id: str
    amount: float

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<h1>Nexus AI Engine Server Active.</h1>"

def detect_language(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["cha", "jor", "kare", "zma", "sta", "sangay"]):
        return "pashto"
    elif any(char in text for char in ["ک", "گ", "ی", "ے", "ہ", "ن"]):
        return "urdu"
    elif any(kw in text_lower for kw in ["who", "what", "created", "built", "made"]):
        return "english"
    else:
        return "roman_urdu"

def handle_identity_query(user_msg: str) -> Optional[str]:
    keywords = ["kisne banaya", "who made", "who created", "creator", "owner", "cha jor kare", "developer", "who built you"]
    if any(kw in user_msg.lower() for kw in keywords):
        lang = detect_language(user_msg)
        if lang == "pashto":
            return "Zma afsar ao jorawunkay Mr. Sadam Hussain son of Jehanzeb dy. Zma num Nexus AI dy."
        elif lang == "urdu":
            return "مجھے Mr. Sadam Hussain son of Jehanzeb نے بنایا ہے۔ میں Nexus AI ہوں۔"
        elif lang == "english":
            return "I am Nexus AI, created by Mr. Sadam Hussain son of Jehanzeb."
        else:
            return "Main Nexus AI hu, aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai."
    return None

def fetch_pollinations_ai(prompt: str, model_type: str = "openai") -> str:
    encoded_prompt = urllib.parse.quote(prompt)
    encoded_system = urllib.parse.quote(SYSTEM_PROMPT)
    url = f"https://text.pollinations.ai/{encoded_prompt}?model={model_type}&system={encoded_system}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            res_text = response.read().decode("utf-8").strip()
            if res_text and not res_text.startswith("Aapka sawal mil gaya"):
                return res_text
    except Exception as e:
        print(f"API Error: {e}")

    fb_url = f"https://text.pollinations.ai/{encoded_prompt}"
    try:
        req_fb = urllib.request.Request(fb_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_fb, timeout=15) as response:
            return response.read().decode("utf-8").strip()
    except Exception:
        return "Apka sawal process ho raha hai, kripya dobara message karein."

def generate_edited_image(prompt: str) -> str:
    clean_prompt = urllib.parse.quote(prompt.strip())
    # Reliable Image Generation Endpoint
    return f"https://image.pollinations.ai/prompt/{clean_prompt}"

@app.post("/api/chat")
async def process_chat(payload: ChatPayload):
    user_msg = payload.message.strip() if payload.message else ""
    user_img = payload.image
    selected_model = payload.model or "nexus-auto"

    # Identity Check
    identity_reply = handle_identity_query(user_msg)
    if identity_reply:
        return {"reply": identity_reply, "image_url": None, "status": "success"}

    # Image Edit/Generation Engine Trigger
    image_triggers = ["edit", "generate", "image", "photo", "picture", "tasveer", "draw", "logo", "make image", "liko", "write", "draw"]
    if any(trig in user_msg.lower() for trig in image_triggers) or user_img:
        prompt = user_msg if user_msg else "High quality AI generated image"
        img_url = generate_edited_image(prompt)
        return {"reply": "Aap ki image request process ho kar taiyar ho gayi hai:", "image_url": img_url, "status": "success"}

    # Multi-AI Model Mapping
    model_map = {
        "nexus-auto": "openai",
        "gpt-4o": "openai",
        "claude-3-5": "claude",
        "gemini-2": "gemini",
        "deepseek-r1": "deepseek",
        "llama-3-3": "llama",
        "qwen-2-5": "qwen"
    }
    
    target_engine = model_map.get(selected_model, "openai")
    ai_response = fetch_pollinations_ai(user_msg, target_engine)

    return {"reply": ai_response, "image_url": None, "status": "success"}

@app.post("/api/payment/process")
async def process_payment(payment: PaymentPayload):
    return JSONResponse({
        "status": "success",
        "message": f"Package {payment.package_id.upper()} activated successfully!",
        "binance_pay_id": BINANCE_PAY_ID,
        "transaction_id": f"TX_BINANCE_{payment.user_id}_{payment.package_id}"
    })
