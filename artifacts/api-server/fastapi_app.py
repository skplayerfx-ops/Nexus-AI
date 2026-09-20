from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


Role = Literal["user", "assistant"]


def timestamp() -> str:
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


def make_message(role: Role, content: str) -> Message:
    return Message(id=str(uuid4()), role=role, content=content, createdAt=timestamp())


def make_conversation(
    conversation_id: str, title: str, preview: str, messages: list[Message]
) -> ConversationDetail:
    updated_at = messages[-1].createdAt if messages else timestamp()
    return ConversationDetail(
        id=conversation_id,
        title=title,
        preview=preview,
        updatedAt=updated_at,
        messageCount=len(messages),
        messages=messages,
    )


seed_messages = [
    make_message(
        "user",
        "How can I make my weekly planning routine more consistent?",
    ),
    make_message(
        "assistant",
        "Make the routine small enough to repeat. Pick one fixed time, review the previous week, then choose three outcomes for the next one. Treat everything else as optional support work.",
    ),
]

conversations: dict[str, ConversationDetail] = {
    "planning-routine": make_conversation(
        "planning-routine",
        "Weekly planning routine",
        "Make the routine small enough to repeat.",
        seed_messages,
    ),
    "product-brief": make_conversation(
        "product-brief",
        "Product brief refinement",
        "A sharper brief starts with the decision it should unlock.",
        [
            make_message(
                "assistant",
                "A sharper brief starts with the decision it should unlock. From there, name the audience, the constraint, and the evidence that would change your mind.",
            )
        ],
    ),
    "reading-list": make_conversation(
        "reading-list",
        "Build a focused reading list",
        "Start with the question, not the topic.",
        [
            make_message(
                "assistant",
                "Start with the question, not the topic. A useful reading list should help you see a problem from several angles without becoming a second inbox.",
            )
        ],
    ),
}

app = FastAPI(title="Nexus-AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/conversations", response_model=list[Conversation])
def list_conversations() -> list[Conversation]:
    return [
        Conversation(
            id=conversation.id,
            title=conversation.title,
            preview=conversation.preview,
            updatedAt=conversation.updatedAt,
            messageCount=conversation.messageCount,
        )
        for conversation in sorted(
            conversations.values(), key=lambda item: item.updatedAt, reverse=True
        )
    ]


@app.get(
    "/api/conversations/{conversation_id}",
    response_model=ConversationDetail,
)
def get_conversation(conversation_id: str) -> ConversationDetail:
    conversation = conversations.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def response_for(prompt: str) -> str:
    cleaned = " ".join(prompt.strip().split())
    lower = cleaned.lower()
    if "plan" in lower or "priorit" in lower:
        return "Start by naming the outcome that matters most. Then reduce the next step until it can be completed in one sitting. A short, visible sequence is usually more useful than a perfect plan."
    if "write" in lower or "draft" in lower:
        return "Give me the audience, the point you want them to remember, and the tone you want to land. I can turn that into a first draft, then help you tighten it."
    if "idea" in lower or "brainstorm" in lower:
        return "Let’s widen the field before we judge it. List the obvious options first, then add one that feels too ambitious and one that feels almost too simple. The contrast usually reveals the interesting direction."
    return f"Here’s a useful first pass on “{cleaned}”: make the next action concrete, keep the scope narrow, and decide what evidence would tell you it is working. I can help you turn that into a plan, draft, or checklist."


@app.post("/api/chat", response_model=ChatResponse)
def send_chat_message(payload: ChatInput) -> ChatResponse:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="Prompt cannot be empty")

    conversation_id = payload.conversationId
    if conversation_id is None:
        conversation_id = str(uuid4())
        conversations[conversation_id] = make_conversation(
            conversation_id,
            "New conversation",
            prompt,
            [],
        )

    conversation = conversations.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_message = make_message("user", prompt)
    assistant_message = make_message("assistant", response_for(prompt))
    conversation.messages.extend([user_message, assistant_message])
    conversation.title = (
        conversation.title
        if conversation.title != "New conversation"
        else " ".join(prompt.split()[:6]).rstrip(".,:;")
    )
    conversation.preview = assistant_message.content
    conversation.updatedAt = assistant_message.createdAt
    conversation.messageCount = len(conversation.messages)

    return ChatResponse(
        conversation=conversation,
        assistantMessage=assistant_message,
    )