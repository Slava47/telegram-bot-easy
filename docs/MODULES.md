# Руководство по модулям HorecaBot

## Обзор

HorecaBot построен на модульной архитектуре, где каждый модуль отвечает за определенную функциональность. Модули можно использовать независимо или комбинировать для создания полнофункционального бота.

## Основные модули

### 1. Модуль меню (`MenuModule`)

**Назначение:** Управление меню, категориями блюд и позициями.

**Основные возможности:**
- Создание категорий меню
- Добавление/удаление позиций
- Управление доступностью блюд
- Поиск по тегам
- Кэширование для быстрого доступа

**Пример использования:**

```python
from horecabot.modules import MenuModule, MenuItem

# Создание модуля с кэшированием
menu = MenuModule(enable_cache=True)

# Добавление категорий
menu.add_category("appetizers", "Закуски", emoji="🥗")
menu.add_category("main", "Основные блюда", emoji="🍝")
menu.add_category("desserts", "Десерты", emoji="🍰")

# Добавление позиции
item = MenuItem(
    id="caesar_salad",
    name="Цезарь с курицей",
    description="Классический салат с романо, курицей гриль, пармезаном",
    price=450.0,
    category="appetizers",
    weight="250г",
    calories=320,
    allergens=["глютен", "молоко", "яйца"],
    cooking_time=10,
    tags=["салат", "курица", "легкое"],
    photo_url="https://example.com/caesar.jpg",
    available=True
)
menu.add_item(item)

# Получение позиции
caesar = menu.get_item("caesar_salad")

# Получение всех позиций категории
appetizers = menu.get_category_items("appetizers")

# Поиск по тегам (для квизов)
light_dishes = menu.search_by_tags(["легкое", "свежее"], limit=3)

# Управление доступностью
menu.set_item_availability("caesar_salad", available=False)
```

**Кэширование:**

MenuModule автоматически кэширует данные при включенной опции `enable_cache=True`. Кэш автоматически инвалидируется при изменении данных.

```python
# Получить кэшированное меню
cached_menu = menu.get_cached_menu()

# Принудительно закэшировать полное меню
menu.cache_full_menu()
```

---

### 2. Модуль заказов (`OrderModule`)

**Назначение:** Управление заказами, корзиной покупок и историей заказов.

**Основные возможности:**
- Создание и управление заказами
- Корзина покупок
- История заказов пользователя
- Отмена заказов
- Различные типы доставки

**Пример использования:**

```python
from horecabot.modules import OrderModule

orders = OrderModule()

# Создание заказа (корзины)
order = orders.create_order(user_id=123456)

# Добавление позиций
order.add_item(menu_item, quantity=2)
order.add_item(another_item, quantity=1, comment="Без лука")

# Установка типа доставки
order.delivery_type = "delivery"  # delivery, pickup, dine_in
order.delivery_address = "ул. Ленина, д. 10, кв. 5"
order.delivery_cost = 200.0

# Подсчет суммы
subtotal = order.subtotal  # Без доставки
total = order.total  # С доставкой

# Подтверждение заказа
orders.confirm_order(order.id)

# Отмена заказа
success, error = orders.cancel_order(
    order.id,
    reason="Изменились планы"
)

if not success:
    print(f"Не удалось отменить: {error}")

# Получение активных заказов пользователя
active_orders = orders.get_user_active_orders(user_id=123456)

# История заказов (последние 10)
history = orders.get_order_history(user_id=123456, limit=10)

# Обновление статуса
orders.update_order_status(order.id, "ready")
```

**Статусы заказов:**
- `new` - Новый заказ
- `confirmed` - Подтвержден
- `cooking` - Готовится
- `ready` - Готов
- `delivered` - Доставлен
- `cancelled` - Отменен

---

### 3. Модуль квизов (`QuizModule`)

**Назначение:** Интерактивные квизы для подбора блюд и напитков на основе предпочтений.

**Основные возможности:**
- Создание многошаговых квизов
- Система тегов для подбора
- Кэширование результатов
- Статистика прохождения

**Пример использования:**

```python
from horecabot.modules import QuizModule, Quiz, QuizQuestion

# Создание модуля
quiz_module = QuizModule(menu_module=menu, enable_cache=True)

# Создание квиза
quiz = Quiz(
    id="main_dish_quiz",
    name="Подбери своё блюдо 🍽",
    description="Ответь на 3 вопроса и получи персональные рекомендации",
    category="main"
)

# Добавление вопросов
q1 = QuizQuestion(id="q1", text="Что вы предпочитаете?")
q1.add_answer("🥩 Мясо", ["мясо", "сытное"])
q1.add_answer("🐟 Рыбу", ["рыба", "легкое"])
q1.add_answer("🥬 Овощи", ["вегетарианское", "легкое"])
quiz.add_question(q1)

q2 = QuizQuestion(id="q2", text="Какой способ приготовления?")
q2.add_answer("🔥 Гриль", ["гриль"])
q2.add_answer("🍳 Сковорода", ["жареное"])
q2.add_answer("🥘 Тушение", ["тушеное"])
quiz.add_question(q2)

quiz_module.add_quiz(quiz)

# Начало квиза для пользователя
session = quiz_module.start_quiz(user_id=123456, quiz_id="main_dish_quiz")

# Получение текущего вопроса
question = quiz_module.get_current_question(user_id=123456)

# Ответ на вопрос
continues = quiz_module.answer_question(
    user_id=123456,
    tags=["мясо", "сытное"]
)

if not continues:  # Квиз завершен
    # Получение рекомендаций
    recommendations = quiz_module.get_recommendations(
        user_id=123456,
        limit=3
    )
    
    for item in recommendations:
        print(f"{item.name} - {item.price}₽")

# Статистика
stats = quiz_module.get_quiz_stats("main_dish_quiz")
print(f"Пройдено {stats['total_completions']} раз")
print(f"Среднее время: {stats.get('avg_completion_time', 0):.1f} сек")
```

---

### 4. Модуль лояльности (`LoyaltyModule`)

**Назначение:** Карточки гостей и программы лояльности.

**Типы программ:**
- **POINTS** - Балльная система (кэшбэк)
- **STAMPS** - Штампы (6-й кофе бесплатно)
- **LEVELS** - Уровневая система (Bronze, Silver, Gold, Platinum)

**Пример использования:**

```python
from horecabot.modules import LoyaltyModule, LoyaltyType

# Балльная программа (5% кэшбэк)
loyalty = LoyaltyModule(
    loyalty_type=LoyaltyType.POINTS,
    points_per_ruble=0.05
)

# Создание карточки гостя
card = loyalty.create_guest_card(
    user_id=123456,
    name="Иван Иванов",
    phone="+79991234567",
    email="ivan@example.com"
)

# Обработка заказа (начисление баллов)
loyalty.process_order(
    user_id=123456,
    order_amount=1500.0,
    item_ids=["item1", "item2", "item3"]
)

# Получение карточки
card = loyalty.get_guest_card(123456)
print(f"Баллов: {card.loyalty_points}")
print(f"Заказов: {card.total_orders}")
print(f"Потрачено: {card.total_spent}₽")
print(f"Уровень: {card.loyalty_level}")

# Использование баллов
success = card.spend_points(200)

# Топ гостей
top_guests = loyalty.get_top_guests(limit=10)
```

**Пример программы со штампами:**

```python
# 6-й кофе бесплатно
loyalty = LoyaltyModule(
    loyalty_type=LoyaltyType.STAMPS,
    stamps_for_reward=6
)

# Обработка заказа (добавление штампа)
loyalty.process_order(user_id=123456, order_amount=250.0, item_ids=["coffee"])

# Проверка доступности награды
if loyalty.check_reward_available(123456):
    # Получение награды
    success = loyalty.claim_reward(123456)
```

---

### 5. Модуль бронирования (`BookingModule`)

**Назначение:** Управление бронированием столиков, номеров, VIP-зон.

**Типы ресурсов:**
- `TABLE` - Столики в ресторане/кафе
- `ROOM` - Номера в отеле
- `VIP_ZONE` - VIP-зоны в баре/клубе

**Пример использования:**

```python
from horecabot.modules import BookingModule, BookingType, Resource, TimeSlot
from datetime import date, time

booking = BookingModule()

# Добавление ресурсов (столиков)
for i in range(1, 11):
    table = Resource(
        id=f"table_{i}",
        name=f"Столик №{i}",
        resource_type=BookingType.TABLE,
        capacity=4,
        features=["у окна"] if i <= 3 else []
    )
    booking.add_resource(table)

# Настройка рабочего времени
booking.set_working_hours(
    opening=time(10, 0),
    closing=time(23, 0),
    slot_duration=60  # Слоты по 60 минут
)

# На сколько дней вперед можно бронировать
booking.booking_depth_days = 30

# Получение доступных слотов
today = date.today()
available_slots = booking.get_available_slots(today)

# Создание бронирования
reservation = booking.create_booking(
    user_id=123456,
    user_name="Иван Иванов",
    user_phone="+79991234567",
    booking_type=BookingType.TABLE,
    booking_date=today,
    guests_count=4,
    time_slot=available_slots[0],
    special_requests="Столик у окна, день рождения"
)

# Подтверждение
booking.confirm_booking(reservation.id)

# Получение бронирований пользователя
user_bookings = booking.get_user_bookings(user_id=123456, active_only=True)

# Получение всех бронирований на дату
today_bookings = booking.get_bookings_by_date(today)

# Отмена
booking.cancel_booking(reservation.id)
```

---

## Вспомогательные модули

### Управление состояниями (`StateManager`)

Отслеживание состояния пользователя в диалоге для многошаговых процессов.

```python
from horecabot.core.states import StateManager, UserState

state_manager = StateManager(default_timeout=1800)  # 30 минут

# Установка состояния
state_manager.set_state(
    user_id=123456,
    state=UserState.BROWSING_MENU,
    category="main"
)

# Обновление контекста
state_manager.update_context(
    user_id=123456,
    selected_item="pizza_123"
)

# Получение состояния
state = state_manager.get_state(123456)

# Получение контекста
context = state_manager.get_context(123456)
category = context.get_data("category")

# Возврат к предыдущему состоянию
state_manager.go_back(123456)
```

### Валидация ввода

```python
from horecabot.core.validation import (
    validate_phone, validate_email,
    validate_date, validate_integer
)

# Валидация телефона
valid, error = validate_phone("+79991234567")
if not valid:
    await bot.send_message(chat_id, f"Ошибка: {error}")

# Валидация даты
valid, error, date_obj = validate_date("25.12.2024")

# Валидация количества
valid, error, count = validate_integer("5", min_value=1, max_value=10)
```

### Интернационализация

```python
from horecabot.core.i18n import I18n, Language

i18n = I18n(Language.RU)

# Установка языка пользователя
i18n.set_user_language(user_id=123456, language=Language.EN)

# Получение перевода
welcome_text = i18n.get("welcome", user_id=123456, name="Restaurant")
menu_text = i18n.get("menu", user_id=123456)
```

---

## Интеграция модулей

Модули легко интегрируются друг с другом:

```python
from horecabot import RestaurantBot
from horecabot.modules import (
    MenuModule, OrderModule,
    QuizModule, LoyaltyModule, BookingModule
)

# Создание бота
bot = RestaurantBot(token="YOUR_TOKEN", name="Ресторан")

# Инициализация модулей
menu = MenuModule(enable_cache=True)
orders = OrderModule()
quiz = QuizModule(menu_module=menu)  # Связь с меню
loyalty = LoyaltyModule(loyalty_type=LoyaltyType.POINTS)
booking = BookingModule()

# Подключение к боту
bot.menu_module = menu
bot.order_module = orders
bot.quiz_module = quiz
bot.loyalty_module = loyalty
bot.booking_module = booking

# Теперь модули работают вместе
# - Квизы подбирают блюда из меню
# - Заказы используют позиции меню
# - Лояльность начисляет баллы за заказы
```

---

## Best Practices

### 1. Используйте кэширование

```python
# Включайте кэширование для меню и квизов
menu = MenuModule(enable_cache=True)
quiz = QuizModule(menu_module=menu, enable_cache=True)
```

### 2. Валидируйте пользовательский ввод

```python
from horecabot.core.validation import validate_phone, sanitize_input

# Очистка от опасных символов
clean_text = sanitize_input(user_input)

# Валидация телефона
valid, error = validate_phone(phone)
if not valid:
    # Сообщить об ошибке
```

### 3. Используйте состояния для сложных диалогов

```python
# Многошаговый процесс заказа
state_manager.set_state(user_id, UserState.BROWSING_MENU)
# ... выбор блюда
state_manager.set_state(user_id, UserState.IN_CART)
# ... оформление
state_manager.set_state(user_id, UserState.CHECKOUT)
```

### 4. Обрабатывайте ошибки

```python
from horecabot.core.validation import ValidationError, ErrorHandler

try:
    # Код, который может вызвать ошибку
    pass
except ValidationError as e:
    error_msg = ErrorHandler.handle_validation_error(e)
    await bot.send_message(chat_id, error_msg)
```

---

## Дополнительная информация

- [API Reference](API.md) - Полный справочник API
- [Примеры](../examples/) - Рабочие примеры кода
- [Архитектура](ARCHITECTURE.md) - Архитектура библиотеки

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
