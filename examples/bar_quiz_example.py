"""
Пример бота для бара с квизом для подбора коктейлей
====================================================

Демонстрирует:
- Барное меню
- Интерактивный квиз для подбора коктейлей
- Кальянное меню
- Бронирование VIP-зон
"""

from horecabot import BarBot
from horecabot.modules import (
    MenuModule, MenuItem,
    QuizModule, Quiz, QuizQuestion,
    BookingModule, BookingType, Resource
)
from datetime import time
import os


def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Создаем бота для бара
    bot = BarBot(
        token=TOKEN,
        name="Бар Атмосфера",
        timezone="Europe/Moscow",
        currency="₽",
        enable_hookah=True,
        age_limit=18
    )
    
    print(f"🍸 Инициализация бара '{bot.name}'...")
    
    # ========================================
    # Настройка меню
    # ========================================
    print("🍹 Настройка барного меню...")
    
    menu = MenuModule()
    bot.menu_module = menu
    
    # Категории
    menu.add_category("cocktails", "Коктейли", emoji="🍹")
    menu.add_category("shots", "Шоты", emoji="🥃")
    menu.add_category("hookah", "Кальяны", emoji="💨")
    
    # Коктейли
    cocktails = [
        MenuItem(
            id="mojito",
            name="Мохито",
            description="Ром, мята, лайм, сахар, содовая",
            price=450.0,
            category="cocktails",
            tags=["коктейль", "освежающий", "мята", "цитрус", "легкий", "ром"]
        ),
        MenuItem(
            id="margarita",
            name="Маргарита",
            description="Текила, трипл-сек, сок лайма",
            price=500.0,
            category="cocktails",
            tags=["коктейль", "кислый", "цитрус", "крепкий", "текила"]
        ),
        MenuItem(
            id="pina_colada",
            name="Пина Колада",
            description="Ром, кокосовые сливки, ананасовый сок",
            price=480.0,
            category="cocktails",
            tags=["коктейль", "сладкий", "кокос", "тропический", "легкий", "ром"]
        ),
        MenuItem(
            id="whiskey_sour",
            name="Виски Сауэр",
            description="Виски, лимонный сок, сахарный сироп",
            price=550.0,
            category="cocktails",
            tags=["коктейль", "кислый", "цитрус", "крепкий", "виски"]
        ),
        MenuItem(
            id="espresso_martini",
            name="Эспрессо Мартини",
            description="Водка, кофейный ликер, эспрессо",
            price=520.0,
            category="cocktails",
            tags=["коктейль", "кофе", "крепкий", "бодрящий", "водка"]
        ),
        MenuItem(
            id="cosmopolitan",
            name="Космополитан",
            description="Водка, трипл-сек, клюквенный сок, лайм",
            price=490.0,
            category="cocktails",
            tags=["коктейль", "кислый", "ягоды", "крепкий", "водка"]
        ),
    ]
    
    for cocktail in cocktails:
        menu.add_item(cocktail)
    
    # Кальяны
    hookahs = [
        MenuItem(
            id="hookah_apple",
            name="Двойное яблоко",
            description="Классический вкус яблока",
            price=1500.0,
            category="hookah",
            tags=["кальян", "фруктовый", "классика"]
        ),
        MenuItem(
            id="hookah_mint",
            name="Мята",
            description="Освежающая мята",
            price=1500.0,
            category="hookah",
            tags=["кальян", "мята", "освежающий"]
        ),
        MenuItem(
            id="hookah_berry",
            name="Ягодный микс",
            description="Микс лесных ягод",
            price=1600.0,
            category="hookah",
            tags=["кальян", "ягоды", "сладкий"]
        ),
    ]
    
    for hookah in hookahs:
        menu.add_item(hookah)
    
    print(f"✅ Меню: {len(menu.items)} позиций")
    
    # ========================================
    # Создание квиза для подбора коктейля
    # ========================================
    print("🎯 Создание квиза для подбора коктейлей...")
    
    quiz_module = QuizModule(menu_module=menu)
    bot.quiz_module = quiz_module
    
    cocktail_quiz = Quiz(
        id="cocktail_selector",
        name="Подбери свой коктейль 🍹",
        description="Ответь на 3 вопроса, и мы подберем идеальный коктейль для тебя!",
        category="cocktails"
    )
    
    # Вопрос 1: Вкус
    q1 = QuizQuestion(id="taste", text="Какой вкус предпочитаете?")
    q1.add_answer("🍬 Сладкий", ["сладкий", "тропический"])
    q1.add_answer("🍋 Кислый", ["кислый", "цитрус"])
    q1.add_answer("🌿 Освежающий", ["освежающий", "мята"])
    q1.add_answer("☕ Кофейный", ["кофе", "бодрящий"])
    cocktail_quiz.add_question(q1)
    
    # Вопрос 2: Крепость
    q2 = QuizQuestion(id="strength", text="Какую крепость предпочитаете?")
    q2.add_answer("🔥 Крепкий", ["крепкий"])
    q2.add_answer("💧 Легкий", ["легкий"])
    cocktail_quiz.add_question(q2)
    
    # Вопрос 3: Основа
    q3 = QuizQuestion(id="base", text="На какой основе?")
    q3.add_answer("🥃 Виски", ["виски"])
    q3.add_answer("🍹 Ром", ["ром"])
    q3.add_answer("🍸 Водка", ["водка"])
    q3.add_answer("🌵 Текила", ["текила"])
    cocktail_quiz.add_question(q3)
    
    quiz_module.add_quiz(cocktail_quiz)
    
    print("✅ Квиз создан")
    
    # ========================================
    # Настройка бронирования VIP-зон
    # ========================================
    print("🪑 Настройка VIP-зон...")
    
    booking = BookingModule()
    bot.booking_module = booking
    
    vip_zones = [
        Resource(
            id="vip_1",
            name="VIP-зона 1",
            resource_type=BookingType.VIP_ZONE,
            capacity=6,
            min_deposit=5000.0,
            features=["диван", "столик", "приватность"]
        ),
        Resource(
            id="vip_2",
            name="VIP-зона 2",
            resource_type=BookingType.VIP_ZONE,
            capacity=10,
            min_deposit=8000.0,
            features=["большой диван", "два столика", "отдельный вход"]
        ),
    ]
    
    for zone in vip_zones:
        booking.add_resource(zone)
    
    booking.set_working_hours(
        opening=time(18, 0),
        closing=time(6, 0),  # до 6 утра
        slot_duration=120  # слоты по 2 часа
    )
    
    print(f"✅ VIP-зон: {len(vip_zones)}")
    
    # ========================================
    # Дополнительные обработчики
    # ========================================
    
    @bot.command('quiz')
    async def quiz_handler(update):
        chat_id = update['message']['chat']['id']
        user_id = update['message']['from']['id']
        
        # Начинаем квиз
        session = quiz_module.start_quiz(user_id, "cocktail_selector")
        
        if session:
            question = quiz_module.get_current_question(user_id)
            
            # Формируем кнопки с ответами
            buttons = [
                [{"text": answer["text"], "callback_data": f"quiz_answer_{i}"}]
                for i, answer in enumerate(question.answers)
            ]
            
            keyboard = bot.create_inline_keyboard(buttons)
            
            await bot.send_message(
                chat_id,
                f"🎯 <b>{cocktail_quiz.name}</b>\n\n{question.text}",
                reply_markup=keyboard
            )
    
    @bot.command('events')
    async def events_handler(update):
        chat_id = update['message']['chat']['id']
        
        events_text = (
            "🎫 <b>Афиша мероприятий</b>\n\n"
            "📅 Пятница, 15 марта\n"
            "🎵 <b>Live Jazz</b>\n"
            "Время: 21:00 - 01:00\n"
            "Вход: 500₽\n\n"
            "📅 Суббота, 16 марта\n"
            "🎉 <b>DJ Night</b>\n"
            "Время: 22:00 - 04:00\n"
            "Вход: 1000₽ (включает 1 коктейль)\n\n"
            "📅 Воскресенье, 17 марта\n"
            "🎤 <b>Караоке вечер</b>\n"
            "Время: 20:00 - 02:00\n"
            "Вход: бесплатно\n\n"
            "💡 Для бронирования VIP-зоны используйте /booking"
        )
        
        await bot.send_message(chat_id, events_text)
    
    # ========================================
    # Запуск бота
    # ========================================
    print("\n" + "="*50)
    print(f"🚀 Бот '{bot.name}' готов к работе!")
    print("="*50)
    print(f"🍹 Меню: {len(menu.items)} позиций")
    print(f"🎯 Квиз: Подбор коктейлей")
    print(f"🪑 VIP-зон: {len(vip_zones)}")
    print(f"💨 Кальяны: Да")
    print(f"⚠️  Возраст: {bot.age_limit}+")
    print("="*50 + "\n")
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")


if __name__ == "__main__":
    main()
