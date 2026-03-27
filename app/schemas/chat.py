from typing import Optional
from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    """Запрос к LLM"""
    
    prompt: str = Field(..., min_length=1, max_length=10000, description="Текст запроса", example="Самая популярная игра в мире?")
    system: Optional[str] = Field(default=None, max_length=2000, description="Системная инструкция", example="Ты полезный ассистент")
    max_history: int = Field(default=10, ge=0, le=50, description="Количество предыдущих сообщений")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Ответы (0.0 - точно, 2.0 - неточно)")
    
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Запрос не может быть пустым")
        return v


class ChatResponse(BaseModel):
    
    answer: str = Field(..., description="Сгенерированный ответ")


class ChatMessageHistory(BaseModel):
    
    role: str = Field(..., description="Роль отправителя (user, assistant, system)")
    content: str = Field(..., description="Текст сообщения")
    created_at: str = Field(..., description="Время создания")


class ConversationHistoryResponse(BaseModel):
    
    messages: list[ChatMessageHistory] = Field(..., description="Список сообщений")
    total: int = Field(..., description="Общее количество сообщений")
