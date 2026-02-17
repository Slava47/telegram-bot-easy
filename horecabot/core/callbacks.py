"""
Callback Query Router
=====================

Advanced routing system for inline button callbacks with pattern matching,
middleware support, and automatic error handling.
"""

import re
import logging
from typing import Dict, List, Callable, Optional, Any, Pattern
from dataclasses import dataclass
from enum import Enum


class CallbackAction(Enum):
    """Типы действий callback кнопок"""
    VIEW = "view"
    ADD = "add"
    REMOVE = "remove"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    NAVIGATE = "navigate"
    FILTER = "filter"


@dataclass
class CallbackData:
    """
    Структурированные данные callback.
    
    Attributes:
        action: Действие
        entity: Сущность (menu, order, booking и т.д.)
        id: ID объекта
        params: Дополнительные параметры
    """
    action: str
    entity: str
    id: Optional[str] = None
    params: Dict[str, str] = None
    
    @classmethod
    def parse(cls, callback_string: str) -> 'CallbackData':
        """
        Разобрать строку callback в структурированные данные.
        
        Формат: action:entity:id:param1=value1,param2=value2
        Примеры:
        - view:menu:main
        - add:cart:item_123:quantity=2
        - confirm:order:order_456
        
        Args:
            callback_string: Строка callback
        
        Returns:
            CallbackData объект
        """
        parts = callback_string.split(':')
        
        if len(parts) < 2:
            raise ValueError(f"Invalid callback format: {callback_string}")
        
        action = parts[0]
        entity = parts[1]
        item_id = parts[2] if len(parts) > 2 else None
        
        # Парсинг параметров
        params = {}
        if len(parts) > 3:
            param_str = parts[3]
            for param in param_str.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        
        return cls(
            action=action,
            entity=entity,
            id=item_id,
            params=params
        )
    
    def build(self) -> str:
        """
        Собрать callback строку из данных.
        
        Returns:
            Callback строка
        """
        parts = [self.action, self.entity]
        
        if self.id:
            parts.append(self.id)
        
        if self.params:
            param_str = ','.join(f"{k}={v}" for k, v in self.params.items())
            parts.append(param_str)
        
        return ':'.join(parts)


class CallbackRouter:
    """
    Роутер для callback запросов.
    
    Поддерживает:
    - Точное совпадение
    - Паттерны с регулярными выражениями
    - Middleware
    - Автоматическую обработку ошибок
    
    Example:
        >>> router = CallbackRouter()
        >>> 
        >>> @router.callback("view:menu:*")
        >>> async def view_menu_category(update, callback_data):
        ...     category_id = callback_data.id
        ...     # Handle menu view
        >>> 
        >>> @router.callback_pattern(r"add:cart:item_(\d+)")
        >>> async def add_to_cart(update, match):
        ...     item_id = match.group(1)
        ...     # Handle add to cart
    """
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}  # Exact match handlers
        self.pattern_handlers: List[tuple[Pattern, Callable]] = []  # Pattern handlers
        self.middleware: List[Callable] = []
        self.error_handler: Optional[Callable] = None
        
        self.logger = logging.getLogger("CallbackRouter")
    
    def callback(self, callback_pattern: str):
        """
        Декоратор для регистрации обработчика callback.
        
        Поддерживает подстановочные знаки (*).
        
        Args:
            callback_pattern: Паттерн callback (например, "view:menu:*")
        
        Example:
            >>> @router.callback("view:menu:*")
            >>> async def view_menu(update, callback_data):
            ...     pass
        """
        def decorator(func: Callable):
            # Проверяем, есть ли подстановочные знаки
            if '*' in callback_pattern:
                # Преобразуем в regex паттерн
                regex_pattern = callback_pattern.replace('*', '.*')
                regex = re.compile(f'^{regex_pattern}$')
                self.pattern_handlers.append((regex, func))
            else:
                # Точное совпадение
                self.handlers[callback_pattern] = func
            
            self.logger.debug(f"Registered callback handler for: {callback_pattern}")
            return func
        return decorator
    
    def callback_pattern(self, regex_pattern: str):
        """
        Декоратор для регистрации обработчика с regex паттерном.
        
        Args:
            regex_pattern: Регулярное выражение
        
        Example:
            >>> @router.callback_pattern(r"add:cart:item_(\d+)")
            >>> async def add_to_cart(update, match):
            ...     item_id = match.group(1)
        """
        def decorator(func: Callable):
            regex = re.compile(regex_pattern)
            self.pattern_handlers.append((regex, func))
            self.logger.debug(f"Registered pattern handler: {regex_pattern}")
            return func
        return decorator
    
    def use_middleware(self, middleware_func: Callable):
        """
        Добавить middleware для предобработки.
        
        Middleware выполняется перед обработчиком и может:
        - Модифицировать update
        - Прерывать обработку (вернув False)
        - Добавлять данные в контекст
        
        Args:
            middleware_func: Функция middleware
        
        Example:
            >>> @router.use_middleware
            >>> async def auth_middleware(update, context):
            ...     user_id = update['callback_query']['from']['id']
            ...     if not is_authorized(user_id):
            ...         return False  # Прервать обработку
            ...     context['user'] = get_user(user_id)
            ...     return True
        """
        self.middleware.append(middleware_func)
        return middleware_func
    
    def on_error(self, error_handler_func: Callable):
        """
        Установить обработчик ошибок.
        
        Args:
            error_handler_func: Функция обработки ошибок
        
        Example:
            >>> @router.on_error
            >>> async def handle_error(update, error):
            ...     logger.error(f"Callback error: {error}")
            ...     await bot.answer_callback_query(
            ...         update['callback_query']['id'],
            ...         text="Произошла ошибка",
            ...         show_alert=True
            ...     )
        """
        self.error_handler = error_handler_func
        return error_handler_func
    
    async def route(self, update: Dict[str, Any], bot: Any) -> bool:
        """
        Маршрутизировать callback запрос.
        
        Args:
            update: Update от Telegram
            bot: Экземпляр бота
        
        Returns:
            True если обработан, False иначе
        """
        if 'callback_query' not in update:
            return False
        
        callback_query = update['callback_query']
        callback_data_str = callback_query.get('data')
        
        if not callback_data_str:
            return False
        
        # Контекст для middleware
        context = {}
        
        try:
            # Выполняем middleware
            for middleware_func in self.middleware:
                result = await middleware_func(update, context)
                if result is False:
                    # Middleware прервал обработку
                    return True
            
            # Поиск обработчика с точным совпадением
            if callback_data_str in self.handlers:
                handler = self.handlers[callback_data_str]
                
                # Парсим callback данные
                try:
                    callback_data = CallbackData.parse(callback_data_str)
                except Exception:
                    callback_data = None
                
                await handler(update, callback_data)
                return True
            
            # Поиск по паттернам
            for pattern, handler in self.pattern_handlers:
                match = pattern.match(callback_data_str)
                if match:
                    await handler(update, match)
                    return True
            
            # Обработчик не найден
            self.logger.warning(f"No handler found for callback: {callback_data_str}")
            return False
        
        except Exception as e:
            self.logger.error(f"Error handling callback: {e}", exc_info=True)
            
            # Вызываем обработчик ошибок
            if self.error_handler:
                try:
                    await self.error_handler(update, e)
                except Exception as handler_error:
                    self.logger.error(
                        f"Error in error handler: {handler_error}",
                        exc_info=True
                    )
            
            return True


class CallbackBuilder:
    """
    Помощник для создания callback данных.
    
    Example:
        >>> builder = CallbackBuilder()
        >>> 
        >>> # Простой callback
        >>> callback = builder.build("view", "menu", "main")
        >>> # Результат: "view:menu:main"
        >>> 
        >>> # С параметрами
        >>> callback = builder.build(
        ...     "add", "cart", "item_123",
        ...     quantity=2, modifier="large"
        ... )
        >>> # Результат: "add:cart:item_123:quantity=2,modifier=large"
    """
    
    @staticmethod
    def build(action: str, entity: str, item_id: Optional[str] = None, **params) -> str:
        """
        Построить callback строку.
        
        Args:
            action: Действие
            entity: Сущность
            item_id: ID объекта
            **params: Дополнительные параметры
        
        Returns:
            Callback строка
        """
        callback_data = CallbackData(
            action=action,
            entity=entity,
            id=item_id,
            params=params if params else None
        )
        return callback_data.build()
    
    @staticmethod
    def build_pagination(entity: str, page: int, total_pages: int) -> List[Dict[str, str]]:
        """
        Построить кнопки пагинации.
        
        Args:
            entity: Сущность для пагинации
            page: Текущая страница
            total_pages: Всего страниц
        
        Returns:
            Список кнопок для inline клавиатуры
        """
        buttons = []
        
        # Предыдущая страница
        if page > 1:
            buttons.append({
                "text": "◀️ Назад",
                "callback_data": CallbackBuilder.build(
                    "navigate", entity, page=str(page - 1)
                )
            })
        
        # Текущая страница
        buttons.append({
            "text": f"• {page}/{total_pages} •",
            "callback_data": "ignore"
        })
        
        # Следующая страница
        if page < total_pages:
            buttons.append({
                "text": "Вперед ▶️",
                "callback_data": CallbackBuilder.build(
                    "navigate", entity, page=str(page + 1)
                )
            })
        
        return buttons
    
    @staticmethod
    def build_confirmation(action: str, entity: str, item_id: str) -> List[List[Dict[str, str]]]:
        """
        Построить кнопки подтверждения действия.
        
        Args:
            action: Действие для подтверждения
            entity: Сущность
            item_id: ID объекта
        
        Returns:
            Кнопки для inline клавиатуры
        """
        return [
            [
                {
                    "text": "✅ Подтвердить",
                    "callback_data": CallbackBuilder.build(
                        "confirm", entity, item_id, action=action
                    )
                },
                {
                    "text": "❌ Отмена",
                    "callback_data": CallbackBuilder.build(
                        "cancel", entity, item_id, action=action
                    )
                }
            ]
        ]
