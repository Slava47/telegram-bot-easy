# HorecaBot 🍽

**Специализированная библиотека для создания Telegram ботов для предприятий сферы HoReCa**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📖 Оглавление

- [О проекте](#о-проекте)
- [Возможности](#возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Типы заведений](#типы-заведений)
- [Модули](#модули)
- [Веб-аналитика](#веб-аналитика)
- [Примеры использования](#примеры-использования)
- [Документация](#документация)
- [Лицензия](#лицензия)

## О проекте

**HorecaBot** — это мощная библиотека для Python, которая кардинально упрощает создание профессиональных Telegram ботов для предприятий индустрии гостеприимства (отели, рестораны, кафе, бары, фастфуд).

### Философия библиотеки

Владелец заведения или менеджер должен иметь возможность запустить полноценный работающий бот **за 15 минут**, написав минимум кода и не вникая в тонкости Telegram API. Библиотека берет на себя всю рутину: регистрацию команд, создание меню, обработку бронирований, корзину заказов, систему лояльности.

## Возможности

### 🎯 Основные функции

- ✅ **Поддержка 5 типов заведений** — ресторан, отель, кафе, бар, фастфуд
- ✅ **Электронное меню** с категориями, фото, модификаторами, аллергенами
- ✅ **Система заказов** с корзиной и различными способами получения
- ✅ **Бронирование** столиков/номеров с учетом доступности
- ✅ **Интерактивные квизы** для подбора блюд и напитков
- ✅ **Карточка гостя** с историей заказов и статистикой
- ✅ **Программа лояльности** (баллы, штампы, уровни)
- ✅ **Веб-панель аналитики** для управления заведением
- ✅ **Готовые интеграции** с платежными системами

### 🚀 Преимущества

- **Минимум кода** — запустите бот за 15 минут
- **Модульная архитектура** — используйте только нужные функции
- **Асинхронность** — высокая производительность на базе asyncio
- **Типизация** — полная поддержка type hints для IDE
- **Документация** — подробные руководства на русском языке
- **Примеры** — готовые шаблоны для разных типов заведений

## Установка

### Требования

- Python 3.8 или выше
- Токен Telegram бота от [@BotFather](https://t.me/BotFather)

### Установка из PyPI

```bash
pip install horecabot
```

### Установка из исходников

```bash
git clone https://github.com/Slava47/telegram-bot-easy.git
cd telegram-bot-easy
pip install -r requirements.txt
python setup.py install
```

### Дополнительные зависимости

```bash
# Для PostgreSQL
pip install horecabot[postgresql]

# Для платежных систем
pip install horecabot[payments]

# Для аналитики
pip install horecabot[analytics]

# Все зависимости
pip install horecabot[postgresql,payments,analytics]
```

## Быстрый старт

### Создание простого бота для ресторана

```python
from horecabot import RestaurantBot

# Создаем бота
bot = RestaurantBot(
    token="YOUR_BOT_TOKEN",
    name="Ресторан Вкусно",
    timezone="Europe/Moscow",
    currency="₽"
)

# Запускаем
bot.run()
```

**Готово!** 🎉 Ваш бот уже работает с базовым функционалом!

### Добавление меню

```python
from horecabot import RestaurantBot
from horecabot.modules import MenuModule, MenuItem

bot = RestaurantBot(
    token="YOUR_BOT_TOKEN",
    name="Ресторан Вкусно"
)

# Создаем модуль меню
menu = MenuModule()
bot.menu_module = menu

# Добавляем категорию
menu.add_category("salads", "Салаты", emoji="🥗")

# Добавляем блюдо
salad = MenuItem(
    id="caesar",
    name="Цезарь с курицей",
    description="Классический салат с пармезаном и соусом",
    price=450.0,
    category="salads",
    weight="250г",
    calories=320,
    tags=["салат", "курица", "легкое"],
    photo_url="https://example.com/caesar.jpg"
)
menu.add_item(salad)

bot.run()
```

## Типы заведений

### 🍽 RestaurantBot — Ресторан

Полнофункциональный бот для ресторана:
- Бронирование столиков с учетом количества гостей
- Меню с категориями и модификаторами
- Система доставки с расчетом стоимости
- Отзывы и рейтинги блюд
- Специальные предложения

```python
from horecabot import RestaurantBot

bot = RestaurantBot(
    token="YOUR_TOKEN",
    name="Ресторан Премиум",
    enable_delivery=True,
    enable_booking=True,
    enable_reviews=True
)
```

### 🏨 HotelBot — Отель

Специализированный бот для отеля:
- Бронирование номеров с датами заезда/выезда
- Консьерж-сервис (такси, экскурсии)
- Информация об услугах (бассейн, спа, рестораны)
- Продление проживания и поздний выезд

```python
from horecabot import HotelBot

bot = HotelBot(
    token="YOUR_TOKEN",
    name="Гранд Отель",
    enable_concierge=True,
    enable_spa=True
)
```

### ☕ CafeBot — Кафе и кофейня

Оптимизирован для быстрых заказов:
- Упрощенное меню (напитки, десерты)
- Программа лояльности (штампы/баллы)
- Предзаказ с выбором времени
- Push-уведомления о новинках

```python
from horecabot import CafeBot

bot = CafeBot(
    token="YOUR_TOKEN",
    name="Кофейня Аромат",
    loyalty_program="stamps"  # 6-й кофе бесплатно
)
```

### 🍸 BarBot — Бар и ночной клуб

Специальные возможности для баров:
- Бронирование VIP-зон с депозитом
- Гостевой лист
- Афиша мероприятий
- Кальянное меню
- Информация о дресс-коде

```python
from horecabot import BarBot

bot = BarBot(
    token="YOUR_TOKEN",
    name="Бар Атмосфера",
    enable_hookah=True,
    age_limit=18
)
```

### 🍔 FastFoodBot — Фастфуд

Быстрый заказ за 3 клика:
- Упрощенное меню
- Комбо-предложения
- Купоны на скидку
- Отслеживание статуса заказа
- Drive-Through

```python
from horecabot import FastFoodBot

bot = FastFoodBot(
    token="YOUR_TOKEN",
    name="Бургер Мастер",
    enable_drive_through=True
)
```

## Модули

### 📋 Модуль меню и заказов

Управление меню, категориями и заказами:

```python
from horecabot.modules import MenuModule, MenuItem, OrderModule

# Создаем меню
menu = MenuModule()
menu.add_category("main", "Основные блюда", emoji="🍝")

# Добавляем блюдо с модификаторами
pasta = MenuItem(
    id="carbonara",
    name="Карбонара",
    description="Паста со сливочным соусом и беконом",
    price=650.0,
    category="main",
    weight="350г",
    cooking_time=20,
    allergens=["молоко", "глютен"],
    tags=["паста", "сливочный", "сытное"]
)
menu.add_item(pasta)

# Создаем систему заказов
orders = OrderModule()
order = orders.create_order(user_id=123456)
order.add_item(pasta, quantity=2)
order.delivery_type = "delivery"
order.delivery_address = "ул. Ленина, д. 10"
```

### 🎯 Модуль интерактивного подбора (квиз)

Создание тестов для подбора блюд:

```python
from horecabot.modules import QuizModule, Quiz, QuizQuestion

quiz_module = QuizModule(menu_module=menu)

# Создаем квиз для коктейлей
quiz = Quiz(
    id="cocktail_quiz",
    name="Подбери свой коктейль 🍹",
    description="Ответь на 3 вопроса"
)

# Добавляем вопросы
q1 = QuizQuestion(id="q1", text="Какой вкус предпочитаете?")
q1.add_answer("🍬 Сладкий", ["sweet", "fruity"])
q1.add_answer("🍋 Кислый", ["sour", "citrus"])
quiz.add_question(q1)

quiz_module.add_quiz(quiz)

# Пользователь проходит квиз
session = quiz_module.start_quiz(user_id=123456, quiz_id="cocktail_quiz")
quiz_module.answer_question(user_id=123456, tags=["sweet", "fruity"])

# Получаем рекомендации
recommendations = quiz_module.get_recommendations(user_id=123456, limit=3)
```

### 👤 Модуль карточки гостя и лояльности

Персонализация и программа лояльности:

```python
from horecabot.modules import LoyaltyModule, LoyaltyType

# Создаем систему лояльности
loyalty = LoyaltyModule(
    loyalty_type=LoyaltyType.POINTS,
    points_per_ruble=0.05  # 5% кэшбэк
)

# Регистрируем гостя
card = loyalty.create_guest_card(
    user_id=123456,
    name="Иван Иванов",
    phone="+79991234567"
)

# Обрабатываем заказ (начисляем баллы)
loyalty.process_order(
    user_id=123456,
    order_amount=1500.0,
    item_ids=["caesar", "pasta"]
)

# Проверяем баланс
print(f"Баллов: {card.loyalty_points}")
print(f"Всего заказов: {card.total_orders}")
print(f"Потрачено: {card.total_spent}₽")
```

### 📅 Модуль бронирования

Управление бронированиями:

```python
from horecabot.modules import BookingModule, BookingType, Resource
from datetime import date, time

# Создаем модуль бронирования
booking = BookingModule()

# Добавляем столики
for i in range(1, 11):
    table = Resource(
        id=f"table_{i}",
        name=f"Столик №{i}",
        resource_type=BookingType.TABLE,
        capacity=4
    )
    booking.add_resource(table)

# Настраиваем рабочие часы
booking.set_working_hours(
    opening=time(10, 0),
    closing=time(22, 0),
    slot_duration=60  # слоты по 1 часу
)

# Получаем доступные слоты
today = date.today()
available_slots = booking.get_available_slots(today)

# Создаем бронирование
from horecabot.modules import TimeSlot
slot = TimeSlot(start_time=time(18, 0), end_time=time(19, 0))

reservation = booking.create_booking(
    user_id=123456,
    user_name="Иван Иванов",
    user_phone="+79991234567",
    booking_type=BookingType.TABLE,
    booking_date=today,
    guests_count=4,
    time_slot=slot,
    special_requests="Столик у окна, день рождения"
)
```

## Веб-аналитика

HorecaBot включает встроенную веб-панель для аналитики и управления:

```python
from horecabot import RestaurantBot
from horecabot.web import create_analytics_app
import threading

# Создаем бота
bot = RestaurantBot(
    token="YOUR_TOKEN",
    name="Ресторан Премиум"
)

# Создаем веб-панель
app = create_analytics_app(
    bot_instance=bot,
    admin_login="admin",
    admin_password="secure_password_123"
)

# Запускаем веб-сервер в отдельном потоке
def run_web():
    app.run(host="0.0.0.0", port=5000)

web_thread = threading.Thread(target=run_web)
web_thread.daemon = True
web_thread.start()

# Запускаем бота
bot.run()
```

Панель будет доступна по адресу: `http://localhost:5000`

### Возможности веб-панели

- 📊 **Дашборд** — ключевые метрики (гости, заказы, выручка)
- 👥 **База гостей** — полная информация о каждом клиенте
- 📋 **Управление меню** — популярные позиции и рейтинги
- 📅 **Бронирования** — список всех броней на сегодня
- 📈 **Экспорт данных** — выгрузка в CSV и Excel

## Примеры использования

### Полный пример для ресторана

См. файл: `examples/restaurant_example.py`

### Полный пример для отеля

См. файл: `examples/hotel_example.py`

### Пример с квизом для бара

См. файл: `examples/bar_quiz_example.py`

## Документация

Полная документация доступна в папке `docs/`:

- [Архитектура библиотеки](docs/ARCHITECTURE.md)
- [Руководство по модулям](docs/MODULES.md)
- [API Reference](docs/API.md)
- [Развертывание](docs/DEPLOYMENT.md)
- [Интеграции](docs/INTEGRATIONS.md)

## Технические детали

### Архитектура

- **Асинхронность**: asyncio + aiohttp для высокой производительности
- **База данных**: SQLite (малые проекты) / PostgreSQL (крупные заведения)
- **Кэширование**: Redis для меню и частых запросов
- **Типизация**: Полная поддержка type hints

### Производительность

- Поддержка тысяч одновременных пользователей
- Long polling для получения обновлений
- Оптимизированные запросы к БД

## Лицензия

MIT License — см. файл [LICENSE](LICENSE)

## Поддержка

- 📧 Email: support@horecabot.ru
- 💬 Telegram: [@horecabot_support](https://t.me/horecabot_support)
- 🐛 Issues: [GitHub Issues](https://github.com/Slava47/telegram-bot-easy/issues)

## Авторы

HorecaBot Team

---

**Создано с ❤️ для индустрии гостеприимства**
