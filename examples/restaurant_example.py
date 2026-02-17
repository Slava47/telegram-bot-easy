"""
Полный пример бота для ресторана
==================================

Демонстрирует все возможности RestaurantBot:
- Электронное меню с категориями
- Система заказов и корзина
- Бронирование столиков
- Интерактивный квиз для подбора блюд
- Программа лояльности
- Веб-панель аналитики
"""

from horecabot import RestaurantBot
from horecabot.modules import (
    MenuModule, MenuItem,
    OrderModule,
    BookingModule, BookingType, Resource,
    QuizModule, Quiz, QuizQuestion,
    LoyaltyModule, LoyaltyType
)
from horecabot.web import create_analytics_app
from datetime import time
import threading
import os


def main():
    # Получаем токен из переменной окружения
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Создаем бота для ресторана
    bot = RestaurantBot(
        token=TOKEN,
        name="Ресторан Премиум",
        timezone="Europe/Moscow",
        currency="₽",
        enable_delivery=True,
        enable_booking=True,
        enable_reviews=True
    )
    
    print(f"🍽 Инициализация бота '{bot.name}'...")
    
    # ========================================
    # 1. Настройка меню
    # ========================================
    print("📋 Настройка меню...")
    
    menu = MenuModule()
    bot.menu_module = menu
    
    # Добавляем категории
    menu.add_category("appetizers", "Закуски", emoji="🥗")
    menu.add_category("main", "Основные блюда", emoji="🍝")
    menu.add_category("desserts", "Десерты", emoji="🍰")
    menu.add_category("drinks", "Напитки", emoji="🍹")
    
    # Добавляем блюда
    
    # Закуски
    menu.add_item(MenuItem(
        id="caesar",
        name="Цезарь с курицей",
        description="Классический салат с пармезаном, соусом и гренками",
        price=450.0,
        category="appetizers",
        weight="250г",
        calories=320,
        allergens=["глютен", "молоко", "яйца"],
        cooking_time=10,
        tags=["салат", "курица", "легкое", "свежее"],
        available=True
    ))
    
    menu.add_item(MenuItem(
        id="bruschetta",
        name="Брускетта с томатами",
        description="Хрустящий хлеб с томатами, базиликом и оливковым маслом",
        price=350.0,
        category="appetizers",
        weight="200г",
        calories=180,
        allergens=["глютен"],
        cooking_time=8,
        tags=["вегетарианское", "легкое", "свежее"],
        available=True
    ))
    
    # Основные блюда
    menu.add_item(MenuItem(
        id="steak",
        name="Стейк Рибай",
        description="Сочный стейк из мраморной говядины с картофелем",
        price=1450.0,
        category="main",
        weight="350г",
        calories=650,
        allergens=[],
        cooking_time=25,
        tags=["мясо", "сытное", "премиум", "гриль"],
        available=True
    ))
    
    menu.add_item(MenuItem(
        id="pasta_carbonara",
        name="Паста Карбонара",
        description="Паста со сливочным соусом, беконом и пармезаном",
        price=650.0,
        category="main",
        weight="350г",
        calories=580,
        allergens=["глютен", "молоко", "яйца"],
        cooking_time=15,
        tags=["паста", "сливочный", "сытное", "итальянское"],
        available=True
    ))
    
    menu.add_item(MenuItem(
        id="salmon",
        name="Лосось на гриле",
        description="Стейк лосося с овощами гриль и лимоном",
        price=950.0,
        category="main",
        weight="300г",
        calories=420,
        allergens=["рыба"],
        cooking_time=20,
        tags=["рыба", "здоровое", "легкое", "гриль"],
        available=True
    ))
    
    # Десерты
    menu.add_item(MenuItem(
        id="tiramisu",
        name="Тирамису",
        description="Классический итальянский десерт с маскарпоне и кофе",
        price=380.0,
        category="desserts",
        weight="150г",
        calories=350,
        allergens=["молоко", "яйца", "глютен"],
        cooking_time=5,
        tags=["десерт", "сладкое", "кофейный", "итальянское"],
        available=True
    ))
    
    menu.add_item(MenuItem(
        id="cheesecake",
        name="Чизкейк Нью-Йорк",
        description="Нежный сырный торт с ягодным соусом",
        price=420.0,
        category="desserts",
        weight="180г",
        calories=410,
        allergens=["молоко", "яйца", "глютен"],
        cooking_time=5,
        tags=["десерт", "сладкое", "сырный", "ягоды"],
        available=True
    ))
    
    # Напитки
    menu.add_item(MenuItem(
        id="lemonade",
        name="Домашний лимонад",
        description="Освежающий лимонад с мятой",
        price=180.0,
        category="drinks",
        weight="400мл",
        calories=120,
        allergens=[],
        cooking_time=3,
        tags=["напиток", "безалкогольное", "освежающее", "цитрус"],
        available=True
    ))
    
    menu.add_item(MenuItem(
        id="wine_red",
        name="Красное вино (бокал)",
        description="Бокал красного сухого вина",
        price=350.0,
        category="drinks",
        weight="150мл",
        calories=125,
        allergens=[],
        cooking_time=2,
        tags=["напиток", "алкоголь", "вино"],
        available=True
    ))
    
    print(f"✅ Добавлено {len(menu.items)} позиций в меню")
    
    # ========================================
    # 2. Настройка системы заказов
    # ========================================
    print("🛒 Настройка системы заказов...")
    
    orders = OrderModule()
    bot.order_module = orders
    
    # ========================================
    # 3. Настройка бронирования
    # ========================================
    print("📅 Настройка системы бронирования...")
    
    booking = BookingModule()
    bot.booking_module = booking
    
    # Добавляем столики
    for i in range(1, 16):
        capacity = 2 if i <= 5 else (4 if i <= 12 else 6)
        features = []
        if i in [1, 2, 8, 9]:
            features.append("у окна")
        if i >= 13:
            features.append("для большой компании")
        
        table = Resource(
            id=f"table_{i}",
            name=f"Столик №{i}",
            resource_type=BookingType.TABLE,
            capacity=capacity,
            features=features
        )
        booking.add_resource(table)
    
    # Настраиваем рабочие часы
    booking.set_working_hours(
        opening=time(10, 0),
        closing=time(23, 0),
        slot_duration=60  # слоты по 1 часу
    )
    booking.booking_depth_days = 30  # бронирование на 30 дней вперед
    
    print(f"✅ Добавлено {len(booking.resources)} столиков")
    
    # ========================================
    # 4. Настройка квизов
    # ========================================
    print("🎯 Настройка интерактивных квизов...")
    
    quiz_module = QuizModule(menu_module=menu)
    bot.quiz_module = quiz_module
    
    # Создаем квиз для подбора основного блюда
    main_dish_quiz = Quiz(
        id="main_dish_quiz",
        name="Подбери свое блюдо 🍽",
        description="Ответь на 3 вопроса, и мы подберем идеальное блюдо!",
        category="main"
    )
    
    q1 = QuizQuestion(id="q1", text="Что предпочитаете?")
    q1.add_answer("🥩 Мясо", ["мясо", "сытное"])
    q1.add_answer("🐟 Рыбу", ["рыба", "легкое"])
    q1.add_answer("🍝 Пасту", ["паста", "итальянское"])
    main_dish_quiz.add_question(q1)
    
    q2 = QuizQuestion(id="q2", text="Какой способ приготовления?")
    q2.add_answer("🔥 Гриль", ["гриль"])
    q2.add_answer("🍳 Сливочный соус", ["сливочный"])
    q2.add_answer("💚 Здоровое питание", ["здоровое", "легкое"])
    main_dish_quiz.add_question(q2)
    
    q3 = QuizQuestion(id="q3", text="Уровень сытности?")
    q3.add_answer("🔴 Сытное", ["сытное"])
    q3.add_answer("🟡 Среднее", ["легкое"])
    q3.add_answer("🟢 Легкое", ["легкое", "свежее"])
    main_dish_quiz.add_question(q3)
    
    quiz_module.add_quiz(main_dish_quiz)
    
    print(f"✅ Создан квиз '{main_dish_quiz.name}'")
    
    # ========================================
    # 5. Настройка программы лояльности
    # ========================================
    print("🎁 Настройка программы лояльности...")
    
    loyalty = LoyaltyModule(
        loyalty_type=LoyaltyType.POINTS,
        points_per_ruble=0.05  # 5% кэшбэк баллами
    )
    bot.loyalty_module = loyalty
    
    print("✅ Программа лояльности: 5% кэшбэк баллами")
    
    # ========================================
    # 6. Запуск веб-панели аналитики
    # ========================================
    print("📊 Настройка веб-панели аналитики...")
    
    web_app = create_analytics_app(
        bot_instance=bot,
        admin_login=os.getenv("ADMIN_LOGIN", "admin"),
        admin_password=os.getenv("ADMIN_PASSWORD", "admin123")
    )
    
    # Запускаем веб-сервер в отдельном потоке
    def run_web_server():
        web_app.run(host="0.0.0.0", port=5000, debug=False)
    
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    print("✅ Веб-панель запущена на http://localhost:5000")
    print("   Логин: admin")
    print("   Пароль: admin123")
    
    # ========================================
    # 7. Запуск бота
    # ========================================
    print("\n" + "="*50)
    print(f"🚀 Бот '{bot.name}' готов к работе!")
    print("="*50)
    print(f"📋 Меню: {len(menu.items)} позиций")
    print(f"📅 Бронирование: {len(booking.resources)} столиков")
    print(f"🎯 Квизы: {len(quiz_module.quizzes)}")
    print(f"🎁 Лояльность: баллы (5% кэшбэк)")
    print(f"📊 Веб-панель: http://localhost:5000")
    print("="*50 + "\n")
    
    # Запускаем бота
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")


if __name__ == "__main__":
    main()
