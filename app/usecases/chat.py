from typing import List, Dict, Optional
from app.core.errors import ExternalServiceError
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient

class ChatUseCases:
    """Работа с чатом."""
    
    def __init__(self, chat_repository: ChatMessageRepository, openrouter_client: OpenRouterClient) -> None:
        self._chat_repo = chat_repository
        self._openrouter_client = openrouter_client
    
    async def ask(
        self,
        user_id: int,
        prompt: str,
        system: Optional[str] = None,
        max_history: int = 10,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:

        await self._chat_repo.add_message(user_id=user_id, role="user", content=prompt)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        history = await self._chat_repo.get_conversation_context(user_id=user_id, max_messages=max_history)
        for msg in history:
            if msg.role == "system" and system:
                continue
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self._openrouter_client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature
            )
        except ExternalServiceError:
            raise
        

        await self._chat_repo.add_message(user_id=user_id, role="assistant", content=response)
        return response
    
    async def clear_history(self, user_id: int) -> int:
        return await self._chat_repo.delete_user_messages(user_id)
    
    async def get_conversation_history(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, str]]:
        messages = await self._chat_repo.get_user_messages(user_id=user_id, limit=limit, offset=offset)
        return [
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in messages
        ]
