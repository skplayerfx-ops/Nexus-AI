from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import urllib.request
import urllib.parse
import urllib.error

app = FastAPI(
    title="Nexus AI Engine API",
    description="Multi-Model AI Assistant with Image Editing and Voice Mode",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IDENTITY_RESPONSE = "Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai."

SYSTEM_PROMPT = "You are Nexus AI, created exclusively by Mr. Sadam Hussain son of Jehanzeb. Reply naturally, intelligently, and helpful in Roman Urdu, Urdu, Pashto, or English."

class ChatPayload(BaseModel):
    message: Optional[str] = ""
    image: Optional[str] = None
    model: Optional[str] = "openai"

# 1. UI Dashboard Code
@app.get("/", response_class=HTMLResponse)
async def serve_home_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Nexus AI Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b0f17; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .pulse-orb { animation: pulse 1.5s infinite ease-in-out; }
        @keyframes pulse { 0%, 100% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.08); opacity: 1; } }
    </style>
</head>
<body class="flex flex-col min-h-screen">

    <!-- Header -->
    <header class="p-3 bg-gray-900 border-b border-gray-800 flex items-center justify-between">
        <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center font-bold text-white text-sm shadow">NX</div>
            <div>
                <h1 class="font-bold text-sm text-white">NEXUS AI</h1>
                <p class="text-[10px] text-cyan-400">By Mr. Sadam Hussain</p>
            </div>
        </div>
        
        <select id="ai-model-select" class="bg-gray-800 text-xs text-cyan-300 border border-cyan-500/30 rounded-lg px-2 py-1 focus:outline-none">
            <option value="openai">✨ ChatGPT (GPT-4o)</option>
            <option value="qwen">🧠 Qwen 2.5 Turbo</option>
            <option value="claude">🔮 Claude 3.5 Sonnet</option>
            <option value="deepseek">🔍 DeepSeek R1</option>
        </select>
    </header>

    <!-- Chat Display Area -->
    <main class="flex-1 p-3 overflow-y-auto space-y-3" id="chat-box" style="padding-bottom: 90px;">
        <div class="bg-gray-800 p-3 rounded-xl max-w-[85%] text-xs border border-gray-700/60 leading-relaxed">
            <strong class="text-cyan-400 block mb-1">Nexus AI Engine</strong>
            Salam! Main Nexus AI hu. Mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.<br><br>
            • **Text Chat:** Koi bhi sawal poochen.<br>
            • **Image Editing / Generation:** Image upload karein aur likhein "is image ko edit karke professional logo bana do" ya "generate a cat".<br>
            • **Voice Chat:** Mic button dabain aur bol kar baat karein.
        </div>
    </main>

    <!-- Image Preview Bar -->
    <div id="image-preview-bar" class="hidden fixed bottom-16 left-3 right-3 bg-gray-900 border border-cyan-500/40 p-2 rounded-xl flex items-center justify-between z-20">
        <div class="flex items-center space-x-2">
            <img id="image-preview" class="w-10 h-10 object-cover rounded-lg border border-gray-700">
            <span class="text-xs text-cyan-300">Image Attached for Editing/Analysis</span>
        </div>
        <button onclick="clearImage()" class="text-red-400 font-bold text-xs px-2 py-1">✕ Remove</button>
    </div>

    <!-- Controls Bar -->
    <div class="fixed bottom-0 left-0 right-0 p-2 bg-gray-950 border-t border-gray-800 flex items-center gap-2 z-10">
        <label class="p-2 text-gray-400 hover:text-cyan-400 cursor-pointer">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
            <input type="file" id="image-input" accept="image/*" class="hidden" onchange="previewImage(event)">
        </label>

        <button onclick="openVoiceModal()" class="p-2 text-cyan-400 hover:text-cyan-300" title="Voice Mode">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
        </button>

        <input type="text" id="user-input" placeholder="Ask question or type 'Edit this image'..." class="flex-1 bg-gray-900 border border-gray-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500" onkeypress="if(event.key==='Enter') sendMsg()">

        <button onclick="sendMsg()" class="bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs px-4 py-2.5 rounded-xl shadow">
            Send
        </button>
    </div>

    <!-- Live Voice Modal -->
    <div id="voice-overlay" class="fixed inset-0 bg-gray-950/95 backdrop-blur-md hidden z-50 flex flex-col items-center justify-between p-6">
        <div class="w-full flex justify-between items-center">
            <span class="text-xs font-bold text-cyan-400">NEXUS LIVE VOICE TALK</span>
            <button onclick="closeVoiceModal()" class="text-gray-400 text-lg font-bold">✕</button>
        </div>

        <div class="flex flex-col items-center space-y-4 text-center">
            <div id="orb-graphic" class="w-28 h-28 rounded-full bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center pulse-orb shadow-2xl">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
            </div>
            <p id="voice-status-text" class="text-cyan-200 text-sm font-semibold">Tap 'Start Speaking' to talk</p>
            <p id="voice-transcript" class="text-xs text-gray-400 max-w-xs italic"></p>
        </div>

        <div class="w-full flex space-x-3">
            <button onclick="startVoiceRecognition()" class="flex-1 bg-cyan-500 text-black font-bold py-3 rounded-xl text-xs">Start Speaking</button>
            <button onclick="closeVoiceModal()" class="bg-gray-800 text-white px-5 py-3 rounded-xl text-xs border border-gray-700">Close</button>
        </div>
    </div>

    <script>
        let attachedImageBase64 = null;
        let activeRecognition = null;

        function previewImage(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(evt) {
                    attachedImageBase64 = evt.target.result;
                    document.getElementById('image-preview').src = attachedImageBase64;
                    document.getElementById('image-preview-bar').classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        }

        function clearImage() {
            attachedImageBase64 = null;
            document.getElementById('image-input').value = '';
            document.getElementById('image-preview-bar').classList.add('hidden');
        }

        function speakAIResponse(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                // Clean markdown tags for clear speech
                const cleanText = text.replace(/[*_#`]/g, '').replace(/!\[.*?\]\(.*?\)/g, 'Generated Image');
                const utter = new SpeechSynthesisUtterance(cleanText);
                utter.lang = 'ur-PK';
                utter.rate = 1.0;
                window.speechSynthesis.speak(utter);
            }
        }

        function openVoiceModal() {
            document.getElementById('voice-overlay').classList.remove('hidden');
        }

        function startVoiceRecognition() {
            const statusLabel = document.getElementById('voice-status-text');
            const transcriptLabel = document.getElementById('voice-transcript');

            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) {
                statusLabel.innerText = "Safari/Browser Speech API restricted. Please use Chrome or type message.";
                return;
            }

            if (activeRecognition) {
                try { activeRecognition.stop(); } catch(e){}
            }

            activeRecognition = new SpeechRec();
            activeRecognition.continuous = false;
            activeRecognition.interimResults = false;
            activeRecognition.lang = 'ur-PK';

            activeRecognition.onstart = function() {
                statusLabel.innerText = "Listening... Bolna shuru karein!";
            };

            activeRecognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                transcriptLabel.innerText = '"' + text + '"';
                statusLabel.innerText = "Nexus AI thinking & responding...";
                sendVoiceMessage(text);
            };

            activeRecognition.onerror = function(e) {
                statusLabel.innerText = "Mic stopped. Tap 'Start Speaking' again.";
            };

            try { activeRecognition.start(); } catch(err){
                statusLabel.innerText = "Microphone permission error.";
            }
        }

        function closeVoiceModal() {
            if (activeRecognition) try{ activeRecognition.stop(); }catch(e){}
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            document.getElementById('voice-overlay').classList.add('hidden');
        }

        async function sendVoiceMessage(userText) {
            const selectedModel = document.getElementById('ai-model-select').value;
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: userText, model: selectedModel })
                });
                const data = await res.json();
                document.getElementById('voice-status-text').innerText = "Nexus AI Speaking...";
                speakAIResponse(data.reply);
            } catch(e) {
                document.getElementById('voice-status-text').innerText = "Connection error.";
            }
        }

        async function sendMsg() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            const chatBox = document.getElementById('chat-box');
            const selectedModel = document.getElementById('ai-model-select').value;

            if (!text && !attachedImageBase64) return;

            let userMsgHTML = `<div class="bg-cyan-950/70 text-cyan-100 p-3 rounded-xl max-w-[85%] ml-auto text-xs border border-cyan-800/50">`;
            if (attachedImageBase64) {
                userMsgHTML += `<img src="${attachedImageBase64}" class="w-28 h-28 object-cover rounded-lg mb-1 border border-cyan-700">`;
            }
            if (text) userMsgHTML += `<p>${text}</p>`;
            userMsgHTML += `</div>`;

            chatBox.innerHTML += userMsgHTML;

            const currentImg = attachedImageBase64;
            clearImage();
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const loadingId = 'load-' + Date.now();
            chatBox.innerHTML += `<div id="${loadingId}" class="bg-gray-800 p-3 rounded-xl max-w-[85%] text-xs text-gray-400 italic">Nexus AI processing request...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: text, image: currentImg, model: selectedModel })
                });
                const data = await res.json();
                
                let responseContent = data.reply;
                if (data.image_url) {
                    responseContent += `<br><br><img src="${data.image_url}" class="w-64 h-64 object-cover rounded-xl border border-cyan-500 mt-2 shadow-lg">`;
                }

                document.getElementById(loadingId).outerHTML = `<div class="bg-gray-800 p-3 rounded-xl max-w-[85%] text-xs border border-gray-700/60 leading-relaxed"><strong class="text-cyan-400 block mb-1">Nexus AI [${selectedModel.toUpperCase()}]</strong>${responseContent}</div>`;
                speakAIResponse(data.reply);
            } catch(err) {
                document.getElementById(loadingId).outerHTML = `<div class="bg-gray-800 p-3 rounded-xl max-w-[85%] text-xs border border-gray-700/60 leading-relaxed"><strong class="text-cyan-400 block mb-1">Nexus AI</strong>Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.</div>`;
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

def process_identity_check(text: str) -> bool:
    keywords = ["kisne banaya", "who made", "who created", "who is your creator", "da cha ye", "cha jor kare", "owner", "creator", "sadam"]
    return any(kw in text.lower() for kw in keywords)

def generate_edited_image(prompt: str) -> str:
    clean_prompt = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=800&height=800&nologo=true&seed=42"

def fetch_text_response(user_text: str, model_type: str) -> str:
    encoded_text = urllib.parse.quote(user_text)
    url = f"https://text.pollinations.ai/{encoded_text}?model={model_type}&system={urllib.parse.quote(SYSTEM_PROMPT)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            res = response.read().decode("utf-8").strip()
            if res:
                return res
    except Exception as e:
        print(f"API Error: {e}")
    return ""

# 2. Endpoints
@app.post("/api/chat")
@app.post("/api/chat/v2")
async def handle_chat_request(payload: ChatPayload):
    user_message = payload.message.strip() if payload.message else ""
    user_image = payload.image
    selected_model = payload.model or "openai"

    # Identity Check
    if user_message and process_identity_check(user_message):
        return {"reply": IDENTITY_RESPONSE, "response": IDENTITY_RESPONSE, "image_url": None}

    # Image Generation / Editing Trigger
    image_keywords = ["edit", "generate", "image", "photo", "tasveer", "picture", "logo", "draw", "make image", "edit karo"]
    is_image_request = any(kw in user_message.lower() for kw in image_keywords) or (user_image and is_image_request)

    if is_image_request or (user_image and ("edit" in user_message.lower() or not user_message)):
        prompt = user_message if user_message else "Professional edited high quality 3D neon logo of NX Nexus AI"
        image_url = generate_edited_image(f"professional ultra detailed edited version: {prompt}")
        reply_text = f"Yeh lijiye aapki requested edited/generated image ready hai:"
        return {"reply": reply_text, "response": reply_text, "image_url": image_url, "status": "success"}

    # Text Chat Route
    ai_reply = fetch_text_response(user_message or "Hello Nexus AI", selected_model)
    if not ai_reply:
        ai_reply = "Nexus AI: Aapka paigham mil gaya hai. Aap trading, programming, ya koi bhi sawal pooch sakte hain!"

    return {"reply": ai_reply, "response": ai_reply, "image_url": None, "status": "success"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"reply": IDENTITY_RESPONSE, "response": IDENTITY_RESPONSE, "image_url": None}
    )
