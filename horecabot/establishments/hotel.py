"""
Класс HotelBot для отелей
==========================

Специализированный бот для отелей с функционалом:
- Бронирование номеров
- Консьерж-сервис
- Информация об услугах отеля
- Продление проживания
"""

from horecabot.core.base import HorecaBot, EstablishmentType


class HotelBot(HorecaBot):
    """
    Специализированный бот для отеля.
    
    Включает функционал:
    - Бронирование номеров с выбором дат
    - Консьерж-сервис (такси, экскурсии)
    - Информация об услугах (бассейн, спа, рестораны)
    - Продление проживания и поздний выезд
    - Дополнительные услуги (трансфер, завтрак в номер)
    
    Example:
        >>> bot = HotelBot(
        ...     token="YOUR_TOKEN",
        ...     name="Гранд Отель",
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
        enable_concierge: bool = True,
        enable_spa: bool = True
    ):
        """
        Инициализация бота отеля.
        
        Args:
            token: Токен Telegram бота
            name: Название отеля
            timezone: Часовой пояс
            currency: Символ валюты
            enable_concierge: Включить консьерж-сервис
            enable_spa: Включить спа-услуги
        """
        super().__init__(
            token=token,
            name=name,
            timezone=timezone,
            currency=currency,
            establishment_type=EstablishmentType.HOTEL
        )
        
        self.enable_concierge = enable_concierge
        self.enable_spa = enable_spa
        
        self.logger.info(f"Инициализирован HotelBot: {name}")
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Настройка стандартных обработчиков для отеля"""
        
        @self.command('start')
        async def start_handler(update):
            chat_id = update['message']['chat']['id']
            user_name = update['message']['from'].get('first_name', 'Гость')
            
            welcome_text = (
                f"🏨 <b>Добро пожаловать в {self.name}!</b>\n\n"
                f"Здравствуйте, {user_name}! Я ваш цифровой помощник:\n\n"
                f"• 🛏 Забронировать номер\n"
                f"• ℹ️ Узнать об услугах отеля\n"
            )
            
            if self.enable_concierge:
                welcome_text += "• 🎩 Консьерж-сервис\n"
            
            if self.enable_spa:
                welcome_text += "• 💆 Спа и велнес\n"
            
            welcome_text += "\n💡 Используйте кнопки меню ниже"
            
            keyboard = self.get_main_menu_keyboard()
            await self.send_message(chat_id, welcome_text, reply_markup=keyboard)
    
    def get_main_menu_keyboard(self):
        """Получить главную клавиатуру отеля"""
        buttons = [
            [{"text": "🛏 Забронировать номер", "callback_data": "hotel_booking"}],
            [{"text": "ℹ️ Услуги отеля", "callback_data": "hotel_services"}]
        ]
        
        if self.enable_concierge:
            buttons.append([{"text": "🎩 Консьерж", "callback_data": "concierge"}])
        
        if self.enable_spa:
            buttons.append([{"text": "💆 Спа-салон", "callback_data": "spa"}])
        
        buttons.extend([
            [{"text": "🍽 Рестораны", "callback_data": "restaurants"}],
            [{"text": "👤 Мой профиль", "callback_data": "profile"}]
        ])
        
        return self.create_inline_keyboard(buttons)
