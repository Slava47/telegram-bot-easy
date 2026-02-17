# API Reference - HorecaBot

## Core Modules

### Base Bot (`horecabot.core.base`)

#### HorecaBot

Base class for all bot types.

```python
from horecabot.core.base import HorecaBot, EstablishmentType

bot = HorecaBot(
    token="YOUR_BOT_TOKEN",
    name="My Establishment",
    timezone="Europe/Moscow",
    currency="₽",
    establishment_type=EstablishmentType.RESTAURANT
)
```

**Parameters:**
- `token` (str): Telegram bot token from @BotFather
- `name` (str): Name of your establishment
- `timezone` (str): Timezone string (e.g., "Europe/Moscow")
- `currency` (str): Currency symbol (e.g., "₽", "$", "€")
- `establishment_type` (EstablishmentType): Type of establishment

**Methods:**

##### `command(command_name: str)`

Decorator for registering command handlers.

```python
@bot.command('start')
async def start_handler(update):
    await bot.send_message(update['chat']['id'], "Welcome!")
```

##### `on_message(func: Callable)`

Decorator for registering text message handlers.

```python
@bot.on_message
async def message_handler(update):
    text = update['message']['text']
    # Handle message
```

##### `on_callback(callback_data: str)`

Decorator for registering callback query handlers.

```python
@bot.on_callback('menu_main')
async def show_main_menu(update):
    # Handle callback
```

##### `send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None, parse_mode: str = "HTML")`

Send a text message.

```python
await bot.send_message(
    chat_id=123456,
    text="<b>Hello!</b>",
    parse_mode="HTML"
)
```

##### `send_photo(chat_id: int, photo: str, caption: Optional[str] = None, reply_markup: Optional[Dict] = None)`

Send a photo message.

##### `create_inline_keyboard(buttons: List[List[Dict[str, str]]])`

Create an inline keyboard.

```python
keyboard = bot.create_inline_keyboard([
    [{"text": "Menu", "callback_data": "menu"}],
    [{"text": "Orders", "callback_data": "orders"}]
])
```

##### `run()`

Start the bot (blocking call).

```python
bot.run()
```

---

### State Management (`horecabot.core.states`)

#### StateManager

Manages user states for conversation flows.

```python
from horecabot.core.states import StateManager, UserState

state_manager = StateManager(default_timeout=1800)
```

**Methods:**

##### `set_state(user_id: int, state: UserState, timeout: Optional[int] = None, **context_data)`

Set user state with optional context data.

```python
state_manager.set_state(
    user_id=123456,
    state=UserState.BROWSING_MENU,
    category="main_dishes"
)
```

##### `get_state(user_id: int) -> UserState`

Get current user state.

```python
state = state_manager.get_state(123456)
```

##### `update_context(user_id: int, **data)`

Update context data for a user.

```python
state_manager.update_context(
    user_id=123456,
    item_id="pizza_123",
    quantity=2
)
```

##### `reset_state(user_id: int)`

Reset user state to IDLE.

##### `go_back(user_id: int) -> bool`

Go back to previous state.

#### UserState (Enum)

Available user states:
- `IDLE` - Default state
- `BROWSING_MENU` - Browsing menu
- `VIEWING_ITEM` - Viewing menu item
- `IN_CART` - In shopping cart
- `CHECKOUT` - Checkout process
- `BOOKING_START` - Starting booking
- `IN_QUIZ` - Taking quiz
- And more...

---

### Input Validation (`horecabot.core.validation`)

#### Validation Functions

##### `validate_phone(phone: str) -> Tuple[bool, Optional[str]]`

Validate phone number.

```python
valid, error = validate_phone("+79991234567")
if not valid:
    print(error)
```

##### `validate_email(email: str) -> Tuple[bool, Optional[str]]`

Validate email address.

##### `validate_date(date_str: str, date_format: str = "%d.%m.%Y") -> Tuple[bool, Optional[str], Optional[date]]`

Validate date string.

##### `validate_integer(value: str, min_value: Optional[int] = None, max_value: Optional[int] = None) -> Tuple[bool, Optional[str], Optional[int]]`

Validate integer with optional range check.

##### `validate_rating(rating: str) -> Tuple[bool, Optional[str], Optional[int]]`

Validate rating (1-5).

##### `sanitize_input(text: str) -> str`

Sanitize user input by removing HTML tags and control characters.

```python
clean_text = sanitize_input(user_input)
```

---

### Internationalization (`horecabot.core.i18n`)

#### I18n

Multi-language support.

```python
from horecabot.core.i18n import I18n, Language

i18n = I18n(Language.RU)

# Get translation
text = i18n.get("welcome", name="MyBot")

# Set user language
i18n.set_user_language(user_id=123456, language=Language.EN)

# Get user-specific translation
text = i18n.get("menu", user_id=123456)
```

**Supported Languages:**
- Russian (RU)
- English (EN)
- Spanish (ES)
- German (DE)
- French (FR)
- Italian (IT)
- Chinese (ZH)

---

### Menu Caching (`horecabot.core.cache`)

#### MenuCache

Cache system for menu items.

```python
from horecabot.core.cache import MenuCache

cache = MenuCache(ttl=300, max_size=1000)

# Set value
cache.set("menu:full", menu_data, ttl=600)

# Get value
menu = cache.get("menu:full")

# Clear cache
cache.clear()

# Get stats
stats = cache.get_stats()
```

#### SmartMenuCache

Cache with automatic invalidation.

```python
from horecabot.core.cache import SmartMenuCache

cache = SmartMenuCache(ttl=300)

# Set with dependencies
cache.set_with_dependencies(
    key="item:123",
    value=item_data,
    depends_on=["category:main"]
)

# Invalidate (automatically invalidates dependents)
cache.invalidate("category:main")
```

---

## Module Classes

### Menu Module (`horecabot.modules.menu`)

#### MenuModule

Manage menu, categories, and items.

```python
from horecabot.modules import MenuModule, MenuItem

menu = MenuModule(enable_cache=True)

# Add category
menu.add_category("main", "Main Dishes", emoji="🍝")

# Add item
item = MenuItem(
    id="pasta_carbonara",
    name="Pasta Carbonara",
    description="Creamy pasta with bacon",
    price=650.0,
    category="main",
    tags=["pasta", "italian"]
)
menu.add_item(item)

# Get item
item = menu.get_item("pasta_carbonara")

# Search by tags
results = menu.search_by_tags(["pasta", "italian"], limit=3)
```

#### OrderModule

Manage orders and shopping carts.

```python
from horecabot.modules import OrderModule

orders = OrderModule()

# Create order
order = orders.create_order(user_id=123456)
order.add_item(menu_item, quantity=2)

# Confirm order
orders.confirm_order(order.id)

# Cancel order
success, error = orders.cancel_order(order.id, reason="Customer request")

# Get user orders
user_orders = orders.get_user_orders(user_id=123456)
```

---

### Quiz Module (`horecabot.modules.quiz`)

#### QuizModule

Interactive quiz for item recommendations.

```python
from horecabot.modules import QuizModule, Quiz, QuizQuestion

quiz_module = QuizModule(menu_module=menu)

# Create quiz
quiz = Quiz(
    id="main_dish_quiz",
    name="Find Your Dish",
    description="Answer 3 questions"
)

# Add question
q1 = QuizQuestion(id="q1", text="What do you prefer?")
q1.add_answer("Meat", ["meat", "hearty"])
q1.add_answer("Fish", ["fish", "light"])
quiz.add_question(q1)

quiz_module.add_quiz(quiz)

# Start quiz
session = quiz_module.start_quiz(user_id=123456, quiz_id="main_dish_quiz")

# Answer question
continues = quiz_module.answer_question(user_id=123456, tags=["meat", "hearty"])

# Get recommendations
recommendations = quiz_module.get_recommendations(user_id=123456, limit=3)
```

---

### Loyalty Module (`horecabot.modules.loyalty`)

#### LoyaltyModule

Guest cards and loyalty programs.

```python
from horecabot.modules import LoyaltyModule, LoyaltyType

loyalty = LoyaltyModule(
    loyalty_type=LoyaltyType.POINTS,
    points_per_ruble=0.05  # 5% cashback
)

# Create guest card
card = loyalty.create_guest_card(
    user_id=123456,
    name="John Doe",
    phone="+79991234567"
)

# Process order (add points)
loyalty.process_order(
    user_id=123456,
    order_amount=1000.0,
    item_ids=["item1", "item2"]
)

# Get card
card = loyalty.get_guest_card(123456)
print(f"Points: {card.loyalty_points}")

# Top guests
top_guests = loyalty.get_top_guests(limit=10)
```

**Loyalty Types:**
- `LoyaltyType.POINTS` - Points-based system
- `LoyaltyType.STAMPS` - Stamp-based (e.g., 6th coffee free)
- `LoyaltyType.LEVELS` - Level-based with tiers

---

### Booking Module (`horecabot.modules.booking`)

#### BookingModule

Manage table/room bookings.

```python
from horecabot.modules import BookingModule, BookingType, Resource
from datetime import date, time

booking = BookingModule()

# Add resource
table = Resource(
    id="table_1",
    name="Table 1",
    resource_type=BookingType.TABLE,
    capacity=4,
    features=["window view"]
)
booking.add_resource(table)

# Set working hours
booking.set_working_hours(
    opening=time(10, 0),
    closing=time(22, 0),
    slot_duration=60
)

# Get available slots
today = date.today()
slots = booking.get_available_slots(today)

# Create booking
reservation = booking.create_booking(
    user_id=123456,
    user_name="John Doe",
    user_phone="+79991234567",
    booking_type=BookingType.TABLE,
    booking_date=today,
    guests_count=4,
    time_slot=slots[0]
)

# Confirm booking
booking.confirm_booking(reservation.id)

# Cancel booking
booking.cancel_booking(reservation.id)
```

---

## Establishment Types

### RestaurantBot

```python
from horecabot import RestaurantBot

bot = RestaurantBot(
    token="YOUR_TOKEN",
    name="My Restaurant",
    enable_delivery=True,
    enable_booking=True,
    enable_reviews=True
)
```

### HotelBot

```python
from horecabot import HotelBot

bot = HotelBot(
    token="YOUR_TOKEN",
    name="My Hotel",
    enable_concierge=True,
    enable_spa=True
)
```

### CafeBot

```python
from horecabot import CafeBot

bot = CafeBot(
    token="YOUR_TOKEN",
    name="My Cafe",
    loyalty_program="stamps"
)
```

### BarBot

```python
from horecabot import BarBot

bot = BarBot(
    token="YOUR_TOKEN",
    name="My Bar",
    enable_hookah=True,
    age_limit=18
)
```

### FastFoodBot

```python
from horecabot import FastFoodBot

bot = FastFoodBot(
    token="YOUR_TOKEN",
    name="My FastFood",
    enable_drive_through=True
)
```

---

## Error Handling

```python
from horecabot.core.validation import ValidationError, ErrorHandler, ErrorType

try:
    # Your code
    pass
except ValidationError as e:
    message = ErrorHandler.handle_validation_error(e)
    await bot.send_message(chat_id, message)

# Format custom error
error_msg = ErrorHandler.format_error(
    ErrorType.TIMEOUT,
    details="Please try again"
)
```

---

## Telegram API Wrapper

```python
from horecabot.core.telegram_api import TelegramAPIWrapper

api = TelegramAPIWrapper(
    token="YOUR_TOKEN",
    timeout=30,
    max_retries=3
)

# Automatic retry and timeout handling
result = await api.send_message(
    chat_id=123456,
    text="Hello!",
    reply_markup=keyboard
)
```

---

## Examples

See the `examples/` directory for complete working examples:
- `restaurant_example.py` - Full restaurant bot
- `hotel_example.py` - Hotel bot
- `cafe_example.py` - Cafe bot
- `bar_quiz_example.py` - Bar with quiz

---

## Testing

Run tests:

```bash
python -m unittest discover tests
```

Run specific test:

```bash
python -m unittest tests.test_states
```
