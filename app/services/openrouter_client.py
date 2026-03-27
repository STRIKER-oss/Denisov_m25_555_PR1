import httpx
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    """Клиент для взаимодействия с OpenRouter API."""
    
    def __init__(self) -> None:
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        if settings.OPENROUTER_SITE_URL:
            self.headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            self.headers["X-Title"] = settings.OPENROUTER_APP_NAME
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        payload = {
            "model": model or settings.OPENROUTER_MODEL,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    await self._handle_error(response)
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                if not content:
                    raise ExternalServiceError("Пустой ответ от OpenRouter")
                
                return content
                
            except httpx.TimeoutException:
                raise ExternalServiceError("Таймаут")
            except httpx.RequestError:
                raise ExternalServiceError("Не удалось подключиться к OpenRouter")
    
    async def _handle_error(self, response: httpx.Response) -> None:
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Неизвестная ошибка")
        except Exception:
            error_message = response.text[:500]
        
        if response.status_code == 401:
            error_msg = "Неверный API ключ"
        elif response.status_code == 429:
            error_msg = "Превышен лимит запросов"
        else:
            error_msg = f"Ошибка  (HTTP {response.status_code}): {error_message}"
        
        raise ExternalServiceError(error_msg, status_code=response.status_code)


openrouter_client = OpenRouterClient()
