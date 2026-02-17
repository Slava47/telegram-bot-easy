"""
Модуль карточки гостя и системы лояльности
===========================================

Персонализация опыта гостя и программы лояльности.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LoyaltyType(Enum):
    """Типы программ лояльности"""
    POINTS = "points"  # Накопительная балльная система
    STAMPS = "stamps"  # Система штампов (6-й кофе бесплатно)
    LEVELS = "levels"  # Уровневая система с привилегиями


@dataclass
class GuestCard:
    """
    Карточка гостя.
    
    Хранит всю персональную информацию и историю взаимодействия
    с заведением.
    
    Attributes:
        user_id: ID пользователя Telegram
        name: Имя гостя
        phone: Номер телефона (опционально)
        email: Email (опционально)
        created_at: Дата регистрации
        loyalty_points: Накопленные баллы лояльности
        loyalty_level: Уровень в программе лояльности
        stamps: Количество штампов (для STAMPS программы)
        total_orders: Общее количество заказов
        total_spent: Общая сумма потраченных средств
        favorite_items: Любимые блюда/напитки
        quiz_completions: Количество пройденных квизов
        reviews_count: Количество оставленных отзывов
        average_rating: Средний рейтинг, который ставит гость
        last_visit: Дата последнего визита/заказа
        preferences: Предпочтения гостя (теги из квизов и заказов)
    """
    user_id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Лояльность
    loyalty_points: int = 0
    loyalty_level: str = "bronze"  # bronze, silver, gold, platinum
    stamps: int = 0
    
    # Статистика
    total_orders: int = 0
    total_spent: float = 0.0
    favorite_items: List[str] = field(default_factory=list)  # item_ids
    quiz_completions: int = 0
    reviews_count: int = 0
    average_rating: float = 0.0
    last_visit: Optional[datetime] = None
    
    # Предпочтения
    preferences: List[str] = field(default_factory=list)  # теги
    
    def add_order(self, order_amount: float, items: List[str]):
        """
        Добавить информацию о заказе.
        
        Args:
            order_amount: Сумма заказа
            items: Список ID позиций в заказе
        """
        self.total_orders += 1
        self.total_spent += order_amount
        self.last_visit = datetime.now()
        
        # Обновляем любимые блюда
        for item_id in items:
            if item_id not in self.favorite_items:
                self.favorite_items.append(item_id)
    
    def add_points(self, points: int):
        """Добавить баллы лояльности"""
        self.loyalty_points += points
    
    def spend_points(self, points: int) -> bool:
        """
        Потратить баллы лояльности.
        
        Args:
            points: Количество баллов
        
        Returns:
            True если баллов хватает, False иначе
        """
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            return True
        return False
    
    def add_stamp(self):
        """Добавить штамп"""
        self.stamps += 1
    
    def use_stamps(self, count: int = 1) -> bool:
        """
        Использовать штампы.
        
        Args:
            count: Количество штампов
        
        Returns:
            True если штампов хватает, False иначе
        """
        if self.stamps >= count:
            self.stamps -= count
            return True
        return False
    
    def update_level(self):
        """Обновить уровень лояльности на основе потраченной суммы"""
        if self.total_spent >= 100000:
            self.loyalty_level = "platinum"
        elif self.total_spent >= 50000:
            self.loyalty_level = "gold"
        elif self.total_spent >= 20000:
            self.loyalty_level = "silver"
        else:
            self.loyalty_level = "bronze"
    
    def add_quiz_completion(self, tags: List[str]):
        """
        Добавить завершенный квиз.
        
        Args:
            tags: Теги из ответов квиза (для обновления предпочтений)
        """
        self.quiz_completions += 1
        
        # Обновляем предпочтения
        for tag in tags:
            if tag not in self.preferences:
                self.preferences.append(tag)
    
    def add_review(self, rating: float):
        """
        Добавить отзыв.
        
        Args:
            rating: Оценка (1-5)
        """
        # Обновляем средний рейтинг
        total = self.average_rating * self.reviews_count + rating
        self.reviews_count += 1
        self.average_rating = total / self.reviews_count


class LoyaltyModule:
    """
    Модуль системы лояльности.
    
    Управление карточками гостей и программами лояльности.
    
    Example:
        >>> loyalty = LoyaltyModule(loyalty_type=LoyaltyType.POINTS)
        >>> 
        >>> # Регистрация гостя
        >>> card = loyalty.create_guest_card(
        ...     user_id=123456,
        ...     name="Иван Иванов",
        ...     phone="+79991234567"
        ... )
        >>> 
        >>> # Начисление баллов за заказ
        >>> loyalty.process_order(
        ...     user_id=123456,
        ...     order_amount=1500.0,
        ...     item_ids=["item_1", "item_2"]
        ... )
    """
    
    def __init__(
        self,
        loyalty_type: LoyaltyType = LoyaltyType.POINTS,
        points_per_ruble: float = 0.05,  # 5% кэшбэк баллами
        stamps_for_reward: int = 6  # Каждый 6-й бесплатно
    ):
        """
        Инициализация модуля лояльности.
        
        Args:
            loyalty_type: Тип программы лояльности
            points_per_ruble: Сколько баллов за 1 рубль (для POINTS)
            stamps_for_reward: Сколько штампов для награды (для STAMPS)
        """
        self.loyalty_type = loyalty_type
        self.points_per_ruble = points_per_ruble
        self.stamps_for_reward = stamps_for_reward
        
        self.guest_cards: Dict[int, GuestCard] = {}  # user_id -> GuestCard
    
    def create_guest_card(
        self,
        user_id: int,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> GuestCard:
        """
        Создать карточку гостя.
        
        Args:
            user_id: ID пользователя Telegram
            name: Имя гостя
            phone: Номер телефона (опционально)
            email: Email (опционально)
        
        Returns:
            Объект GuestCard
        """
        card = GuestCard(
            user_id=user_id,
            name=name,
            phone=phone,
            email=email
        )
        self.guest_cards[user_id] = card
        return card
    
    def get_guest_card(self, user_id: int) -> Optional[GuestCard]:
        """Получить карточку гостя"""
        return self.guest_cards.get(user_id)
    
    def process_order(
        self,
        user_id: int,
        order_amount: float,
        item_ids: List[str]
    ):
        """
        Обработать заказ: начислить баллы/штампы, обновить статистику.
        
        Args:
            user_id: ID пользователя
            order_amount: Сумма заказа
            item_ids: Список ID позиций в заказе
        """
        card = self.guest_cards.get(user_id)
        if not card:
            return
        
        # Обновляем статистику заказа
        card.add_order(order_amount, item_ids)
        
        # Начисляем бонусы
        if self.loyalty_type == LoyaltyType.POINTS:
            points = int(order_amount * self.points_per_ruble)
            card.add_points(points)
        
        elif self.loyalty_type == LoyaltyType.STAMPS:
            card.add_stamp()
        
        # Обновляем уровень (для LEVELS)
        if self.loyalty_type == LoyaltyType.LEVELS:
            card.update_level()
    
    def check_reward_available(self, user_id: int) -> bool:
        """
        Проверить, доступна ли награда.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если награда доступна
        """
        card = self.guest_cards.get(user_id)
        if not card:
            return False
        
        if self.loyalty_type == LoyaltyType.STAMPS:
            return card.stamps >= self.stamps_for_reward
        
        return False
    
    def claim_reward(self, user_id: int) -> bool:
        """
        Получить награду (использовать штампы/баллы).
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если награда успешно получена
        """
        card = self.guest_cards.get(user_id)
        if not card:
            return False
        
        if self.loyalty_type == LoyaltyType.STAMPS:
            return card.use_stamps(self.stamps_for_reward)
        
        return False
    
    def get_all_guests(self) -> List[GuestCard]:
        """Получить список всех гостей"""
        return list(self.guest_cards.values())
    
    def get_top_guests(self, limit: int = 10) -> List[GuestCard]:
        """
        Получить топ гостей по потраченной сумме.
        
        Args:
            limit: Количество результатов
        
        Returns:
            Список GuestCard, отсортированный по total_spent
        """
        sorted_guests = sorted(
            self.guest_cards.values(),
            key=lambda g: g.total_spent,
            reverse=True
        )
        return sorted_guests[:limit]
