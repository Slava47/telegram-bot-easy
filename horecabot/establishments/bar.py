"""
Класс BarBot для баров и ночных клубов
=======================================

Специализированный функционал для баров.
"""

from horecabot.core.base import HorecaBot, EstablishmentType


class BarBot(HorecaBot):
    """
    Специализированный бот для бара/ночного клуба.
    
    Функционал:
    - Бронирование VIP-зон и столов с депозитом
    - Гостевой лист для входа
    - Афиша мероприятий и покупка билетов
    - Информация о дресс-коде и правилах
    - Кальянное меню
    - Бутылочный сервис
    
    Example:
        >>> bot = BarBot(
        ...     token="YOUR_TOKEN",
        ...     name="Бар Атмосфера",
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
        enable_hookah: bool = True,
        age_limit: int = 18
    ):
        """
        Инициализация бота бара.
        
        Args:
            token: Токен Telegram бота
            name: Название бара
            timezone: Часовой пояс
            currency: Символ валюты
            enable_hookah: Включить кальянное меню
            age_limit: Возрастное ограничение
        """
        super().__init__(
            token=token,
            name=name,
            timezone=timezone,
            currency=currency,
            establishment_type=EstablishmentType.BAR
        )
        
        self.enable_hookah = enable_hookah
        self.age_limit = age_limit
        
        self.logger.info(f"Инициализирован BarBot: {name}")
        self.logger.info(f"  - Кальяны: {'Да' if enable_hookah else 'Нет'}")
        self.logger.info(f"  - Возрастное ограничение: {age_limit}+")
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Настройка стандартных обработчиков для бара"""
        
        @self.command('start')
        async def start_handler(update):
            chat_id = update['message']['chat']['id']
            user_name = update['message']['from'].get('first_name', 'Гость')
            
            welcome_text = (
                f"🍸 <b>Добро пожаловать в {self.name}!</b>\n\n"
                f"Привет, {user_name}! 🎉\n\n"
                f"Я помогу вам:\n"
                f"• 🍹 Посмотреть барное меню\n"
                f"• 🎫 Узнать афишу мероприятий\n"
                f"• 🪑 Забронировать стол/VIP-зону\n"
                f"• 📝 Попасть в гостевой лист\n"
            )
            
            if self.enable_hookah:
                welcome_text += "• 💨 Заказать кальян\n"
            
            welcome_text += f"\n⚠️ Вход {self.age_limit}+"
            
            keyboard = self.get_main_menu_keyboard()
            await self.send_message(chat_id, welcome_text, reply_markup=keyboard)
    
    def get_main_menu_keyboard(self):
        """Получить главную клавиатуру бара"""
        buttons = [
            [{"text": "🍹 Барное меню", "callback_data": "bar_menu"}],
            [{"text": "🎫 Афиша", "callback_data": "events"}],
            [{"text": "🪑 Бронирование", "callback_data": "vip_booking"}],
            [{"text": "📝 Гостевой лист", "callback_data": "guest_list"}]
        ]
        
        if self.enable_hookah:
            buttons.append([{"text": "💨 Кальянная карта", "callback_data": "hookah_menu"}])
        
        buttons.append([{"text": "ℹ️ Правила и дресс-код", "callback_data": "rules"}])
        
        return self.create_inline_keyboard(buttons)
