import os
import urllib.parse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Optional SDK Imports (In case API keys are present)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import httpx
except ImportError:
    httpx = None


# ==========================================
# 1. INDIVIDUAL AI ENGINE MODULES
# ==========================================

class OpenAIEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if OpenAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def query(self, prompt: str, system_prompt: str) -> str:
        if not self.client:
            return "OpenAI API Key not configured."
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {str(e)}"


class ClaudeEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if anthropic and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def query(self, prompt: str, system_prompt: str) -> str:
        if not self.client:
            return "Anthropic API Key not configured."
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Claude Error: {str(e)}"


class GeminiEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def query(self, prompt: str, system_prompt: str) -> str:
        if not self.model:
            return "Gemini API Key not configured."
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"


class DeepSeekEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if OpenAI and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
        else:
            self.client = None

    def query(self, prompt: str, system_prompt: str) -> str:
        if not self.client:
            return "DeepSeek API Key not configured."
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"DeepSeek Error: {str(e)}"


class LlamaEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if OpenAI and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        else:
            self.client = None

    def query(self, prompt: str, system_prompt: str) -> str:
        if not self.client:
            return "Llama/Groq API Key not configured."
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Llama Error: {str(e)}"


class ImageEngine:
    @staticmethod
    def generate_image_url(prompt: str) -> str:
        encoded_prompt = urllib.parse.quote(prompt.strip())
        return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true&model=flux"


# ==========================================
# 2. FASTAPI MASTER ROUTER
# ==========================================

app = FastAPI(title="Nexus Master Combined AI System")

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
    system_prompt: Optional[str] = "You are Nexus AI Assistant."

@app.post("/api/chat")
async def combined_chat_router(req: ChatRequest):
    msg = req.message.strip()
    selected_model = req.model.lower() if req.model else "gpt-4o"

    # Image Check
    image_keywords = ["generate image", "make photo", "edit image", "draw", "picture", "logo", "tasveer"]
    if any(k in msg.lower() for k in image_keywords):
        return {
            "type": "image",
            "reply": "Image generated successfully:",
            "image_url": ImageEngine.generate_image_url(msg)
        }

    # Model Router
    if "gpt" in selected_model or "openai" in selected_model:
        res = OpenAIEngine().query(msg, req.system_prompt)
    elif "claude" in selected_model or "anthropic" in selected_model:
        res = ClaudeEngine().query(msg, req.system_prompt)
    elif "gemini" in selected_model:
        res = GeminiEngine().query(msg, req.system_prompt)
    elif "deepseek" in selected_model:
        res = DeepSeekEngine().query(msg, req.system_prompt)
    elif "llama" in selected_model:
        res = LlamaEngine().query(msg, req.system_prompt)
    else:
        res = OpenAIEngine().query(msg, req.system_prompt)

    return {
        "type": "text",
        "reply": res,
        "image_url": None
    }
