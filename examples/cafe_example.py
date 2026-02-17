"""
Пример бота для кафе с программой лояльности
=============================================

Демонстрирует:
- Упрощенное меню (напитки и десерты)
- Систему штампов (6-й кофе бесплатно)
- Предзаказ
"""

from horecabot import CafeBot
from horecabot.modules import (
    MenuModule, MenuItem,
    LoyaltyModule, LoyaltyType
)
import os


def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Создаем бота для кафе
    bot = CafeBot(
        token=TOKEN,
        name="Кофейня Аромат",
        timezone="Europe/Moscow",
        currency="₽",
        loyalty_program="stamps"  # Система штампов
    )
    
    print(f"☕ Инициализация кофейни '{bot.name}'...")
    
    # Настройка меню
    menu = MenuModule()
    bot.menu_module = menu
    
    # Категории
    menu.add_category("coffee", "Кофе", emoji="☕")
    menu.add_category("tea", "Чай", emoji="🍵")
    menu.add_category("desserts", "Десерты", emoji="🧁")
    
    # Кофе
    menu.add_item(MenuItem(
        id="espresso",
        name="Эспрессо",
        description="Классический крепкий кофе",
        price=120.0,
        category="coffee",
        weight="30мл",
        tags=["кофе", "крепкий", "классический"]
    ))
    
    menu.add_item(MenuItem(
        id="cappuccino",
        name="Капучино",
        description="Эспрессо с молочной пенкой",
        price=180.0,
        category="coffee",
        weight="200мл",
        tags=["кофе", "молочный", "нежный"]
    ))
    
    menu.add_item(MenuItem(
        id="latte",
        name="Латте",
        description="Кофе с большим количеством молока",
        price=200.0,
        category="coffee",
        weight="300мл",
        tags=["кофе", "молочный", "мягкий"]
    ))
    
    # Десерты
    menu.add_item(MenuItem(
        id="croissant",
        name="Круассан",
        description="Французский слоеный круассан",
        price=150.0,
        category="desserts",
        weight="80г",
        tags=["выпечка", "французский"]
    ))
    
    # Программа лояльности
    loyalty = LoyaltyModule(
        loyalty_type=LoyaltyType.STAMPS,
        stamps_for_reward=6  # Каждый 6-й бесплатно
    )
    bot.loyalty_module = loyalty
    
    print(f"✅ Меню: {len(menu.items)} позиций")
    print(f"🎁 Лояльность: каждый 6-й кофе бесплатно!")
    print(f"🚀 Бот готов к работе!\n")
    
    bot.run()


if __name__ == "__main__":
    main()
