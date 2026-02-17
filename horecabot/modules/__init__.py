"""Модули HorecaBot"""

from horecabot.modules.menu import MenuModule, MenuItem, Order, OrderItem
from horecabot.modules.quiz import QuizModule, Quiz, QuizQuestion
from horecabot.modules.loyalty import LoyaltyModule, GuestCard, LoyaltyType
from horecabot.modules.booking import BookingModule, Booking, BookingType, BookingStatus

__all__ = [
    "MenuModule",
    "MenuItem",
    "Order",
    "OrderItem",
    "QuizModule",
    "Quiz",
    "QuizQuestion",
    "LoyaltyModule",
    "GuestCard",
    "LoyaltyType",
    "BookingModule",
    "Booking",
    "BookingType",
    "BookingStatus",
]
