"""
Пример бота для отеля
======================

Демонстрирует:
- Бронирование номеров
- Консьерж-сервис
- Информация об услугах отеля
"""

from horecabot import HotelBot
from horecabot.modules import (
    BookingModule, BookingType, Resource,
    MenuModule, MenuItem
)
from datetime import time
import os


def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Создаем бота для отеля
    bot = HotelBot(
        token=TOKEN,
        name="Гранд Отель",
        timezone="Europe/Moscow",
        currency="₽",
        enable_concierge=True,
        enable_spa=True
    )
    
    print(f"🏨 Инициализация отеля '{bot.name}'...")
    
    # ========================================
    # Настройка бронирования номеров
    # ========================================
    print("🛏 Настройка номеров...")
    
    booking = BookingModule()
    bot.booking_module = booking
    
    # Добавляем номера
    rooms = [
        Resource(
            id="standard_101",
            name="Стандарт 101",
            resource_type=BookingType.ROOM,
            capacity=2,
            price_per_night=3000.0,
            features=["двуспальная кровать", "душ"]
        ),
        Resource(
            id="standard_102",
            name="Стандарт 102",
            resource_type=BookingType.ROOM,
            capacity=2,
            price_per_night=3000.0,
            features=["две односпальные кровати", "душ"]
        ),
        Resource(
            id="deluxe_201",
            name="Делюкс 201",
            resource_type=BookingType.ROOM,
            capacity=2,
            price_per_night=5000.0,
            features=["двуспальная кровать", "ванна", "балкон"]
        ),
        Resource(
            id="deluxe_202",
            name="Делюкс 202",
            resource_type=BookingType.ROOM,
            capacity=3,
            price_per_night=5500.0,
            features=["двуспальная кровать", "диван", "ванна", "балкон"]
        ),
        Resource(
            id="suite_301",
            name="Люкс 301",
            resource_type=BookingType.ROOM,
            capacity=4,
            price_per_night=8000.0,
            features=["спальня", "гостиная", "джакузи", "вид на море"]
        ),
    ]
    
    for room in rooms:
        booking.add_resource(room)
    
    print(f"✅ Добавлено {len(rooms)} номеров")
    
    # ========================================
    # Меню ресторана отеля
    # ========================================
    print("🍽 Настройка меню ресторана...")
    
    menu = MenuModule()
    bot.menu_module = menu
    
    menu.add_category("breakfast", "Завтраки", emoji="🍳")
    menu.add_category("room_service", "Обслуживание в номер", emoji="🛎")
    
    # Завтраки
    menu.add_item(MenuItem(
        id="continental",
        name="Континентальный завтрак",
        description="Круассаны, джем, сок, кофе",
        price=500.0,
        category="breakfast",
        tags=["завтрак", "легкий"]
    ))
    
    menu.add_item(MenuItem(
        id="english",
        name="Английский завтрак",
        description="Яичница, бекон, сосиски, тосты",
        price=750.0,
        category="breakfast",
        tags=["завтрак", "сытный"]
    ))
    
    # Room service
    menu.add_item(MenuItem(
        id="club_sandwich",
        name="Клаб-сэндвич",
        description="Многослойный сэндвич с курицей",
        price=650.0,
        category="room_service",
        tags=["сэндвич", "курица"]
    ))
    
    print(f"✅ Меню: {len(menu.items)} позиций")
    
    # ========================================
    # Дополнительные обработчики
    # ========================================
    
    @bot.command('spa')
    async def spa_handler(update):
        chat_id = update['message']['chat']['id']
        
        spa_text = (
            "💆 <b>Спа-салон 'Релакс'</b>\n\n"
            "Часы работы: 09:00 - 21:00\n\n"
            "Услуги:\n"
            "• Массаж классический (60 мин) — 2500₽\n"
            "• Массаж расслабляющий (90 мин) — 3500₽\n"
            "• Спа-уход для лица (60 мин) — 3000₽\n"
            "• Сауна (1 час) — 1000₽\n"
            "• Хаммам (1 час) — 1200₽\n\n"
            "📞 Для записи нажмите кнопку ниже"
        )
        
        keyboard = bot.create_inline_keyboard([
            [{"text": "📞 Записаться", "callback_data": "spa_booking"}],
            [{"text": "🔙 Назад", "callback_data": "back_to_main"}]
        ])
        
        await bot.send_message(chat_id, spa_text, reply_markup=keyboard)
    
    @bot.command('concierge')
    async def concierge_handler(update):
        chat_id = update['message']['chat']['id']
        
        concierge_text = (
            "🎩 <b>Консьерж-сервис</b>\n\n"
            "Мы поможем вам:\n"
            "• 🚖 Заказать такси\n"
            "• 🎭 Забронировать билеты в театр\n"
            "• 🏛 Организовать экскурсию\n"
            "• 🍽 Зарезервировать столик в ресторане\n"
            "• 🛍 Помощь с шопингом\n\n"
            "Доступны 24/7\n"
            "Звоните: +7 (999) 123-45-67"
        )
        
        keyboard = bot.create_inline_keyboard([
            [{"text": "🚖 Заказать такси", "callback_data": "concierge_taxi"}],
            [{"text": "🎭 Билеты в театр", "callback_data": "concierge_theatre"}],
            [{"text": "🏛 Экскурсии", "callback_data": "concierge_tours"}],
            [{"text": "🔙 Назад", "callback_data": "back_to_main"}]
        ])
        
        await bot.send_message(chat_id, concierge_text, reply_markup=keyboard)
    
    @bot.command('services')
    async def services_handler(update):
        chat_id = update['message']['chat']['id']
        
        services_text = (
            "ℹ️ <b>Услуги отеля</b>\n\n"
            "🏊‍♂️ Бассейн — 07:00-22:00 (бесплатно для гостей)\n"
            "💪 Фитнес-центр — 24/7 (бесплатно)\n"
            "💆 Спа-салон — 09:00-21:00\n"
            "🍽 Ресторан — 07:00-23:00\n"
            "☕ Лобби-бар — 24/7\n"
            "🅿️ Парковка — бесплатно\n"
            "📶 Wi-Fi — бесплатно\n"
            "🧺 Прачечная — 08:00-20:00\n\n"
            "Конференц-зал на 50 человек доступен для бронирования"
        )
        
        keyboard = bot.create_inline_keyboard([
            [{"text": "🔙 Назад", "callback_data": "back_to_main"}]
        ])
        
        await bot.send_message(chat_id, services_text, reply_markup=keyboard)
    
    # ========================================
    # Запуск бота
    # ========================================
    print("\n" + "="*50)
    print(f"🚀 Бот '{bot.name}' готов к работе!")
    print("="*50)
    print(f"🛏 Номеров: {len(rooms)}")
    print(f"🍽 Меню: {len(menu.items)} позиций")
    print(f"🎩 Консьерж: Включен")
    print(f"💆 Спа: Включен")
    print("="*50 + "\n")
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")


if __name__ == "__main__":
    main()
