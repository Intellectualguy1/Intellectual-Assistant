from typing import Literal

from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    """
    A message used internally as recent conversation context.
    """

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class Source(BaseModel):
    title: str
    url: str


class ConversationMessage(BaseModel):
    """
    A saved message returned when restoring a conversation.
    """

    role: Literal["user", "assistant"]
    content: str
    source: str
    sources: list[Source] = Field(default_factory=list)
    created_at: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str = Field(min_length=8, max_length=100)


class ChatResponse(BaseModel):
    answer: str
    source: str
    sources: list[Source] = Field(default_factory=list)