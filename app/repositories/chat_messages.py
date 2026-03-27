from typing import List
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ChatMessage


class ChatMessageRepository:
    """Операции с сообщениями чата."""
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def add_message(self, user_id: int, role: str, content: str) -> ChatMessage:
        message = ChatMessage(user_id=user_id, role=role, content=content)
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return message
    
    async def get_last_n_messages(self, user_id: int, n: int, include_system: bool = True) -> List[ChatMessage]:
        if n <= 0:
            return []
        
        n = min(n, 100)
        query = select(ChatMessage).where(ChatMessage.user_id == user_id)
        
        if not include_system:
            query = query.where(ChatMessage.role != "system")
        
        query = query.order_by(desc(ChatMessage.created_at)).limit(n)
        result = await self._session.execute(query)
        messages = list(result.scalars().all())
        messages.reverse()
        return messages
    
    async def get_conversation_context(self, user_id: int, max_messages: int = 10, include_system: bool = True) -> List[ChatMessage]:
        return await self.get_last_n_messages(user_id, max_messages, include_system)
    
    async def get_user_messages(self, user_id: int, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        query = select(ChatMessage).where(ChatMessage.user_id == user_id).order_by(ChatMessage.created_at)
        if offset > 0:
            query = query.offset(offset)
        if limit > 0:
            query = query.limit(limit)
        result = await self._session.execute(query)
        return list(result.scalars().all())
    
    async def delete_user_messages(self, user_id: int) -> int:
        query = delete(ChatMessage).where(ChatMessage.user_id == user_id)
        result = await self._session.execute(query)
        await self._session.flush()
        return result.rowcount
