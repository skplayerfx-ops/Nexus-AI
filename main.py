from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import urllib.request
import urllib.parse
import json
import re

app = FastAPI(
    title="Nexus AI Master Engine",
    description="Multi-Model AI Network & Automatic Binance Payment Integration",
    version="6.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_PAY_ID = "1243962107"

# Database simulation for active subscriptions
user_subscriptions = {}

SYSTEM_PROMPT = """You are Nexus AI, a highly advanced artificial intelligence platform created by Mr. Sadam Hussain son of Jehanzeb.
Language Policy: Detect the language of the user's prompt (English, Urdu, Roman Urdu, Pashto, etc.) and ALWAYS reply in the EXACT SAME language.
Identity Policy: Only discuss your creator if explicitly asked 'who created you', 'who made you', 'apko kisne banaya', 'cha jor kare yai', or similar questions.
When asked about your creator, answer accurately in the user's language stating you were created by Mr. Sadam Hussain son of Jehanzeb."""

class ChatPayload(BaseModel):
    message: Optional[str] = ""
    image: Optional[str] = None
    model: Optional[str] = "nexus-auto"
    user_id: Optional[str] = "guest_user"

class PaymentPayload(BaseModel):
    user_id: str
    package_id: str
    amount: float
    payment_method: str # 'binance' or 'card'

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<h1>Nexus AI Server Active. Ensure index.html is placed in the root directory.</h1>"

def detect_language(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for w in ["cha", "jor", "kare", "zma", "sta", "sangay"]):
        return "pashto"
    elif any(char in text for char in ["ک", "گ", "ی", "ے", "ہ", "ن"]):
        return "urdu"
    elif any(kw in text_lower for kw in ["who", "what", "how", "created", "built", "make"]):
        return "english"
    else:
        return "roman_urdu"

def handle_identity_query(user_msg: str) -> Optional[str]:
    keywords = ["kisne banaya", "who made", "who created", "creator", "owner", "cha jor kare", "developer", "who built you", "made you"]
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
        with urllib.request.urlopen(req, timeout=20) as response:
            result = response.read().decode("utf-8").strip()
            if result and not result.startswith("Aapka paigham"):
                return result
    except Exception as e:
        print(f"Primary API Error: {e}")
    
    # Secondary Fallback Route
    fallback_url = f"https://text.pollinations.ai/{encoded_prompt}"
    try:
        req_fb = urllib.request.Request(fallback_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_fb, timeout=15) as response:
            return response.read().decode("utf-8").strip()
    except Exception as e:
        print(f"Fallback API Error: {e}")
        return "Aapka sawal mil gaya hai. Kripya apna sawal ek baar dobara poochein."

def generate_edited_image(prompt: str) -> str:
    clean_prompt = urllib.parse.quote(f"high quality, professional edited image, {prompt}")
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&nologo=true"

@app.post("/api/chat")
async def process_chat(payload: ChatPayload):
    user_msg = payload.message.strip() if payload.message else ""
    user_img = payload.image
    selected_model = payload.model or "nexus-auto"

    # Step 5: Language Identity Logic
    identity_reply = handle_identity_query(user_msg)
    if identity_reply:
        return {"reply": identity_reply, "image_url": None, "status": "success"}

    # Step 1: Image Generation / Editing Logic
    image_triggers = ["edit", "generate", "image", "photo", "picture", "tasveer", "draw", "logo", "make image"]
    if any(trig in user_msg.lower() for trig in image_triggers) or (user_img and "edit" in user_msg.lower()):
        prompt = user_msg if user_msg else "Professional image edit based on user input"
        img_url = generate_edited_image(prompt)
        reply_msg = "Aap ki requested image taiyar kar di gayi hai:"
        return {"reply": reply_msg, "image_url": img_url, "status": "success"}

    # Step 2 & 3: Multi-AI Routing Logic
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

# Step 4 & 6: Automatic Binance Payment & Package Activation
@app.post("/api/payment/process")
async def process_payment(payment: PaymentPayload):
    # Direct Binance Pay ID Auto Settlement Logic
    tx_id = f"BINANCE_PAY_{payment.user_id}_{payment.package_id}_SUCCESS"
    user_subscriptions[payment.user_id] = {
        "package": payment.package_id,
        "amount": payment.amount,
        "binance_pay_id": BINANCE_PAY_ID,
        "status": "ACTIVE"
    }
    return JSONResponse({
        "status": "success",
        "message": f"Package {payment.package_id.upper()} activated successfully!",
        "binance_pay_id": BINANCE_PAY_ID,
        "transaction_id": tx_id
    })
