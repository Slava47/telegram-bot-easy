"""
Класс CafeBot для кафе и кофеен
================================

Оптимизирован под быстрые заказы и программы лояльности.
"""

from horecabot.core.base import HorecaBot, EstablishmentType


class CafeBot(HorecaBot):
    """
    Специализированный бот для кафе и кофеен.
    
    Функционал:
    - Упрощенное меню (напитки, десерты, выпечка)
    - Система накопления бонусов (например, 6-й кофе бесплатно)
    - Предзаказ с выбором времени забора
    - Push-уведомления о новинках и акциях
    
    Example:
        >>> bot = CafeBot(
        ...     token="YOUR_TOKEN",
        ...     name="Кофейня Аромат",
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
        loyalty_program: str = "stamps"  # stamps или points
    ):
        """
        Инициализация бота кафе.
        
        Args:
            token: Токен Telegram бота
            name: Название кафе
            timezone: Часовой пояс
            currency: Символ валюты
            loyalty_program: Тип программы лояльности (stamps - штампы, points - баллы)
        """
        super().__init__(
            token=token,
            name=name,
            timezone=timezone,
            currency=currency,
            establishment_type=EstablishmentType.CAFE
        )
        
        self.loyalty_program = loyalty_program
        self.logger.info(f"Инициализирован CafeBot: {name}")
        self.logger.info(f"  - Программа лояльности: {loyalty_program}")
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Настройка стандартных обработчиков для кафе"""
        
        @self.command('start')
        async def start_handler(update):
            chat_id = update['message']['chat']['id']
            user_name = update['message']['from'].get('first_name', 'Гость')
            
            welcome_text = (
                f"☕ <b>Добро пожаловать в {self.name}!</b>\n\n"
                f"Привет, {user_name}! 👋\n\n"
                f"Я помогу вам:\n"
                f"• ☕ Заказать кофе и десерты\n"
                f"• ⏰ Сделать предзаказ\n"
                f"• 🎁 Собирать бонусы\n"
                f"• 🆕 Узнавать о новинках\n\n"
                f"💡 Используйте меню ниже"
            )
            
            keyboard = self.get_main_menu_keyboard()
            await self.send_message(chat_id, welcome_text, reply_markup=keyboard)
    
    def get_main_menu_keyboard(self):
        """Получить главную клавиатуру кафе"""
        buttons = [
            [{"text": "☕ Меню", "callback_data": "cafe_menu"}],
            [{"text": "⏰ Предзаказ", "callback_data": "preorder"}],
            [{"text": "🎁 Мои бонусы", "callback_data": "loyalty"}],
            [{"text": "🆕 Новинки", "callback_data": "new_items"}],
            [{"text": "👤 Профиль", "callback_data": "profile"}]
        ]
        return self.create_inline_keyboard(buttons)
