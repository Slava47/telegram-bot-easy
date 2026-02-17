"""Специализированные классы для разных типов заведений"""

from horecabot.establishments.restaurant import RestaurantBot
from horecabot.establishments.hotel import HotelBot
from horecabot.establishments.cafe import CafeBot
from horecabot.establishments.bar import BarBot
from horecabot.establishments.fastfood import FastFoodBot

__all__ = [
    "RestaurantBot",
    "HotelBot",
    "CafeBot",
    "BarBot",
    "FastFoodBot",
]
