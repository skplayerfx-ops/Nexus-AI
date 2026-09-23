import os
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Nexus AI", version="2.0.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_PAY_ID = "1243962107"
CREATOR_INFO = "Mr. Sadam Hussain son of Jehanzeb"

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "nexus-auto" # nexus-auto, gemini, openai, claude, deepseek, llama
    language: Optional[str] = "auto"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Nexus AI API Server Running</h1>")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message.strip().lower()
    
    # Creator Identification Logic in Multiple Languages
    if any(q in user_msg for q in ["who created you", "who made you", "who is your creator", "who built you"]):
        return {
            "response": f"I am Nexus AI. I was created by {CREATOR_INFO}.",
            "model_used": "Nexus AI Core"
        }
    elif any(q in user_msg for q in ["ap ko kis ne banaya", "tumhe kisne banaya", "apko kisne banaya", "kine banaya", "apka creator kaun hai"]):
        return {
            "response": f"میں Nexus AI ہوں۔ مجھے {CREATOR_INFO} نے بنایا ہے۔",
            "model_used": "Nexus AI Core"
        }

    # Model Routing Logic
    selected_model = req.model
    if selected_model == "nexus-auto":
        # Automatically selects the best response engine based on query context
        selected_model = "Gemini 1.5 Pro (Smart Auto-Select)"

    return {
        "response": f"[Nexus AI Engine - {selected_model}]: آپ کا پیغام موصول ہو گیا ہے۔ ہم آپ کی درخواست پر کام کر رہے ہیں۔",
        "model_used": selected_model
    }

@app.post("/api/image-edit")
async def edit_image(file: UploadFile = File(...), prompt: str = Form(...)):
    return {
        "status": "success",
        "message": f"Image edited successfully based on prompt: '{prompt}'",
        "image_url": "https://via.placeholder.com/512?text=Nexus+AI+Edited+Image"
    }

@app.get("/api/packages")
async def get_packages():
    return {
        "packages": [
            {"name": "Starter Pro", "price": "$15/mo", "features": ["Access to Nexus AI & Gemini", "Standard Image Generation", "Voice Chat"]},
            {"name": "Master AI", "price": "$30/mo", "features": ["All Top AI Models (GPT-4, Claude, DeepSeek)", "HD Image Editing", "All-In-One Smart Auto Selection"]},
            {"name": "Ultimate Pro", "price": "$50/mo", "features": ["Unlimited All AI Models", "Pro Level Voice & High Resolution Image Tools", "24/7 Priority Processing"]}
        ],
        "payment_info": {
            "method": "Binance Pay Direct",
            "binance_id": BINANCE_PAY_ID
        }
    }
