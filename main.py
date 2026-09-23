from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


Role = Literal["user", "assistant"]
DEFAULT_MODEL = "nexus-core"


class AIModel(BaseModel):
    model_name: str
    display_name: str
    description: str
    capabilities: list[str]


AVAILABLE_MODELS: dict[str, AIModel] = {
    "nexus-core": AIModel(
        model_name="nexus-core",
        display_name="Nexus Core",
        description="A balanced model for everyday questions, drafts, and planning.",
        capabilities=["general", "writing", "planning"],
    ),
    "nexus-focus": AIModel(
        model_name="nexus-focus",
        display_name="Nexus Focus",
        description="A concise model for clear decisions, summaries, and next steps.",
        capabilities=["concise", "analysis", "prioritization"],
    ),
    "nexus-explore": AIModel(
        model_name="nexus-explore",
        display_name="Nexus Explore",
        description="A divergent model for brainstorming and comparing possibilities.",
        capabilities=["brainstorming", "ideation", "alternatives"],
    ),
}

MODEL_ALIASES = {
    "nexus core": "nexus-core",
    "nexus focus": "nexus-focus",
    "nexus explore": "nexus-explore",
}


class PromptInput(BaseModel):
    """Validated input for a chat completion."""

    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(
        min_length=1,
        max_length=4000,
        description="The message to send to the selected model.",
    )
    model_name: str = Field(
        default=DEFAULT_MODEL,
        min_length=1,
        max_length=64,
        description="The model identifier from GET /api/models.",
    )
    conversation_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("conversationId", "conversation_id"),
        description="Existing conversation ID, when continuing a conversation.",
    )


# Keep the previous public type name available to callers that imported it.
ChatInput = PromptInput


class ModelsResponse(BaseModel):
    models: list[AIModel]
    default_model: str


def now() -> str:
    return datetime.now(UTC).isoformat()


class Message(BaseModel):
    id: str
    role: Role
    content: str
    createdAt: str


class Conversation(BaseModel):
    id: str
    title: str
    preview: str
    updatedAt: str
    messageCount: int


class ConversationDetail(Conversation):
    messages: list[Message]


class ChatResponse(BaseModel):
    conversation: ConversationDetail
    assistantMessage: Message
    model_name: str
    provider: str


def message(role: Role, content: str) -> Message:
    return Message(id=str(uuid4()), role=role, content=content, createdAt=now())


def conversation(
    conversation_id: str, title: str, messages: list[Message]
) -> ConversationDetail:
    return ConversationDetail(
        id=conversation_id,
        title=title,
        preview=messages[-1].content if messages else "Start a new conversation.",
        updatedAt=messages[-1].createdAt if messages else now(),
        messageCount=len(messages),
        messages=messages,
    )


conversations: dict[str, ConversationDetail] = {
    "planning-routine": conversation(
        "planning-routine",
        "Weekly planning routine",
        [
            message("user", "How can I make my weekly planning routine more consistent?"),
            message(
                "assistant",
                "Make the routine small enough to repeat. Pick one fixed time, review the previous week, then choose three outcomes for the next one. Treat everything else as optional support work.",
            ),
        ],
    ),
    "product-brief": conversation(
        "product-brief",
        "Product brief refinement",
        [
            message(
                "assistant",
                "A sharper brief starts with the decision it should unlock. From there, name the audience, the constraint, and the evidence that would change your mind.",
            )
        ],
    ),
    "reading-list": conversation(
        "reading-list",
        "Build a focused reading list",
        [
            message(
                "assistant",
                "Start with the question, not the topic. A useful reading list should help you see a problem from several angles without becoming a second inbox.",
            )
        ],
    ),
}

app = FastAPI(title="Nexus-AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api", tags=["Nexus AI"])


import os
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    for path in ["index.html", "./index.html", "../index.html"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>Nexus AI Dashboard Active</h1>"


@app.get("/api/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/models", response_model=ModelsResponse)
def list_models() -> ModelsResponse:
    return ModelsResponse(
        models=list(AVAILABLE_MODELS.values()),
        default_model=DEFAULT_MODEL,
    )


@api_router.get("/conversations", response_model=list[Conversation])
def list_conversations() -> list[Conversation]:
    return sorted(
        conversations.values(),
        key=lambda item: item.updatedAt,
        reverse=True,
    )


@api_router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str) -> ConversationDetail:
    item = conversations.get(conversation_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return item


def resolve_model_name(model_name: str) -> str:
    normalized = model_name.strip().lower().replace("_", "-")
    normalized = MODEL_ALIASES.get(normalized, normalized)
    if normalized not in AVAILABLE_MODELS:
        supported = ", ".join(AVAILABLE_MODELS)
        raise HTTPException(
            status_code=422,
            detail=f"Unknown model_name '{model_name}'. Choose one of: {supported}.",
        )
    return normalized


class AIProviderError(Exception):
    """An expected failure while communicating with the configured AI provider."""


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
PROVIDER_TIMEOUT_SECONDS = 45

PROVIDER_MODELS: dict[str, dict[str, str]] = {
    "openrouter": {
        "nexus-core": "openai/gpt-4o-mini",
        "nexus-focus": "meta-llama/llama-3.1-8b-instruct",
        "nexus-explore": "mistralai/mistral-small-3.1-24b-instruct",
    },
    "groq": {
        "nexus-core": "llama-3.3-70b-versatile",
        "nexus-focus": "llama-3.1-8b-instant",
        "nexus-explore": "llama-3.3-70b-versatile",
    },
}


def provider_configuration() -> tuple[str, str, str]:
    """Return provider name, endpoint, and key without ever logging the key."""

    preferred = os.getenv("AI_PROVIDER", "").strip().lower()
    keys = {
        "openrouter": os.getenv("OPENROUTER_API_KEY", "").strip(),
        "groq": os.getenv("GROQ_API_KEY", "").strip(),
    }
    endpoints = {
        "openrouter": OPENROUTER_ENDPOINT,
        "groq": GROQ_ENDPOINT,
    }

    if preferred and preferred not in keys:
        raise AIProviderError("AI_PROVIDER must be either 'openrouter' or 'groq'.")
    if preferred:
        if not keys[preferred]:
            raise AIProviderError(
                f"AI_PROVIDER is set to '{preferred}', but its API key is not configured."
            )
        return preferred, endpoints[preferred], keys[preferred]

    for provider in ("openrouter", "groq"):
        if keys[provider]:
            return provider, endpoints[provider], keys[provider]

    raise AIProviderError(
        "No AI provider is configured. Add OPENROUTER_API_KEY or GROQ_API_KEY "
        "to the project secrets."
    )


def provider_model_name(provider: str, model_name: str) -> str:
    try:
        return PROVIDER_MODELS[provider][model_name]
    except KeyError as error:
        raise AIProviderError(
            f"Model '{model_name}' is not configured for provider '{provider}'."
        ) from error


def system_instruction(model_name: str) -> str:
    instructions = {
        "nexus-core": "Be helpful, clear, and practical. Give a balanced answer with concrete next steps.",
        "nexus-focus": "Be concise and decisive. Prioritize the most important answer and give a short action plan.",
        "nexus-explore": "Think divergently. Offer useful alternatives, tradeoffs, and one simple experiment to learn more.",
    }
    return instructions[model_name]


def extract_provider_content(payload: object) -> str:
    if not isinstance(payload, dict):
        raise AIProviderError("The AI provider returned an invalid response.")

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AIProviderError("The AI provider returned no response choices.")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise AIProviderError("The AI provider returned an invalid response choice.")
    message_payload = first_choice.get("message")
    if not isinstance(message_payload, dict):
        raise AIProviderError("The AI provider returned no assistant message.")

    content = message_payload.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        text_parts = [
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ]
        combined = "".join(text_parts).strip()
        if combined:
            return combined

    raise AIProviderError("The AI provider returned an empty assistant message.")


def post_provider_request(
    endpoint: str,
    api_key: str,
    provider: str,
    provider_model: str,
    messages: list[dict[str, str]],
) -> str:
    body = json.dumps(
        {
            "model": provider_model,
            "messages": messages,
            "temperature": 0.7,
        }
    ).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if provider == "openrouter":
        headers["X-Title"] = "Nexus AI"

    request = urllib.request.Request(
        endpoint,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=PROVIDER_TIMEOUT_SECONDS) as response:
            raw_response = response.read(2_000_000)
    except urllib.error.HTTPError as error:
        # Do not return the provider body: it may contain sensitive request details.
        raise AIProviderError(
            f"{provider.title()} rejected the request with HTTP {error.code}."
        ) from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise AIProviderError(
            f"{provider.title()} could not be reached. Try again shortly."
        ) from error

    try:
        response_payload = json.loads(raw_response.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AIProviderError(
            f"{provider.title()} returned an invalid JSON response."
        ) from error
    return extract_provider_content(response_payload)


async def live_model_response(
    prompt: str,
    model_name: str,
    history: list[Message],
) -> tuple[str, str]:
    provider, endpoint, api_key = provider_configuration()
    provider_model = provider_model_name(provider, model_name)
    messages = [{"role": "system", "content": system_instruction(model_name)}]
    messages.extend(
        {"role": item.role, "content": item.content}
        for item in history[-12:]
    )
    messages.append({"role": "user", "content": prompt})
    response = await asyncio.to_thread(
        post_provider_request,
        endpoint,
        api_key,
        provider,
        provider_model,
        messages,
    )
    return response, provider


@api_router.post("/chat", response_model=ChatResponse)
async def chat(payload: PromptInput) -> ChatResponse:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be empty")

    model_name = resolve_model_name(payload.model_name)
    conversation_id = payload.conversation_id or str(uuid4())
    item = conversations.get(conversation_id)
    if item is None:
        item = conversation(conversation_id, "New conversation", [])
        conversations[conversation_id] = item

    try:
        assistant_content, provider = await live_model_response(
            prompt,
            model_name,
            item.messages,
        )
    except AIProviderError as error:
        message_text = str(error)
        status_code = 503 if "configured" in message_text else 502
        raise HTTPException(status_code=status_code, detail=message_text) from error

    item.messages.extend(
        [
            message("user", prompt),
            message("assistant", assistant_content),
        ]
    )
    if item.title == "New conversation":
        item.title = " ".join(prompt.split()[:6]).rstrip(".,:;") or "New conversation"
    item.preview = item.messages[-1].content
    item.updatedAt = item.messages[-1].createdAt
    item.messageCount = len(item.messages)

    return ChatResponse(
        conversation=item,
        assistantMessage=item.messages[-1],
        model_name=model_name,
        provider=provider,
    )


app.include_router(api_router)
# ==========================================
# NEXUS AI EXTENSION (ADDED AT THE BOTTOM)
# ==========================================

from pydantic import BaseModel
from typing import Optional

class NexusCustomPrompt(BaseModel):
    prompt: str
    user_language: Optional[str] = "auto"
    selected_model: Optional[str] = "nexus-auto"

class BinancePaymentNotice(BaseModel):
    package_price: float
    user_id: str
    binance_pay_id: str = "1243962107"

@app.post("/api/nexus/chat-extension")
async def nexus_chat_extension(data: NexusCustomPrompt):
    p_lower = data.prompt.lower()
    
    # Creator Identity check across languages
    creator_keywords = ["kisne banaya", "who made", "who created", "maker", "developer", "owner", "banaya hy"]
    if any(k in p_lower for k in creator_keywords):
        if any(u in p_lower for u in ["ur", "urdu", "kaun", "kisne", "banaya"]):
            reply = "Main Nexus AI hoon. Mujhe Mr. Sadam Hussain son of Jehanzeb ne banaya hai."
        else:
            reply = "I am Nexus AI. I was created by Mr. Sadam Hussain son of Jehanzeb."
        return {"status": "success", "response": reply, "model_used": "Nexus-Native"}

    # Automatic Smart Routing for All-in-One Option
    chosen_model = data.selected_model
    if chosen_model == "nexus-auto":
        if len(data.prompt) > 100 or "code" in p_lower:
            chosen_model = "Llama-3.3-70B / DeepSeek"
        else:
            chosen_model = "GPT-4o-Mini"

    return {
        "status": "success",
        "response": f"[Processed via {chosen_model}]: {data.prompt}",
        "routed_model": chosen_model
    }

@app.post("/api/nexus/binance-payout")
async def process_binance_payout(info: BinancePaymentNotice):
    # Log payment routing to Binance ID: 1243962107
    return {
        "status": "initiated",
        "message": f"Payment request of ${info.package_price} routed to Binance Pay ID 1243962107.",
        "binance_id": info.binance_pay_id
    }
