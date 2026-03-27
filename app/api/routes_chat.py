from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_chat_usecases, get_current_user_id, get_db_session
from app.core.errors import ExternalServiceError
from app.schemas.chat import ChatRequest, ChatResponse, ConversationHistoryResponse, ChatMessageHistory
from app.usecases.chat import ChatUseCases


router = APIRouter(tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_usecases: ChatUseCases = Depends(get_chat_usecases),
    db: AsyncSession = Depends(get_db_session)
) -> ChatResponse:

    try:
        answer = await chat_usecases.ask(
            user_id=user_id,
            prompt=request.prompt,
            system=request.system,
            max_history=request.max_history,
            temperature=request.temperature
        )
        await db.commit()
        return ChatResponse(answer=answer)
    except ExternalServiceError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_history(
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    chat_usecases: ChatUseCases = Depends(get_chat_usecases),
    db: AsyncSession = Depends(get_db_session)
) -> ConversationHistoryResponse:

    messages = await chat_usecases.get_conversation_history(user_id=user_id, limit=limit, offset=offset)
    history = [
        ChatMessageHistory(role=m["role"], content=m["content"], created_at=m["created_at"])
        for m in messages
    ]
    return ConversationHistoryResponse(messages=history, total=len(history))


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    user_id: int = Depends(get_current_user_id),
    chat_usecases: ChatUseCases = Depends(get_chat_usecases),
    db: AsyncSession = Depends(get_db_session)
) -> None:

    try:
        await chat_usecases.clear_history(user_id=user_id)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
