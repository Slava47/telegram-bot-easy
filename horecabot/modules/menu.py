"""
Модуль меню и заказов
======================

Управление меню, категориями, позициями и заказами.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MenuItem:
    """
    Позиция меню.
    
    Attributes:
        id: Уникальный идентификатор
        name: Название блюда/напитка
        description: Описание
        price: Цена
        category: Категория (закуски, основные блюда и т.д.)
        photo_url: URL фотографии (опционально)
        weight: Вес или объем (опционально)
        calories: Калорийность (опционально)
        allergens: Список аллергенов (опционально)
        cooking_time: Время приготовления в минутах (опционально)
        tags: Теги для интеллектуального подбора
        available: Доступно ли блюдо
    """
    id: str
    name: str
    description: str
    price: float
    category: str
    photo_url: Optional[str] = None
    weight: Optional[str] = None
    calories: Optional[int] = None
    allergens: List[str] = field(default_factory=list)
    cooking_time: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    available: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "photo_url": self.photo_url,
            "weight": self.weight,
            "calories": self.calories,
            "allergens": self.allergens,
            "cooking_time": self.cooking_time,
            "tags": self.tags,
            "available": self.available,
        }


@dataclass
class OrderItem:
    """Позиция в заказе"""
    menu_item: MenuItem
    quantity: int
    modifiers: Dict[str, str] = field(default_factory=dict)  # например, {"соус": "кетчуп"}
    comment: str = ""
    
    @property
    def total_price(self) -> float:
        """Общая стоимость позиции"""
        return self.menu_item.price * self.quantity


@dataclass
class Order:
    """
    Заказ.
    
    Attributes:
        id: Уникальный идентификатор заказа
        user_id: ID пользователя Telegram
        items: Список позиций в заказе
        delivery_type: Тип получения (доставка, самовывоз, в зале)
        delivery_address: Адрес доставки (для доставки)
        delivery_cost: Стоимость доставки
        comment: Комментарий к заказу
        status: Статус заказа
        created_at: Время создания
    """
    id: str
    user_id: int
    items: List[OrderItem] = field(default_factory=list)
    delivery_type: str = "pickup"  # delivery, pickup, dine_in
    delivery_address: Optional[str] = None
    delivery_cost: float = 0.0
    comment: str = ""
    status: str = "new"  # new, confirmed, cooking, ready, delivered, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def subtotal(self) -> float:
        """Сумма заказа без доставки"""
        return sum(item.total_price for item in self.items)
    
    @property
    def total(self) -> float:
        """Общая сумма заказа с доставкой"""
        return self.subtotal + self.delivery_cost
    
    def add_item(self, menu_item: MenuItem, quantity: int = 1, **kwargs):
        """Добавить позицию в заказ"""
        order_item = OrderItem(menu_item=menu_item, quantity=quantity, **kwargs)
        self.items.append(order_item)
    
    def remove_item(self, item_index: int):
        """Удалить позицию из заказа"""
        if 0 <= item_index < len(self.items):
            self.items.pop(item_index)


class MenuModule:
    """
    Модуль управления меню.
    
    Позволяет создавать категории, добавлять позиции,
    управлять доступностью блюд.
    
    Example:
        >>> menu = MenuModule()
        >>> menu.add_category("Закуски", "🍕")
        >>> item = MenuItem(
        ...     id="item_001",
        ...     name="Цезарь с курицей",
        ...     description="Классический салат",
        ...     price=450.0,
        ...     category="Закуски",
        ...     tags=["салат", "курица", "легкое"]
        ... )
        >>> menu.add_item(item)
    """
    
    def __init__(self):
        self.categories: Dict[str, str] = {}  # id -> название
        self.items: Dict[str, MenuItem] = {}  # id -> MenuItem
        self.items_by_category: Dict[str, List[str]] = {}  # category -> [item_ids]
    
    def add_category(self, category_id: str, name: str, emoji: str = "📋"):
        """
        Добавить категорию меню.
        
        Args:
            category_id: Уникальный идентификатор категории
            name: Название категории
            emoji: Эмодзи для визуального оформления
        """
        self.categories[category_id] = f"{emoji} {name}"
        self.items_by_category[category_id] = []
    
    def add_item(self, item: MenuItem):
        """
        Добавить позицию в меню.
        
        Args:
            item: Объект MenuItem
        """
        self.items[item.id] = item
        if item.category not in self.items_by_category:
            self.items_by_category[item.category] = []
        self.items_by_category[item.category].append(item.id)
    
    def get_item(self, item_id: str) -> Optional[MenuItem]:
        """Получить позицию по ID"""
        return self.items.get(item_id)
    
    def get_category_items(self, category_id: str) -> List[MenuItem]:
        """Получить все позиции категории"""
        item_ids = self.items_by_category.get(category_id, [])
        return [self.items[item_id] for item_id in item_ids if item_id in self.items]
    
    def search_by_tags(self, tags: List[str], limit: int = 3) -> List[MenuItem]:
        """
        Поиск позиций по тегам (для квизов).
        
        Args:
            tags: Список тегов для поиска
            limit: Максимальное количество результатов
        
        Returns:
            Список наиболее подходящих позиций
        """
        scored_items = []
        
        for item in self.items.values():
            if not item.available:
                continue
            
            # Подсчитываем совпадения тегов
            matches = sum(1 for tag in tags if tag in item.tags)
            if matches > 0:
                scored_items.append((matches, item))
        
        # Сортируем по количеству совпадений
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return [item for _, item in scored_items[:limit]]
    
    def set_item_availability(self, item_id: str, available: bool):
        """Установить доступность позиции"""
        if item_id in self.items:
            self.items[item_id].available = available


class OrderModule:
    """
    Модуль управления заказами.
    
    Создание заказов, корзина, история заказов.
    
    Example:
        >>> order_module = OrderModule()
        >>> order = order_module.create_order(user_id=123456)
        >>> order.add_item(menu_item, quantity=2)
        >>> order_module.confirm_order(order.id)
    """
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.user_orders: Dict[int, List[str]] = {}  # user_id -> [order_ids]
        self.active_carts: Dict[int, Order] = {}  # user_id -> Order (корзина)
    
    def create_order(self, user_id: int) -> Order:
        """
        Создать новый заказ (корзину) для пользователя.
        
        Args:
            user_id: ID пользователя Telegram
        
        Returns:
            Объект Order
        """
        order_id = f"order_{user_id}_{int(datetime.now().timestamp())}"
        order = Order(id=order_id, user_id=user_id)
        self.active_carts[user_id] = order
        return order
    
    def get_cart(self, user_id: int) -> Optional[Order]:
        """Получить активную корзину пользователя"""
        return self.active_carts.get(user_id)
    
    def confirm_order(self, order_id: str):
        """
        Подтвердить заказ (переместить из корзины в заказы).
        
        Args:
            order_id: ID заказа
        """
        # Находим заказ
        order = None
        user_id = None
        
        for uid, cart in self.active_carts.items():
            if cart.id == order_id:
                order = cart
                user_id = uid
                break
        
        if order:
            order.status = "confirmed"
            self.orders[order_id] = order
            
            # Добавляем в историю пользователя
            if user_id not in self.user_orders:
                self.user_orders[user_id] = []
            self.user_orders[user_id].append(order_id)
            
            # Удаляем из активных корзин
            del self.active_carts[user_id]
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Получить заказ по ID"""
        return self.orders.get(order_id)
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        """Получить историю заказов пользователя"""
        order_ids = self.user_orders.get(user_id, [])
        return [self.orders[oid] for oid in order_ids if oid in self.orders]
    
    def update_order_status(self, order_id: str, status: str):
        """Обновить статус заказа"""
        if order_id in self.orders:
            self.orders[order_id].status = status
