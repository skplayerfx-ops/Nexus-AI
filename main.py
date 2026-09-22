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

# 1. Full Advanced Dashboard Web UI
@app.get("/", response_class=HTMLResponse)
async def serve_home_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus AI — Multi-Model Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b0f17; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; }
        .sidebar { background-color: #111827; }
        .card { background-color: #111827; border: 1px solid #1f2937; }
        .voice-pulse {
            box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.7);
            animation: pulse-ring 1.5s infinite cubic-bezier(0.66, 0, 0, 1);
        }
        @keyframes pulse-ring {
            to { box-shadow: 0 0 0 35px rgba(6, 182, 212, 0); }
        }
    </style>
</head>
<body class="flex flex-col md:flex-row min-h-screen relative overflow-x-hidden">

    <!-- Mobile Header -->
    <header class="md:hidden flex items-center justify-between p-4 bg-gray-900 border-b border-gray-800">
        <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-white font-bold text-base shadow-lg">NX</div>
            <div>
                <h1 class="font-bold text-sm text-white">NEXUS AI</h1>
                <p class="text-[10px] text-gray-400">By Mr. Sadam Hussain</p>
            </div>
        </div>
        <button onclick="toggleMobileMenu()" class="text-gray-400 hover:text-white p-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>
    </header>

    <!-- Sidebar Navigation -->
    <aside id="sidebar-menu" class="hidden md:flex w-full md:w-64 sidebar flex-col justify-between p-4 flex-shrink-0 border-r border-gray-800">
        <div>
            <div class="hidden md:flex items-center space-x-3 mb-6 px-2">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">NX</div>
                <div>
                    <h1 class="font-bold text-lg text-white">NEXUS AI</h1>
                    <p class="text-xs text-gray-400">By Mr. Sadam Hussain</p>
                </div>
            </div>

            <!-- AI Engine Selector -->
            <div class="space-y-4">
                <div class="card p-3 rounded-xl border-cyan-500/30">
                    <label class="text-xs font-semibold text-cyan-400 uppercase tracking-wider block mb-2">🤖 Select AI Engine</label>
                    <select id="ai-model-select" class="w-full bg-gray-800 text-xs border border-cyan-500/40 text-white rounded-lg p-2.5 focus:outline-none focus:border-cyan-400 font-medium">
                        <option value="auto" selected>✨ Nexus AI (Auto Smart Engine)</option>
                        <option value="gpt-4o">⚡ ChatGPT (GPT-4o Vision)</option>
                        <option value="claude-3-5">🧠 Claude 3.5 Sonnet</option>
                        <option value="gemini-1-5">♊ Google Gemini 1.5 Pro</option>
                        <option value="deepseek-r1">🔍 DeepSeek R1 Reasoner</option>
                        <option value="llama-3-3">🦙 Meta Llama 3.3 70B</option>
                        <option value="image-edit-engine">🎨 Image Editing Engine</option>
                    </select>
                </div>

                <div class="card p-3 rounded-xl border-gray-800">
                    <label class="text-xs font-semibold text-gray-300 uppercase tracking-wider block mb-2">🎙️ AI Voice Gender</label>
                    <select id="voice-gender" class="w-full bg-gray-800 text-xs border border-gray-700 text-gray-200 rounded-lg p-2 focus:outline-none">
                        <option value="female">Female AI Voice</option>
                        <option value="male">Male AI Voice</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="text-center p-2 text-[11px] text-gray-500 border-t border-gray-800/80">
            Nexus AI System v2.5 • All AIs Integrated
        </div>
    </aside>

    <!-- Main Workspace -->
    <main class="flex-1 flex flex-col p-4 md:p-6 justify-between h-[calc(100vh-60px)] md:h-screen">
        
        <div class="flex justify-between items-center mb-4">
            <div>
                <h2 class="text-lg md:text-xl font-bold text-white flex items-center gap-2">
                    <span>Nexus Multi-AI Assistant</span>
                </h2>
                <p class="text-xs text-gray-400">ChatGPT, Claude, Gemini, DeepSeek & Llama combined in one</p>
            </div>

            <button onclick="openVoiceDashboard()" class="bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-2 rounded-xl font-semibold text-xs text-white shadow-lg flex items-center space-x-2 hover:opacity-90">
                <span class="w-2 h-2 rounded-full bg-green-400 animate-ping"></span>
                <span>Gemini Live Voice Mode</span>
            </button>
        </div>

        <!-- Chat Display Area -->
        <div class="flex-1 card rounded-xl p-4 overflow-y-auto space-y-4 mb-4" id="chat-box">
            <div class="bg-gray-800 p-3.5 rounded-xl max-w-xl text-sm border border-gray-700/50 shadow-sm">
                <strong class="text-cyan-400 block mb-1">Nexus AI Engine</strong>
                Salam! Main Nexus AI hu. Mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.<br><br>
                Aap sidebar se **ChatGPT, Claude, Gemini, DeepSeek, ya Llama** chun sakte hain. Image upload karein ya voice mic button par tap karke baat karein!
            </div>
        </div>

        <!-- Image Attached Preview -->
        <div id="image-preview-container" class="hidden mb-2 p-2 bg-gray-800 rounded-lg flex items-center justify-between border border-cyan-500/30">
            <div class="flex items-center space-x-3">
                <img id="image-preview" class="w-12 h-12 object-cover rounded-lg border border-gray-700">
                <span class="text-xs text-cyan-400 font-medium">Image attached</span>
            </div>
            <button onclick="removeAttachedImage()" class="text-gray-400 hover:text-red-400 text-xs font-bold px-2 py-1">✕ Remove</button>
        </div>

        <!-- Toolbar / Input Box -->
        <div class="flex items-center gap-2 bg-gray-900 border border-gray-800 p-2 rounded-xl">
            <!-- Image Upload Button -->
            <label class="cursor-pointer p-2 text-gray-400 hover:text-cyan-400 hover:bg-gray-800 rounded-lg transition" title="Attach Image">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                <input type="file" id="image-input" accept="image/*" class="hidden" onchange="handleImageSelect(event)">
            </label>

            <!-- Voice Mic Button -->
            <button onclick="openVoiceDashboard()" class="p-2 text-cyan-400 hover:bg-gray-800 rounded-lg transition" title="Live Voice Chat">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
            </button>

            <input type="text" id="user-input" placeholder="Ask Nexus AI or select model..." class="flex-1 bg-transparent text-white px-2 py-2 text-sm focus:outline-none" onkeypress="if(event.key==='Enter') sendMessage()">

            <button onclick="sendMessage()" class="bg-cyan-500 px-5 py-2.5 rounded-lg font-bold text-black hover:bg-cyan-400 text-sm shadow-md transition">
                Send
            </button>
        </div>

    </main>

    <!-- Voice Live Overlay -->
    <div id="voice-overlay" class="fixed inset-0 bg-slate-950/95 backdrop-blur-xl hidden z-50 flex flex-col items-center justify-between p-8">
        <div class="w-full flex justify-between items-center">
            <span class="text-cyan-400 font-bold tracking-wider text-sm flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                NEXUS LIVE VOICE MODE
            </span>
            <button onclick="closeVoiceDashboard()" class="text-gray-400 hover:text-white text-xl p-2">✕</button>
        </div>

        <div class="flex flex-col items-center justify-center space-y-6">
            <div id="voice-orb" class="w-32 h-32 rounded-full bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center voice-pulse transition-all duration-300">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
            </div>
            <p id="voice-status" class="text-cyan-200 text-lg font-medium tracking-wide">Tap orb to speak...</p>
            <p id="voice-transcription" class="text-gray-400 text-sm max-w-md text-center italic"></p>
        </div>

        <div class="flex items-center space-x-6">
            <button onclick="toggleVoiceListening()" class="bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-8 py-3 rounded-full text-sm shadow-lg transition">
                Start Speaking
            </button>
            <button onclick="closeVoiceDashboard()" class="bg-gray-800 hover:bg-gray-700 text-white font-medium px-6 py-3 rounded-full text-sm border border-gray-700 transition">
                Exit Voice
            </button>
        </div>
    </div>

    <script>
        let selectedImageData = null;
        let recognition = null;

        function toggleMobileMenu() {
            document.getElementById('sidebar-menu').classList.toggle('hidden');
        }

        function handleImageSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedImageData = e.target.result;
                    document.getElementById('image-preview').src = selectedImageData;
                    document.getElementById('image-preview-container').classList.remove('hidden');
                }
                reader.readAsDataURL(file);
            }
        }

        function removeAttachedImage() {
            selectedImageData = null;
            document.getElementById('image-input').value = '';
            document.getElementById('image-preview-container').classList.add('hidden');
        }

        function openVoiceDashboard() {
            document.getElementById('voice-overlay').classList.remove('hidden');
            toggleVoiceListening();
        }

        function closeVoiceDashboard() {
            if (recognition) recognition.stop();
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            document.getElementById('voice-overlay').classList.add('hidden');
        }

        function toggleVoiceListening() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert('Aapke browser mein voice recognition support nahi ho raha.');
                return;
            }

            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'ur-PK';

            const statusTxt = document.getElementById('voice-status');
            const transTxt = document.getElementById('voice-transcription');

            recognition.onstart = function() {
                statusTxt.innerText = "Listening... Bolna shuru karein";
            };

            recognition.onresult = function(event) {
                let transcript = event.results[0][0].transcript;
                transTxt.innerText = '"' + transcript + '"';
                statusTxt.innerText = "Processing...";
                processVoiceMessage(transcript);
            };

            recognition.onerror = function(e) {
                statusTxt.innerText = "Listening stopped. Tap 'Start Speaking' to try again.";
            };

            try {
                recognition.start();
            } catch(e) {}
        }

        async function processVoiceMessage(userText) {
            const selectedModel = document.getElementById('ai-model-select') ? document.getElementById('ai-model-select').value : 'auto';
            let replyText = "";

            try {
                let response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userText, model: selectedModel })
                });

                const data = await response.json();
                replyText = data.reply || data.response;
            } catch (e) {
                replyText = "Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.";
            }

            document.getElementById('voice-status').innerText = "Nexus AI Speaking...";
            speakText(replyText, function() {
                document.getElementById('voice-status').innerText = "Tap orb to speak again";
            });
        }

        function speakText(text, onEndCallback) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'ur-PK';
                
                const genderSelect = document.getElementById('voice-gender');
                const gender = genderSelect ? genderSelect.value : 'female';
                const voices = window.speechSynthesis.getVoices();

                if (gender === 'female') {
                    const fVoice = voices.find(v => v.name.includes('Female') || v.name.includes('Google UK English Female'));
                    if (fVoice) utterance.voice = fVoice;
                    utterance.pitch = 1.1;
                } else {
                    const mVoice = voices.find(v => v.name.includes('Male') || v.name.includes('Google UK English Male'));
                    if (mVoice) utterance.voice = mVoice;
                    utterance.pitch = 0.9;
                }

                utterance.onend = function() {
                    if (onEndCallback) onEndCallback();
                };

                window.speechSynthesis.speak(utterance);
            }
        }

        async function sendMessage() {
            const inputField = document.getElementById('user-input');
            const text = inputField.value.trim();
            const chatBox = document.getElementById('chat-box');
            const modelSelect = document.getElementById('ai-model-select');
            const selectedModel = modelSelect ? modelSelect.value : 'auto';

            if (!text && !selectedImageData) return;

            let userHTML = `<div class="bg-cyan-950/60 text-cyan-100 p-3.5 rounded-xl max-w-xl ml-auto text-sm border border-cyan-800/50">`;
            if (selectedImageData) {
                userHTML += `<img src="${selectedImageData}" class="w-32 h-32 object-cover rounded-lg mb-2 border border-cyan-700">`;
            }
            if (text) userHTML += `<p>${text}</p>`;
            userHTML += `</div>`;
            chatBox.innerHTML += userHTML;

            const tempImage = selectedImageData;
            removeAttachedImage();
            inputField.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            let aiReply = "";

            try {
                let response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, image: tempImage, model: selectedModel })
                });

                const data = await response.json();
                aiReply = data.reply || data.response;
            } catch (err) {
                aiReply = "Main Nexus AI hu aur mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai.";
            }

            let responseHTML = `<div class="bg-gray-800 p-3.5 rounded-xl max-w-xl text-sm border border-gray-700/50 shadow-sm"><strong class="text-cyan-400 block mb-1">Nexus AI [${selectedModel.toUpperCase()}]</strong>${aiReply}</div>`;

            chatBox.innerHTML += responseHTML;
            speakText(aiReply);
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

# 2. Backend Routing
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
        ai_reply = IDENTITY_RESPONSE if not user_message else f"Main aapki baat samajhta hu. Aap Urdu, Pashto ya English mein sawal kar sakte hain."

    return {"reply": ai_reply, "response": ai_reply, "status": "success"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"reply": IDENTITY_RESPONSE, "response": IDENTITY_RESPONSE}
    )
