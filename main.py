from __future__ import annotations

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


class ChatInput(BaseModel):
    conversationId: str | None = None
    prompt: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    conversation: ConversationDetail
    assistantMessage: Message
    model_name: str


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


@app.get("/", include_in_schema=False)
@app.get("/api/", include_in_schema=False)
@app.get("/api", include_in_schema=False)
def hello_world() -> dict[str, str]:
    return {"message": "Hello, World!"}


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


def assistant_reply(prompt: str, model_name: str = DEFAULT_MODEL) -> str:
    text = " ".join(prompt.strip().split())
    lower = text.lower()
    if model_name == "nexus-focus":
        if "plan" in lower or "priorit" in lower:
            return "Choose the most important outcome, define one next action, and schedule it. Defer everything that does not support that outcome."
        return f"First pass on “{text}”: define the outcome, choose the smallest next action, and decide how you will measure progress."
    if model_name == "nexus-explore":
        if "idea" in lower or "brainstorm" in lower:
            return "Generate three safe options, one ambitious option, and one deliberately simple option. Compare them by effort, upside, and what you would learn."
        return f"Explore “{text}” from three angles: the obvious approach, a more ambitious alternative, and the simplest useful experiment."
    if "plan" in lower or "priorit" in lower:
        return "Start by naming the outcome that matters most. Then reduce the next step until it can be completed in one sitting. A short, visible sequence is usually more useful than a perfect plan."
    if "write" in lower or "draft" in lower:
        return "Give me the audience, the point you want them to remember, and the tone you want to land. I can turn that into a first draft, then help you tighten it."
    if "idea" in lower or "brainstorm" in lower:
        return "Let’s widen the field before we judge it. List the obvious options first, then add one that feels too ambitious and one that feels almost too simple. The contrast usually reveals the interesting direction."
    return f"Here’s a useful first pass on “{text}”: make the next action concrete, keep the scope narrow, and decide what evidence would tell you it is working. I can help you turn that into a plan, draft, or checklist."


@api_router.post("/chat", response_model=ChatResponse)
def chat(payload: PromptInput) -> ChatResponse:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be empty")

    model_name = resolve_model_name(payload.model_name)
    conversation_id = payload.conversation_id or str(uuid4())
    item = conversations.get(conversation_id)
    if item is None:
        item = conversation(conversation_id, "New conversation", [])
        conversations[conversation_id] = item

    item.messages.extend(
        [
            message("user", prompt),
            message("assistant", assistant_reply(prompt, model_name)),
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
    )


app.include_router(api_router)