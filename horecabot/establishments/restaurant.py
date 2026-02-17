"""
Класс RestaurantBot для ресторанов
===================================

Специализированный бот для ресторанов с полным набором функций:
- Бронирование столиков
- Электронное меню с категориями
- Система заказов и доставки
- Отзывы и рейтинги
- Специальные предложения и акции
"""

from horecabot.core.base import HorecaBot, EstablishmentType
from typing import Optional


class RestaurantBot(HorecaBot):
    """
    Специализированный бот для ресторана.
    
    Включает функционал:
    - Бронирование столиков с учетом количества гостей
    - Меню с категориями, модификаторами, аллергенами
    - Система доставки с расчетом стоимости
    - Отзывы и рейтинги блюд
    - Акции и специальные предложения
    
    Example:
        >>> bot = RestaurantBot(
        ...     token="YOUR_TOKEN",
        ...     name="Ресторан Вкусно",
        ...     timezone="Europe/Moscow",
        ...     currency="₽"
        ... )
        >>> 
        >>> @bot.command('start')
        ... async def start(update):
        ...     keyboard = bot.get_main_menu_keyboard()
        ...     await bot.send_message(
        ...         update['message']['chat']['id'],
        ...         f"Добро пожаловать в {bot.name}! 🍽",
        ...         reply_markup=keyboard
        ...     )
        >>> 
        >>> bot.run()
    """
    
    def __init__(
        self,
        token: str,
        name: str,
        timezone: str = "Europe/Moscow",
        currency: str = "₽",
        enable_delivery: bool = True,
        enable_booking: bool = True,
        enable_reviews: bool = True
    ):
        """
        Инициализация бота ресторана.
        
        Args:
            token: Токен Telegram бота
            name: Название ресторана
            timezone: Часовой пояс
            currency: Символ валюты
            enable_delivery: Включить модуль доставки
            enable_booking: Включить модуль бронирования
            enable_reviews: Включить систему отзывов
        """
        super().__init__(
            token=token,
            name=name,
            timezone=timezone,
            currency=currency,
            establishment_type=EstablishmentType.RESTAURANT
        )
        
        self.enable_delivery = enable_delivery
        self.enable_booking = enable_booking
        self.enable_reviews = enable_reviews
        
        self.logger.info(f"Инициализирован RestaurantBot: {name}")
        self.logger.info(f"  - Доставка: {'Вкл' if enable_delivery else 'Выкл'}")
        self.logger.info(f"  - Бронирование: {'Вкл' if enable_booking else 'Выкл'}")
        self.logger.info(f"  - Отзывы: {'Вкл' if enable_reviews else 'Выкл'}")
        
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Настройка стандартных обработчиков для ресторана"""
        
        @self.command('start')
        async def start_handler(update):
            chat_id = update['message']['chat']['id']
            user_name = update['message']['from'].get('first_name', 'Гость')
            
            welcome_text = (
                f"🍽 <b>Добро пожаловать в {self.name}!</b>\n\n"
                f"Здравствуйте, {user_name}! Я помогу вам:\n"
                f"• 📋 Посмотреть меню и сделать заказ\n"
            )
            
            if self.enable_booking:
                welcome_text += "• 📅 Забронировать столик\n"
            
            if self.enable_delivery:
                welcome_text += "• 🚗 Оформить доставку\n"
            
            if self.enable_reviews:
                welcome_text += "• ⭐ Оставить отзыв\n"
            
            welcome_text += "\n💡 Используйте кнопки меню ниже для навигации"
            
            keyboard = self.get_main_menu_keyboard()
            await self.send_message(chat_id, welcome_text, reply_markup=keyboard)
        
        @self.command('menu')
        async def menu_handler(update):
            chat_id = update['message']['chat']['id']
            await self.send_message(
                chat_id,
                "📋 <b>Наше меню</b>\n\nВыберите категорию:",
                reply_markup=self.get_menu_categories_keyboard()
            )
        
        @self.command('booking')
        async def booking_handler(update):
            if not self.enable_booking:
                chat_id = update['message']['chat']['id']
                await self.send_message(
                    chat_id,
                    "❌ Бронирование временно недоступно"
                )
                return
            
            chat_id = update['message']['chat']['id']
            await self.send_message(
                chat_id,
                "📅 <b>Бронирование столика</b>\n\n"
                "Укажите желаемую дату и время, количество гостей.\n"
                "Мы подберем для вас свободный столик!",
                reply_markup=self.get_booking_keyboard()
            )
        
        @self.command('delivery')
        async def delivery_handler(update):
            if not self.enable_delivery:
                chat_id = update['message']['chat']['id']
                await self.send_message(
                    chat_id,
                    "❌ Доставка временно недоступна"
                )
                return
            
            chat_id = update['message']['chat']['id']
            await self.send_message(
                chat_id,
                "🚗 <b>Доставка</b>\n\n"
                "Мы доставляем заказы от 500₽\n"
                "Время доставки: 30-60 минут\n\n"
                "Оформите заказ из меню, и мы рассчитаем стоимость доставки"
            )
        
        @self.command('profile')
        async def profile_handler(update):
            chat_id = update['message']['chat']['id']
            user_name = update['message']['from'].get('first_name', 'Гость')
            
            await self.send_message(
                chat_id,
                f"👤 <b>Ваш профиль</b>\n\n"
                f"Имя: {user_name}\n"
                f"Баллы лояльности: 0\n"
                f"Всего заказов: 0\n"
                f"Любимое блюдо: —\n\n"
                f"💡 Совершайте заказы и зарабатывайте баллы!"
            )
    
    def get_main_menu_keyboard(self):
        """Получить главную клавиатуру ресторана"""
        buttons = [
            [{"text": "📋 Меню", "callback_data": "main_menu"}]
        ]
        
        if self.enable_booking:
            buttons.append([{"text": "📅 Забронировать столик", "callback_data": "booking"}])
        
        if self.enable_delivery:
            buttons.append([{"text": "🚗 Доставка", "callback_data": "delivery"}])
        
        buttons.extend([
            [{"text": "👤 Мой профиль", "callback_data": "profile"}],
            [{"text": "ℹ️ О ресторане", "callback_data": "about"}]
        ])
        
        return self.create_inline_keyboard(buttons)
    
    def get_menu_categories_keyboard(self):
        """Получить клавиатуру категорий меню"""
        buttons = [
            [{"text": "🍕 Закуски", "callback_data": "category_appetizers"}],
            [{"text": "🍝 Основные блюда", "callback_data": "category_main"}],
            [{"text": "🍰 Десерты", "callback_data": "category_desserts"}],
            [{"text": "🍹 Напитки", "callback_data": "category_drinks"}],
            [{"text": "🔙 Назад", "callback_data": "back_to_main"}]
        ]
        return self.create_inline_keyboard(buttons)
    
    def get_booking_keyboard(self):
        """Получить клавиатуру бронирования"""
        buttons = [
            [{"text": "📅 Выбрать дату", "callback_data": "booking_select_date"}],
            [{"text": "⏰ Выбрать время", "callback_data": "booking_select_time"}],
            [{"text": "👥 Количество гостей", "callback_data": "booking_guests"}],
            [{"text": "✅ Подтвердить бронь", "callback_data": "booking_confirm"}],
            [{"text": "🔙 Назад", "callback_data": "back_to_main"}]
        ]
        return self.create_inline_keyboard(buttons)
