"""
Telegram API Wrapper with Timeout and Retry Handling
=====================================================

Provides robust API calls with automatic retry, timeout handling,
and rate limiting.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import aiohttp
from enum import Enum


class TelegramError(Exception):
    """Базовая ошибка Telegram API"""
    pass


class TelegramTimeoutError(TelegramError):
    """Ошибка таймаута"""
    pass


class TelegramRateLimitError(TelegramError):
    """Ошибка превышения лимита запросов"""
    
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class TelegramAPIWrapper:
    """
    Обертка для Telegram Bot API с обработкой таймаутов и повторами.
    
    Example:
        >>> api = TelegramAPIWrapper(token="YOUR_TOKEN")
        >>> result = await api.send_message(
        ...     chat_id=123456,
        ...     text="Hello!",
        ...     max_retries=3
        ... )
    """
    
    def __init__(
        self,
        token: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Инициализация API обертки.
        
        Args:
            token: Токен бота
            timeout: Таймаут запросов в секундах
            max_retries: Максимальное количество повторов
            retry_delay: Задержка между повторами в секундах
        """
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.logger = logging.getLogger("TelegramAPI")
        
        # Rate limiting
        self.last_request_time: Dict[str, datetime] = {}
        self.min_request_interval = 0.033  # ~30 requests per second
    
    async def _wait_for_rate_limit(self, method: str):
        """Ожидание для соблюдения rate limit"""
        if method in self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time[method]).total_seconds()
            if elapsed < self.min_request_interval:
                await asyncio.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time[method] = datetime.now()
    
    async def _make_request(
        self,
        method: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Выполнить запрос к API с обработкой ошибок.
        
        Args:
            method: Метод API
            data: Данные для отправки
            files: Файлы для отправки
            timeout: Таймаут (переопределяет значение по умолчанию)
        
        Returns:
            Ответ от API
        
        Raises:
            TelegramTimeoutError: При таймауте
            TelegramRateLimitError: При превышении лимита
            TelegramError: При других ошибках
        """
        url = f"{self.api_url}/{method}"
        request_timeout = timeout or self.timeout
        
        # Соблюдаем rate limit
        await self._wait_for_rate_limit(method)
        
        for attempt in range(self.max_retries):
            try:
                timeout_config = aiohttp.ClientTimeout(total=request_timeout)
                
                async with aiohttp.ClientSession(timeout=timeout_config) as session:
                    if files:
                        # Multipart для файлов
                        form_data = aiohttp.FormData()
                        if data:
                            for key, value in data.items():
                                form_data.add_field(key, str(value))
                        for key, file in files.items():
                            form_data.add_field(key, file)
                        
                        async with session.post(url, data=form_data) as resp:
                            result = await resp.json()
                    else:
                        # JSON для обычных запросов
                        async with session.post(url, json=data) as resp:
                            result = await resp.json()
                
                # Проверяем ответ
                if not result.get("ok"):
                    error_code = result.get("error_code")
                    description = result.get("description", "Unknown error")
                    
                    # Обработка rate limit
                    if error_code == 429:
                        retry_after = result.get("parameters", {}).get("retry_after", 60)
                        self.logger.warning(f"Rate limit hit. Retry after {retry_after}s")
                        
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            raise TelegramRateLimitError(retry_after)
                    
                    # Другие ошибки
                    self.logger.error(f"Telegram API error: {description}")
                    raise TelegramError(f"API Error: {description}")
                
                return result
            
            except asyncio.TimeoutError:
                self.logger.warning(
                    f"Timeout on attempt {attempt + 1}/{self.max_retries} for {method}"
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise TelegramTimeoutError(f"Request timed out after {self.max_retries} attempts")
            
            except aiohttp.ClientError as e:
                self.logger.error(f"Network error on attempt {attempt + 1}: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise TelegramError(f"Network error: {str(e)}")
            
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}", exc_info=True)
                raise TelegramError(f"Unexpected error: {str(e)}")
        
        raise TelegramError("Max retries exceeded")
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Dict] = None,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Отправить сообщение"""
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        
        if reply_markup:
            import json
            data["reply_markup"] = json.dumps(reply_markup)
        
        data.update(kwargs)
        
        return await self._make_request("sendMessage", data)
    
    async def send_photo(
        self,
        chat_id: int,
        photo: str,
        caption: Optional[str] = None,
        reply_markup: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Отправить фото"""
        data = {
            "chat_id": chat_id,
            "photo": photo,
        }
        
        if caption:
            data["caption"] = caption
        
        if reply_markup:
            import json
            data["reply_markup"] = json.dumps(reply_markup)
        
        data.update(kwargs)
        
        return await self._make_request("sendPhoto", data)
    
    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Optional[Dict] = None,
        parse_mode: str = "HTML",
        **kwargs
    ) -> Dict[str, Any]:
        """Редактировать сообщение"""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        
        if reply_markup:
            import json
            data["reply_markup"] = json.dumps(reply_markup)
        
        data.update(kwargs)
        
        return await self._make_request("editMessageText", data)
    
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Ответить на callback query"""
        data = {
            "callback_query_id": callback_query_id,
        }
        
        if text:
            data["text"] = text
        if show_alert:
            data["show_alert"] = show_alert
        
        data.update(kwargs)
        
        return await self._make_request("answerCallbackQuery", data)
    
    async def delete_message(
        self,
        chat_id: int,
        message_id: int
    ) -> Dict[str, Any]:
        """Удалить сообщение"""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
        }
        
        return await self._make_request("deleteMessage", data)
    
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 30,
        allowed_updates: Optional[List[str]] = None
    ) -> List[Dict]:
        """Получить обновления (long polling)"""
        data = {
            "limit": limit,
            "timeout": timeout,
        }
        
        if offset:
            data["offset"] = offset
        
        if allowed_updates:
            data["allowed_updates"] = allowed_updates
        
        result = await self._make_request("getUpdates", data, timeout=timeout + 5)
        return result.get("result", [])
    
    async def get_me(self) -> Dict[str, Any]:
        """Получить информацию о боте"""
        result = await self._make_request("getMe")
        return result.get("result", {})
