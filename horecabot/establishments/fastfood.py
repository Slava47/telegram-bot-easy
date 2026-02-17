"""
Класс FastFoodBot для фастфуда
===============================

Оптимизирован для быстрого оформления заказов.
"""

from horecabot.core.base import HorecaBot, EstablishmentType


class FastFoodBot(HorecaBot):
    """
    Специализированный бот для фастфуда.
    
    Функционал:
    - Быстрый заказ в 3 клика
    - Комбо-предложения
    - Купоны на скидку
    - Отслеживание статуса заказа
    - Drive-Through заказы
    - Навигация для самовывоза
    
    Example:
        >>> bot = FastFoodBot(
        ...     token="YOUR_TOKEN",
        ...     name="БургерКинг",
        ...     timezone="Europe/Moscow",
        ...     currency="₽"
        ... )
        >>> bot.run()
    """
    
    def __init__(
        self,
        token: str,
        name: str,
        timezone: str = "Europe/Moscow",
        currency: str = "₽",
        enable_drive_through: bool = False
    ):
        """
        Инициализация бота фастфуда.
        
        Args:
            token: Токен Telegram бота
            name: Название заведения
            timezone: Часовой пояс
            currency: Символ валюты
            enable_drive_through: Включить Drive-Through
        """
        super().__init__(
            token=token,
            name=name,
            timezone=timezone,
            currency=currency,
            establishment_type=EstablishmentType.FASTFOOD
        )
        
        self.enable_drive_through = enable_drive_through
        
        self.logger.info(f"Инициализирован FastFoodBot: {name}")
        self.logger.info(f"  - Drive-Through: {'Да' if enable_drive_through else 'Нет'}")
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Настройка стандартных обработчиков для фастфуда"""
        
        @self.command('start')
        async def start_handler(update):
            chat_id = update['message']['chat']['id']
            user_name = update['message']['from'].get('first_name', 'Гость')
            
            welcome_text = (
                f"🍔 <b>Добро пожаловать в {self.name}!</b>\n\n"
                f"Привет, {user_name}! 🎉\n\n"
                f"⚡ Быстрый заказ за 3 клика:\n"
                f"• 🍔 Меню и комбо\n"
                f"• 🎟 Купоны и скидки\n"
                f"• 📍 Самовывоз или доставка\n"
                f"• 📊 Отслеживание заказа\n"
            )
            
            if self.enable_drive_through:
                welcome_text += "• 🚗 Drive-Through\n"
            
            welcome_text += "\n💡 Жми на кнопки ниже!"
            
            keyboard = self.get_main_menu_keyboard()
            await self.send_message(chat_id, welcome_text, reply_markup=keyboard)
    
    def get_main_menu_keyboard(self):
        """Получить главную клавиатуру фастфуда"""
        buttons = [
            [{"text": "🍔 Быстрый заказ", "callback_data": "quick_order"}],
            [{"text": "🎯 Комбо", "callback_data": "combo_deals"}],
            [{"text": "🎟 Купоны", "callback_data": "coupons"}],
            [{"text": "📍 Где забрать", "callback_data": "locations"}]
        ]
        
        if self.enable_drive_through:
            buttons.append([{"text": "🚗 Drive-Through", "callback_data": "drive_through"}])
        
        buttons.extend([
            [{"text": "📊 Мои заказы", "callback_data": "my_orders"}],
            [{"text": "👤 Профиль", "callback_data": "profile"}]
        ])
        
        return self.create_inline_keyboard(buttons)
