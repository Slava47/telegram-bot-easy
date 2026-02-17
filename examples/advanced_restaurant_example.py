"""
Improved Restaurant Example with Proper Callback Handling
==========================================================

Demonstrates:
- Advanced inline button handling
- Callback routing with patterns
- State management
- Error handling
- Input validation
"""

import os
import asyncio
from horecabot import RestaurantBot
from horecabot.modules import (
    MenuModule, MenuItem,
    OrderModule,
    LoyaltyModule, LoyaltyType
)
from horecabot.core.states import StateManager, UserState
from horecabot.core.callbacks import CallbackRouter, CallbackBuilder
from horecabot.core.validation import (
    validate_phone, validate_integer,
    sanitize_input, ErrorHandler, ErrorType
)
from horecabot.core.i18n import I18n, Language


def create_advanced_bot():
    """Create an advanced restaurant bot with proper callback handling"""
    
    # Get token
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Create bot
    bot = RestaurantBot(
        token=TOKEN,
        name="Ресторан Премиум",
        timezone="Europe/Moscow",
        currency="₽"
    )
    
    # Initialize modules
    menu = MenuModule(enable_cache=True)
    orders = OrderModule()
    loyalty = LoyaltyModule(loyalty_type=LoyaltyType.POINTS, points_per_ruble=0.05)
    
    # State manager
    state_manager = StateManager(default_timeout=1800)
    
    # Callback router
    router = CallbackRouter()
    
    # I18n
    i18n = I18n(Language.RU)
    
    # ========================================
    # Setup Menu
    # ========================================
    menu.add_category("appetizers", "Закуски", emoji="🥗")
    menu.add_category("main", "Основные блюда", emoji="🍝")
    menu.add_category("desserts", "Десерты", emoji="🍰")
    
    # Add items
    menu.add_item(MenuItem(
        id="caesar",
        name="Цезарь с курицей",
        description="Классический салат с пармезаном и соусом",
        price=450.0,
        category="appetizers",
        tags=["салат", "курица", "легкое"],
        photo_url="https://example.com/caesar.jpg"
    ))
    
    menu.add_item(MenuItem(
        id="pasta_carbonara",
        name="Паста Карбонара",
        description="Паста со сливочным соусом и беконом",
        price=650.0,
        category="main",
        tags=["паста", "сливочный", "сытное"]
    ))
    
    # ========================================
    # Command Handlers
    # ========================================
    
    @bot.command('start')
    async def start_command(update):
        """Start command handler"""
        user_id = update['message']['from']['id']
        user_name = update['message']['from'].get('first_name', 'Гость')
        chat_id = update['message']['chat']['id']
        
        # Reset state
        state_manager.reset_state(user_id)
        
        # Create guest card if doesn't exist
        if not loyalty.get_guest_card(user_id):
            loyalty.create_guest_card(
                user_id=user_id,
                name=user_name
            )
        
        # Welcome message
        text = f"""
🍽 <b>Добро пожаловать в {bot.name}!</b>

Здесь вы можете:
• Посмотреть меню и сделать заказ
• Забронировать столик
• Узнать о программе лояльности

Выберите действие:
"""
        
        keyboard = bot.create_inline_keyboard([
            [{"text": "📋 Меню", "callback_data": CallbackBuilder.build("view", "menu")}],
            [{"text": "🛒 Моя корзина", "callback_data": CallbackBuilder.build("view", "cart")}],
            [{"text": "👤 Профиль", "callback_data": CallbackBuilder.build("view", "profile")}]
        ])
        
        await bot.send_message(chat_id, text, reply_markup=keyboard)
    
    # ========================================
    # Callback Handlers with Router
    # ========================================
    
    # Middleware for logging
    @router.use_middleware
    async def logging_middleware(update, context):
        """Log all callbacks"""
        callback_data = update['callback_query']['data']
        user_id = update['callback_query']['from']['id']
        print(f"[Callback] User {user_id}: {callback_data}")
        return True  # Continue processing
    
    # Error handler
    @router.on_error
    async def handle_callback_error(update, error):
        """Handle callback errors"""
        callback_query_id = update['callback_query']['id']
        await bot.answer_callback_query(
            callback_query_id,
            text="Произошла ошибка. Попробуйте еще раз.",
            show_alert=True
        )
    
    # View menu
    @router.callback("view:menu")
    async def view_menu(update, callback_data):
        """Show menu categories"""
        chat_id = update['callback_query']['message']['chat']['id']
        message_id = update['callback_query']['message']['message_id']
        
        text = "<b>📋 Наше меню</b>\n\nВыберите категорию:"
        
        buttons = []
        for cat_id, cat_name in menu.categories.items():
            buttons.append([{
                "text": cat_name,
                "callback_data": CallbackBuilder.build("view", "category", cat_id)
            }])
        
        buttons.append([{
            "text": "◀️ Назад",
            "callback_data": CallbackBuilder.build("navigate", "main")
        }])
        
        keyboard = bot.create_inline_keyboard(buttons)
        await bot.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
    
    # View category
    @router.callback("view:category:*")
    async def view_category(update, callback_data):
        """Show items in category"""
        chat_id = update['callback_query']['message']['chat']['id']
        message_id = update['callback_query']['message']['message_id']
        category_id = callback_data.id
        
        items = menu.get_category_items(category_id)
        category_name = menu.categories.get(category_id, "Категория")
        
        text = f"<b>{category_name}</b>\n\n"
        
        buttons = []
        for item in items:
            text += f"• {item.name} - {item.price}{bot.currency}\n"
            text += f"  <i>{item.description}</i>\n\n"
            
            buttons.append([{
                "text": f"👁 {item.name}",
                "callback_data": CallbackBuilder.build("view", "item", item.id)
            }])
        
        buttons.append([{
            "text": "◀️ К категориям",
            "callback_data": CallbackBuilder.build("view", "menu")
        }])
        
        keyboard = bot.create_inline_keyboard(buttons)
        await bot.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
    
    # View item
    @router.callback_pattern(r"view:item:(.+)")
    async def view_item(update, match):
        """Show item details"""
        chat_id = update['callback_query']['message']['chat']['id']
        message_id = update['callback_query']['message']['message_id']
        item_id = match.group(1)
        
        item = menu.get_item(item_id)
        if not item:
            await bot.answer_callback_query(
                update['callback_query']['id'],
                text="Блюдо не найдено",
                show_alert=True
            )
            return
        
        text = f"""
<b>{item.name}</b>

{item.description}

💰 Цена: {item.price}{bot.currency}
⚖️ Вес: {item.weight or 'не указан'}
🔥 Калории: {item.calories or 'не указаны'}
⏱ Время приготовления: {item.cooking_time or '?'} мин
"""
        
        if item.allergens:
            text += f"\n⚠️ Аллергены: {', '.join(item.allergens)}"
        
        buttons = [
            [{
                "text": "➕ Добавить в корзину",
                "callback_data": CallbackBuilder.build("add", "cart", item_id)
            }],
            [{
                "text": "◀️ Назад",
                "callback_data": CallbackBuilder.build("view", "category", item.category)
            }]
        ]
        
        keyboard = bot.create_inline_keyboard(buttons)
        
        # Send with photo if available
        if item.photo_url:
            # Delete old message and send new with photo
            await bot.send_photo(
                chat_id,
                item.photo_url,
                caption=text,
                reply_markup=keyboard
            )
        else:
            await bot.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
    
    # Add to cart
    @router.callback("add:cart:*")
    async def add_to_cart(update, callback_data):
        """Add item to cart"""
        user_id = update['callback_query']['from']['id']
        item_id = callback_data.id
        
        item = menu.get_item(item_id)
        if not item:
            await bot.answer_callback_query(
                update['callback_query']['id'],
                text="Блюдо не найдено",
                show_alert=True
            )
            return
        
        # Get or create cart
        cart = orders.get_cart(user_id)
        if not cart:
            cart = orders.create_order(user_id)
        
        # Add item
        cart.add_item(item, quantity=1)
        
        # Show notification
        await bot.answer_callback_query(
            update['callback_query']['id'],
            text=f"✅ {item.name} добавлен в корзину"
        )
    
    # View cart
    @router.callback("view:cart")
    async def view_cart(update, callback_data):
        """Show shopping cart"""
        chat_id = update['callback_query']['message']['chat']['id']
        message_id = update['callback_query']['message']['message_id']
        user_id = update['callback_query']['from']['id']
        
        cart = orders.get_cart(user_id)
        
        if not cart or len(cart.items) == 0:
            text = "🛒 Ваша корзина пуста\n\nДобавьте блюда из меню!"
            
            keyboard = bot.create_inline_keyboard([[{
                "text": "📋 К меню",
                "callback_data": CallbackBuilder.build("view", "menu")
            }]])
        else:
            text = "<b>🛒 Ваша корзина:</b>\n\n"
            
            for idx, item in enumerate(cart.items):
                text += f"{idx + 1}. {item.menu_item.name} x{item.quantity}\n"
                text += f"   {item.total_price}{bot.currency}\n\n"
            
            text += f"<b>Итого: {cart.subtotal}{bot.currency}</b>"
            
            buttons = [
                [{
                    "text": "✅ Оформить заказ",
                    "callback_data": CallbackBuilder.build("confirm", "order", cart.id)
                }],
                [{
                    "text": "🗑 Очистить корзину",
                    "callback_data": CallbackBuilder.build("clear", "cart")
                }],
                [{
                    "text": "◀️ Назад",
                    "callback_data": CallbackBuilder.build("navigate", "main")
                }]
            ]
            keyboard = bot.create_inline_keyboard(buttons)
        
        await bot.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
    
    # View profile
    @router.callback("view:profile")
    async def view_profile(update, callback_data):
        """Show user profile"""
        chat_id = update['callback_query']['message']['chat']['id']
        message_id = update['callback_query']['message']['message_id']
        user_id = update['callback_query']['from']['id']
        
        card = loyalty.get_guest_card(user_id)
        
        if not card:
            text = "Профиль не найден"
        else:
            text = f"""
<b>👤 Ваш профиль</b>

Имя: {card.name}
Телефон: {card.phone or 'не указан'}

<b>💎 Программа лояльности:</b>
Баллов: {card.loyalty_points}
Уровень: {card.loyalty_level}

<b>📊 Статистика:</b>
Заказов: {card.total_orders}
Потрачено: {card.total_spent}{bot.currency}
"""
        
        keyboard = bot.create_inline_keyboard([[{
            "text": "◀️ Назад",
            "callback_data": CallbackBuilder.build("navigate", "main")
        }]])
        
        await bot.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
    
    # Navigate to main
    @router.callback("navigate:main")
    async def navigate_main(update, callback_data):
        """Return to main menu"""
        # Просто вызываем start
        await start_command(update)
    
    # ========================================
    # Process callbacks through router
    # ========================================
    
    @bot.on_callback('*')
    async def process_all_callbacks(update):
        """Route all callbacks through the router"""
        await router.route(update, bot)
    
    # ========================================
    # Attach modules to bot
    # ========================================
    bot.menu_module = menu
    bot.order_module = orders
    bot.loyalty_module = loyalty
    
    return bot


def main():
    """Main function"""
    bot = create_advanced_bot()
    
    print("="*50)
    print("🚀 Advanced Restaurant Bot Started!")
    print("="*50)
    print("Features:")
    print("  ✓ Proper callback routing")
    print("  ✓ State management")
    print("  ✓ Error handling")
    print("  ✓ Menu caching")
    print("  ✓ Loyalty program")
    print("="*50)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")


if __name__ == "__main__":
    main()
