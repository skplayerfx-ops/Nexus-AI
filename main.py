from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


Role = Literal["user", "assistant"]
ROOT = Path(__file__).parent


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


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/api/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/conversations", response_model=list[Conversation])
def list_conversations() -> list[Conversation]:
    return sorted(
        conversations.values(),
        key=lambda item: item.updatedAt,
        reverse=True,
    )


@app.get("/api/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str) -> ConversationDetail:
    item = conversations.get(conversation_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return item


def assistant_reply(prompt: str) -> str:
    text = " ".join(prompt.strip().split())
    lower = text.lower()
    if "plan" in lower or "priorit" in lower:
        return "Start by naming the outcome that matters most. Then reduce the next step until it can be completed in one sitting. A short, visible sequence is usually more useful than a perfect plan."
    if "write" in lower or "draft" in lower:
        return "Give me the audience, the point you want them to remember, and the tone you want to land. I can turn that into a first draft, then help you tighten it."
    if "idea" in lower or "brainstorm" in lower:
        return "Let’s widen the field before we judge it. List the obvious options first, then add one that feels too ambitious and one that feels almost too simple. The contrast usually reveals the interesting direction."
    return f"Here’s a useful first pass on “{text}”: make the next action concrete, keep the scope narrow, and decide what evidence would tell you it is working. I can help you turn that into a plan, draft, or checklist."


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatInput) -> ChatResponse:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be empty")

    conversation_id = payload.conversationId or str(uuid4())
    item = conversations.get(conversation_id)
    if item is None:
        item = conversation(conversation_id, "New conversation", [])
        conversations[conversation_id] = item

    item.messages.extend(
        [
            message("user", prompt),
            message("assistant", assistant_reply(prompt)),
        ]
    )
    if item.title == "New conversation":
        item.title = " ".join(prompt.split()[:6]).rstrip(".,:;") or "New conversation"
    item.preview = item.messages[-1].content
    item.updatedAt = item.messages[-1].createdAt
    item.messageCount = len(item.messages)

    return ChatResponse(conversation=item, assistantMessage=item.messages[-1])