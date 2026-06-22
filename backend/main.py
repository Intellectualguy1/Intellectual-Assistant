from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from context_resolver import resolve_contextual_message
from conversation import build_search_query, get_conversation_response
from database import initialize_database
from knowledge_base import search_knowledge
from llm_provider import generate_response
from memory import (
    get_conversation_messages,
    get_recent_history,
    save_message,
)
from schemas import (
    ChatRequest,
    ChatResponse,
    ConversationMessage,
    Source,
)
from web_search import search_web


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Initializes persistent storage before the API starts.

    Time Complexity:
    - O(1) for normal application startup.
    """
    initialize_database()
    yield


app = FastAPI(
    title="Intellectual Assistant",
    version="0.6.0",
    description=(
        "An open-source AI assistant with persistent conversation memory, "
        "knowledge-base retrieval, web-search fallback, and local AI support."
    ),
    lifespan=lifespan,
)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def complete_turn(
    conversation_id: str,
    answer: str,
    source: str,
    sources: list[Source],
) -> ChatResponse:
    """
    Saves the assistant response and returns the API response.

    Time Complexity:
    - Source serialization: O(s)
    - Database write: effectively O(log n)
    """
    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
        source=source,
        sources=sources,
    )

    return ChatResponse(
        answer=answer,
        source=source,
        sources=sources,
    )


@app.get("/")
def home():
    """
    Health-check endpoint.

    Time Complexity:
    - O(1)
    """
    return {
        "message": "Intellectual Assistant API is running",
        "version": "0.6.0",
    }


@app.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[ConversationMessage],
)
def restore_conversation(
    conversation_id: str,
):
    """
    Restores a conversation after page refresh.

    Time Complexity:
    - O(log n + m), where m is at most 100 messages.
    """
    return get_conversation_messages(
        conversation_id=conversation_id,
        limit=100,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main assistant pipeline.

    Flow:
    1. Load persistent recent memory from SQLite.
    2. Save the user's current message.
    3. Handle casual conversation locally.
    4. Resolve references such as "he", "his age", and prior topics.
    5. Search the local knowledge base.
    6. Search the web only when needed.
    7. Generate and save the final answer.

    Time Complexity:
    - Memory retrieval: O(log n + h), h capped at 12
    - Conversation check: O(l)
    - Knowledge lookup: O(n × k)
    - Search result processing: O(r)
    - LLM generation: depends on model and hardware
    """
    history = get_recent_history(
        conversation_id=request.conversation_id,
        limit=12,
    )

    save_message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.message,
        source="user",
    )

    conversation_answer = get_conversation_response(request.message)

    if conversation_answer:
        return complete_turn(
            conversation_id=request.conversation_id,
            answer=conversation_answer,
            source="conversation",
            sources=[],
        )

    resolution = resolve_contextual_message(
        message=request.message,
        history=history,
    )

    if resolution.direct_answer:
        return complete_turn(
            conversation_id=request.conversation_id,
            answer=resolution.direct_answer,
            source="memory_resolution",
            sources=[],
        )

    effective_message = resolution.rewritten_message

    knowledge_answer = search_knowledge(effective_message)

    if knowledge_answer:
        return complete_turn(
            conversation_id=request.conversation_id,
            answer=knowledge_answer,
            source="knowledge_base",
            sources=[],
        )

    search_query = build_search_query(
        message=effective_message,
        history=history,
    )

    search_results = search_web(search_query)

    context = "\n\n".join(
        (
            f"Source: {result.get('title', 'Untitled Source')}\n"
            f"Content: {result.get('snippet', '')}"
        )
        for result in search_results
    )

    answer = generate_response(
        user_message=effective_message,
        context=context,
        history=history,
    )

    sources = [
        Source(
            title=result.get("title", "Untitled Source"),
            url=result.get("url", ""),
        )
        for result in search_results
    ]

    return complete_turn(
        conversation_id=request.conversation_id,
        answer=answer,
        source="web_search_fallback",
        sources=sources,
    )