"""
User State Management System
=============================

Manages user states for conversation flows, multi-step processes,
and context-aware interactions.
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field


class UserState(Enum):
    """Базовые состояния пользователя"""
    IDLE = "idle"
    
    # Состояния меню и заказов
    BROWSING_MENU = "browsing_menu"
    VIEWING_ITEM = "viewing_item"
    ADDING_TO_CART = "adding_to_cart"
    IN_CART = "in_cart"
    CHECKOUT = "checkout"
    ENTERING_ADDRESS = "entering_address"
    ENTERING_PHONE = "entering_phone"
    CONFIRMING_ORDER = "confirming_order"
    
    # Состояния бронирования
    BOOKING_START = "booking_start"
    SELECTING_DATE = "selecting_date"
    SELECTING_TIME = "selecting_time"
    ENTERING_GUESTS_COUNT = "entering_guests_count"
    ENTERING_BOOKING_NAME = "entering_booking_name"
    ENTERING_BOOKING_PHONE = "entering_booking_phone"
    ENTERING_SPECIAL_REQUESTS = "entering_special_requests"
    CONFIRMING_BOOKING = "confirming_booking"
    
    # Состояния квиза
    IN_QUIZ = "in_quiz"
    QUIZ_COMPLETE = "quiz_complete"
    
    # Состояния регистрации
    REGISTRATION_START = "registration_start"
    ENTERING_NAME = "entering_name"
    ENTERING_EMAIL = "entering_email"
    ENTERING_PHONE_REG = "entering_phone_reg"
    
    # Состояния обратной связи
    LEAVING_REVIEW = "leaving_review"
    ENTERING_RATING = "entering_rating"
    ENTERING_REVIEW_TEXT = "entering_review_text"


@dataclass
class StateContext:
    """
    Контекст состояния пользователя.
    
    Хранит временные данные, связанные с текущим состоянием.
    """
    state: UserState
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    previous_state: Optional[UserState] = None
    
    def set_data(self, key: str, value: Any):
        """Установить данные в контексте"""
        self.data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Получить данные из контекста"""
        return self.data.get(key, default)
    
    def clear_data(self):
        """Очистить все данные контекста"""
        self.data.clear()
    
    def is_expired(self) -> bool:
        """Проверить, истек ли срок действия контекста"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class StateManager:
    """
    Менеджер состояний пользователей.
    
    Управляет состояниями всех пользователей бота,
    обрабатывает переходы между состояниями и хранит контекст.
    
    Example:
        >>> state_manager = StateManager()
        >>> 
        >>> # Установить состояние
        >>> state_manager.set_state(
        ...     user_id=123,
        ...     state=UserState.BROWSING_MENU
        ... )
        >>> 
        >>> # Сохранить данные в контексте
        >>> state_manager.update_context(
        ...     user_id=123,
        ...     category="main_dishes"
        ... )
        >>> 
        >>> # Получить текущее состояние
        >>> state = state_manager.get_state(123)
        >>> print(state)  # UserState.BROWSING_MENU
    """
    
    def __init__(self, default_timeout: int = 1800):
        """
        Инициализация менеджера состояний.
        
        Args:
            default_timeout: Таймаут по умолчанию в секундах (30 минут)
        """
        self.contexts: Dict[int, StateContext] = {}
        self.default_timeout = default_timeout
        
        # Обработчики переходов состояний
        self.transition_handlers: Dict[UserState, Callable] = {}
    
    def set_state(
        self,
        user_id: int,
        state: UserState,
        timeout: Optional[int] = None,
        **context_data
    ):
        """
        Установить состояние пользователя.
        
        Args:
            user_id: ID пользователя
            state: Новое состояние
            timeout: Таймаут в секундах (опционально)
            **context_data: Данные контекста
        """
        # Получаем предыдущее состояние
        previous_state = None
        if user_id in self.contexts:
            previous_state = self.contexts[user_id].state
        
        # Вычисляем время истечения
        expires_at = None
        if timeout is not None:
            expires_at = datetime.now() + timedelta(seconds=timeout)
        elif self.default_timeout > 0:
            expires_at = datetime.now() + timedelta(seconds=self.default_timeout)
        
        # Создаем новый контекст
        context = StateContext(
            state=state,
            data=context_data,
            expires_at=expires_at,
            previous_state=previous_state
        )
        
        self.contexts[user_id] = context
        
        # Вызываем обработчик перехода, если есть
        if state in self.transition_handlers:
            self.transition_handlers[state](user_id, context)
    
    def get_state(self, user_id: int) -> UserState:
        """
        Получить текущее состояние пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Текущее состояние или IDLE если не установлено
        """
        if user_id not in self.contexts:
            return UserState.IDLE
        
        context = self.contexts[user_id]
        
        # Проверяем истечение срока
        if context.is_expired():
            self.reset_state(user_id)
            return UserState.IDLE
        
        return context.state
    
    def get_context(self, user_id: int) -> Optional[StateContext]:
        """
        Получить контекст состояния пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            StateContext или None
        """
        if user_id not in self.contexts:
            return None
        
        context = self.contexts[user_id]
        
        # Проверяем истечение срока
        if context.is_expired():
            self.reset_state(user_id)
            return None
        
        return context
    
    def update_context(self, user_id: int, **data):
        """
        Обновить данные контекста пользователя.
        
        Args:
            user_id: ID пользователя
            **data: Данные для обновления
        """
        if user_id in self.contexts:
            for key, value in data.items():
                self.contexts[user_id].set_data(key, value)
    
    def reset_state(self, user_id: int):
        """
        Сбросить состояние пользователя в IDLE.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self.contexts:
            del self.contexts[user_id]
    
    def go_back(self, user_id: int) -> bool:
        """
        Вернуться к предыдущему состоянию.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если возврат успешен, False иначе
        """
        if user_id not in self.contexts:
            return False
        
        context = self.contexts[user_id]
        if context.previous_state is None:
            return False
        
        self.set_state(user_id, context.previous_state)
        return True
    
    def register_transition_handler(
        self,
        state: UserState,
        handler: Callable[[int, StateContext], None]
    ):
        """
        Зарегистрировать обработчик перехода в состояние.
        
        Args:
            state: Состояние
            handler: Функция-обработчик
        """
        self.transition_handlers[state] = handler
    
    def cleanup_expired(self):
        """Очистить истекшие контексты"""
        expired_users = [
            user_id for user_id, context in self.contexts.items()
            if context.is_expired()
        ]
        
        for user_id in expired_users:
            del self.contexts[user_id]
    
    def get_users_in_state(self, state: UserState) -> list[int]:
        """
        Получить список пользователей в определенном состоянии.
        
        Args:
            state: Состояние
        
        Returns:
            Список user_id
        """
        return [
            user_id for user_id, context in self.contexts.items()
            if context.state == state and not context.is_expired()
        ]
