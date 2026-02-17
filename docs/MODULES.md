# Руководство по модулям HorecaBot

## Оглавление

1. [MenuModule](#menumodule) — Меню и заказы
2. [BookingModule](#bookingmodule) — Бронирование
3. [QuizModule](#quizmodule) — Интерактивные квизы
4. [LoyaltyModule](#loyaltymodule) — Система лояльности

---

## MenuModule

### Описание

Модуль для управления меню ресторана, включая категории, позиции и заказы.

### Основные классы

#### MenuItem

Позиция меню с полной информацией о блюде или напитке.

```python
from horecabot.modules import MenuItem

item = MenuItem(
    id="caesar_salad",               # Уникальный ID
    name="Цезарь с курицей",         # Название
    description="Классический салат", # Описание
    price=450.0,                      # Цена
    category="salads",                # Категория
    photo_url="https://...",          # URL фото (опционально)
    weight="250г",                    # Вес/объем (опционально)
    calories=320,                     # Калорийность (опционально)
    allergens=["глютен", "яйца"],    # Аллергены (опционально)
    cooking_time=15,                  # Время приготовления (опционально)
    tags=["салат", "курица"],        # Теги для квизов
    available=True                    # Доступность
)
```

#### Order и OrderItem

Заказ и позиции в заказе.

```python
from horecabot.modules import Order, OrderItem

# Создание заказа
order = Order(
    id="order_123",
    user_id=123456,
    delivery_type="delivery",  # delivery, pickup, dine_in
    delivery_address="ул. Ленина, 10"
)

# Добавление позиций
order.add_item(item, quantity=2, comment="Без майонеза")

# Стоимость
print(f"Сумма: {order.subtotal}₽")
print(f"Доставка: {order.delivery_cost}₽")
print(f"Итого: {order.total}₽")
```

### MenuModule API

#### Создание и настройка

```python
from horecabot.modules import MenuModule

menu = MenuModule()

# Добавить категорию
menu.add_category(
    category_id="appetizers",
    name="Закуски",
    emoji="🥗"
)

# Добавить позицию
menu.add_item(item)
```

#### Получение данных

```python
# Получить позицию по ID
item = menu.get_item("caesar_salad")

# Получить все позиции категории
items = menu.get_category_items("appetizers")

# Поиск по тегам (для квизов)
results = menu.search_by_tags(
    tags=["салат", "курица"],
    limit=3
)
```

#### Управление доступностью

```python
# Сделать блюдо недоступным
menu.set_item_availability("caesar_salad", False)

# Вернуть в меню
menu.set_item_availability("caesar_salad", True)
```

### OrderModule API

```python
from horecabot.modules import OrderModule

orders = OrderModule()

# Создать корзину для пользователя
order = orders.create_order(user_id=123456)

# Получить активную корзину
cart = orders.get_cart(user_id=123456)

# Подтвердить заказ
orders.confirm_order(order.id)

# Получить историю заказов
history = orders.get_user_orders(user_id=123456)

# Обновить статус
orders.update_order_status(order.id, "cooking")
```

---

## BookingModule

### Описание

Модуль для бронирования столиков, номеров и других ресурсов.

### Основные классы

#### Booking

```python
from horecabot.modules import Booking, BookingType, TimeSlot
from datetime import date, time

booking = Booking(
    id="booking_123",
    user_id=123456,
    user_name="Иван Иванов",
    user_phone="+79991234567",
    booking_type=BookingType.TABLE,
    resource_id="table_5",
    booking_date=date(2024, 3, 15),
    guests_count=4,
    time_slot=TimeSlot(
        start_time=time(18, 0),
        end_time=time(19, 0)
    ),
    special_requests="У окна, день рождения"
)
```

#### Resource

```python
from horecabot.modules import Resource, BookingType

table = Resource(
    id="table_5",
    name="Столик №5",
    resource_type=BookingType.TABLE,
    capacity=4,
    features=["у окна", "возле камина"]
)

room = Resource(
    id="suite_301",
    name="Люкс 301",
    resource_type=BookingType.ROOM,
    capacity=2,
    price_per_night=5000.0,
    features=["вид на море", "балкон"]
)
```

### BookingModule API

#### Настройка

```python
from horecabot.modules import BookingModule
from datetime import time

booking = BookingModule()

# Добавить ресурсы
booking.add_resource(table)

# Настроить рабочие часы
booking.set_working_hours(
    opening=time(10, 0),
    closing=time(23, 0),
    slot_duration=60  # минуты
)

# Глубина бронирования
booking.booking_depth_days = 30
```

#### Создание бронирования

```python
from datetime import date

# Получить доступные слоты
today = date.today()
available = booking.get_available_slots(today)

# Создать бронирование
reservation = booking.create_booking(
    user_id=123456,
    user_name="Иван Иванов",
    user_phone="+79991234567",
    booking_type=BookingType.TABLE,
    booking_date=today,
    guests_count=4,
    time_slot=available[0],  # Первый доступный слот
    special_requests="У окна"
)
```

#### Управление бронированиями

```python
# Подтвердить
booking.confirm_booking(reservation.id)

# Отменить
booking.cancel_booking(reservation.id)

# Получить бронирования пользователя
user_bookings = booking.get_user_bookings(
    user_id=123456,
    active_only=True
)

# Получить все бронирования на дату
today_bookings = booking.get_bookings_by_date(today)
```

---

## QuizModule

### Описание

Модуль для создания интерактивных квизов для подбора блюд и напитков.

### Основные классы

#### Quiz и QuizQuestion

```python
from horecabot.modules import Quiz, QuizQuestion

# Создать квиз
quiz = Quiz(
    id="cocktail_quiz",
    name="Подбери свой коктейль 🍹",
    description="Ответь на 3 вопроса",
    category="drinks"  # опционально
)

# Создать вопрос
question = QuizQuestion(
    id="q1",
    text="Какой вкус предпочитаете?"
)

# Добавить варианты ответов
question.add_answer("🍬 Сладкий", ["sweet", "fruity"])
question.add_answer("🍋 Кислый", ["sour", "citrus"])
question.add_answer("☕ Горький", ["bitter", "strong"])

# Добавить вопрос в квиз
quiz.add_question(question)
```

### QuizModule API

#### Создание и управление

```python
from horecabot.modules import QuizModule

quiz_module = QuizModule(menu_module=menu)

# Добавить квиз
quiz_module.add_quiz(quiz)

# Получить квиз
quiz = quiz_module.get_quiz("cocktail_quiz")
```

#### Прохождение квиза

```python
# Начать квиз для пользователя
session = quiz_module.start_quiz(
    user_id=123456,
    quiz_id="cocktail_quiz"
)

# Получить текущий вопрос
question = quiz_module.get_current_question(user_id=123456)

# Ответить на вопрос
continues = quiz_module.answer_question(
    user_id=123456,
    tags=["sweet", "fruity"]
)

# Если квиз завершен
if not continues:
    # Получить рекомендации
    recommendations = quiz_module.get_recommendations(
        user_id=123456,
        limit=3
    )
    
    for item in recommendations:
        print(f"{item.name} - {item.price}₽")
```

#### Статистика

```python
# Количество пройденных квизов пользователем
count = quiz_module.get_user_quiz_count(user_id=123456)
```

---

## LoyaltyModule

### Описание

Модуль для управления программой лояльности и карточками гостей.

### Типы программ лояльности

```python
from horecabot.modules import LoyaltyType

# POINTS - накопительная балльная система
# STAMPS - система штампов (6-й кофе бесплатно)
# LEVELS - уровневая система (bronze, silver, gold, platinum)
```

### GuestCard

```python
from horecabot.modules import GuestCard

card = GuestCard(
    user_id=123456,
    name="Иван Иванов",
    phone="+79991234567",
    email="ivan@example.com"
)

# Статистика
print(f"Баллов: {card.loyalty_points}")
print(f"Уровень: {card.loyalty_level}")
print(f"Заказов: {card.total_orders}")
print(f"Потрачено: {card.total_spent}₽")
print(f"Квизов: {card.quiz_completions}")
```

### LoyaltyModule API

#### Создание программы

```python
from horecabot.modules import LoyaltyModule, LoyaltyType

# Балльная система
loyalty = LoyaltyModule(
    loyalty_type=LoyaltyType.POINTS,
    points_per_ruble=0.05  # 5% кэшбэк
)

# Система штампов
loyalty = LoyaltyModule(
    loyalty_type=LoyaltyType.STAMPS,
    stamps_for_reward=6  # Каждый 6-й бесплатно
)
```

#### Управление гостями

```python
# Создать карточку
card = loyalty.create_guest_card(
    user_id=123456,
    name="Иван Иванов",
    phone="+79991234567"
)

# Получить карточку
card = loyalty.get_guest_card(user_id=123456)
```

#### Обработка заказов

```python
# Обработать заказ (начислить баллы/штампы)
loyalty.process_order(
    user_id=123456,
    order_amount=1500.0,
    item_ids=["item1", "item2"]
)
```

#### Награды

```python
# Проверить доступность награды
if loyalty.check_reward_available(user_id=123456):
    # Получить награду
    success = loyalty.claim_reward(user_id=123456)
    if success:
        print("Награда получена!")
```

#### Статистика

```python
# Все гости
all_guests = loyalty.get_all_guests()

# Топ гостей по потраченной сумме
top_guests = loyalty.get_top_guests(limit=10)
```

---

## Интеграция модулей

### Пример полной интеграции

```python
from horecabot import RestaurantBot
from horecabot.modules import *

# Создать бота
bot = RestaurantBot(token="...", name="Ресторан")

# Настроить меню
menu = MenuModule()
bot.menu_module = menu
# ... добавить позиции

# Настроить заказы
orders = OrderModule()
bot.order_module = orders

# Настроить бронирование
booking = BookingModule()
bot.booking_module = booking
# ... добавить ресурсы

# Настроить квизы
quiz = QuizModule(menu_module=menu)
bot.quiz_module = quiz
# ... добавить квизы

# Настроить лояльность
loyalty = LoyaltyModule(loyalty_type=LoyaltyType.POINTS)
bot.loyalty_module = loyalty

# Запустить
bot.run()
```

---

## Заключение

Все модули работают независимо и могут быть использованы как вместе, так и по отдельности. Выбирайте только те модули, которые нужны для вашего типа заведения.
