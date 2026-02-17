"""
HorecaBot - Специализированная библиотека для создания Telegram ботов для HoReCa
===================================================================================

HorecaBot упрощает создание профессиональных Telegram ботов для ресторанов,
отелей, кафе, баров и других заведений индустрии гостеприимства.

Основные возможности:
- Поддержка различных типов заведений (ресторан, отель, кафе, бар, фастфуд)
- Модуль меню и заказов с корзиной
- Система бронирования столиков/номеров
- Интерактивные квизы для подбора блюд/напитков
- Карточка гостя и программа лояльности
- Веб-панель аналитики
- Интеграции с платежными системами

Пример использования:
    >>> from horecabot import RestaurantBot
    >>> bot = RestaurantBot(
    ...     token="YOUR_BOT_TOKEN",
    ...     name="Мой Ресторан",
    ...     timezone="Europe/Moscow",
    ...     currency="₽"
    ... )
    >>> bot.run()
"""

__version__ = "1.0.0"
__author__ = "HorecaBot Team"
__license__ = "MIT"

from horecabot.core.base import HorecaBot
from horecabot.establishments.restaurant import RestaurantBot
from horecabot.establishments.hotel import HotelBot
from horecabot.establishments.cafe import CafeBot
from horecabot.establishments.bar import BarBot
from horecabot.establishments.fastfood import FastFoodBot

__all__ = [
    "HorecaBot",
    "RestaurantBot",
    "HotelBot",
    "CafeBot",
    "BarBot",
    "FastFoodBot",
]
