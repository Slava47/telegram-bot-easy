"""
Базовый класс HorecaBot
========================

Фундамент для всех специализированных типов заведений.
Инкапсулирует работу с Telegram API, маршрутизацию сообщений,
обработку ошибок и логирование.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import aiohttp
import pytz
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class EstablishmentType(Enum):
    """Типы заведений"""
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    CAFE = "cafe"
    BAR = "bar"
    FASTFOOD = "fastfood"


class HorecaBot:
    """
    Базовый класс для всех типов HoReCa заведений.
    
    Attributes:
        token (str): Токен Telegram бота
        name (str): Название заведения
        timezone (str): Часовой пояс (например, 'Europe/Moscow')
        currency (str): Символ валюты (например, '₽', '$', '€')
        establishment_type (EstablishmentType): Тип заведения
    
    Example:
        >>> bot = HorecaBot(
        ...     token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        ...     name="Моё Заведение",
        ...     timezone="Europe/Moscow",
        ...     currency="₽",
        ...     establishment_type=EstablishmentType.RESTAURANT
        ... )
        >>> bot.run()
    """
    
    def __init__(
        self,
        token: str,
        name: str,
        timezone: str = "Europe/Moscow",
        currency: str = "₽",
        establishment_type: EstablishmentType = EstablishmentType.RESTAURANT
    ):
        """
        Инициализация базового класса HorecaBot.
        
        Args:
            token: Токен Telegram бота от @BotFather
            name: Название вашего заведения
            timezone: Часовой пояс для корректной работы с бронированиями
            currency: Символ валюты для отображения цен
            establishment_type: Тип заведения (ресторан, отель, кафе и т.д.)
        """
        self.token = token
        self.name = name
        self.timezone = pytz.timezone(timezone)
        self.currency = currency
        self.establishment_type = establishment_type
        
        self.logger = logging.getLogger(f"HorecaBot.{name}")
        self.api_url = f"https://api.telegram.org/bot{token}"
        
        # Хранилище обработчиков команд и сообщений
        self.handlers: Dict[str, Callable] = {}
        self.message_handlers: List[Callable] = []
        self.callback_handlers: Dict[str, Callable] = {}
        
        # Состояние бота
        self.running = False
        self.last_update_id = 0
        
        # Модули (будут инициализированы в дочерних классах)
        self.menu_module = None
        self.booking_module = None
        self.quiz_module = None
        self.loyalty_module = None
        self.analytics_module = None
        
        self.logger.info(
            f"Инициализирован бот '{name}' для заведения типа {establishment_type.value}"
        )
    
    def command(self, command_name: str):
        """
        Декоратор для регистрации обработчиков команд.
        
        Args:
            command_name: Имя команды без слэша (например, 'start', 'help')
        
        Example:
            >>> @bot.command('start')
            ... async def start_handler(update):
            ...     await bot.send_message(update['chat']['id'], "Привет!")
        """
        def decorator(func: Callable):
            self.handlers[command_name] = func
            self.logger.debug(f"Зарегистрирована команда /{command_name}")
            return func
        return decorator
    
    def on_message(self, func: Callable):
        """
        Декоратор для регистрации обработчика текстовых сообщений.
        
        Example:
            >>> @bot.on_message
            ... async def message_handler(update):
            ...     text = update['message']['text']
            ...     await bot.send_message(update['message']['chat']['id'], f"Вы написали: {text}")
        """
        self.message_handlers.append(func)
        self.logger.debug("Зарегистрирован обработчик текстовых сообщений")
        return func
    
    def on_callback(self, callback_data: str):
        """
        Декоратор для регистрации обработчика callback-запросов от inline-кнопок.
        
        Args:
            callback_data: Данные callback-кнопки
        
        Example:
            >>> @bot.on_callback('menu_category_drinks')
            ... async def show_drinks(update):
            ...     await bot.send_message(update['chat']['id'], "Напитки")
        """
        def decorator(func: Callable):
            self.callback_handlers[callback_data] = func
            self.logger.debug(f"Зарегистрирован обработчик callback: {callback_data}")
            return func
        return decorator
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Dict] = None,
        parse_mode: str = "HTML"
    ) -> Dict[str, Any]:
        """
        Отправка сообщения пользователю.
        
        Args:
            chat_id: ID чата/пользователя
            text: Текст сообщения
            reply_markup: Клавиатура (опционально)
            parse_mode: Режим форматирования (HTML или Markdown)
        
        Returns:
            Ответ от Telegram API
        """
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/sendMessage", json=data) as resp:
                result = await resp.json()
                if not result.get("ok"):
                    self.logger.error(f"Ошибка отправки сообщения: {result}")
                return result
    
    async def send_photo(
        self,
        chat_id: int,
        photo: str,
        caption: Optional[str] = None,
        reply_markup: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Отправка фотографии пользователю.
        
        Args:
            chat_id: ID чата/пользователя
            photo: URL или file_id фотографии
            caption: Подпись к фото (опционально)
            reply_markup: Клавиатура (опционально)
        
        Returns:
            Ответ от Telegram API
        """
        data = {
            "chat_id": chat_id,
            "photo": photo
        }
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/sendPhoto", json=data) as resp:
                return await resp.json()
    
    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Редактирование текста сообщения.
        
        Args:
            chat_id: ID чата
            message_id: ID сообщения
            text: Новый текст
            reply_markup: Новая клавиатура (опционально)
        
        Returns:
            Ответ от Telegram API
        """
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/editMessageText", json=data) as resp:
                return await resp.json()
    
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False
    ) -> Dict[str, Any]:
        """
        Ответ на callback-запрос.
        
        Args:
            callback_query_id: ID callback-запроса
            text: Текст уведомления (опционально)
            show_alert: Показать как алерт вместо уведомления
        
        Returns:
            Ответ от Telegram API
        """
        data = {
            "callback_query_id": callback_query_id
        }
        if text:
            data["text"] = text
        if show_alert:
            data["show_alert"] = show_alert
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/answerCallbackQuery", json=data) as resp:
                return await resp.json()
    
    async def get_updates(self, offset: Optional[int] = None, timeout: int = 30) -> List[Dict]:
        """
        Получение обновлений от Telegram (long polling).
        
        Args:
            offset: ID последнего обработанного обновления + 1
            timeout: Таймаут long polling в секундах
        
        Returns:
            Список обновлений
        """
        params = {"timeout": timeout}
        if offset:
            params["offset"] = offset
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/getUpdates", params=params) as resp:
                    result = await resp.json()
                    if result.get("ok"):
                        return result.get("result", [])
                    else:
                        self.logger.error(f"Ошибка получения обновлений: {result}")
                        return []
        except Exception as e:
            self.logger.error(f"Исключение при получении обновлений: {e}")
            return []
    
    async def process_update(self, update: Dict[str, Any]):
        """
        Обработка одного обновления от Telegram.
        
        Args:
            update: Объект обновления от Telegram
        """
        try:
            # Обработка команд
            if "message" in update and "text" in update["message"]:
                text = update["message"]["text"]
                if text.startswith("/"):
                    command = text.split()[0][1:]  # Убираем /
                    if command in self.handlers:
                        await self.handlers[command](update)
                        return
                
                # Обработка текстовых сообщений
                for handler in self.message_handlers:
                    await handler(update)
            
            # Обработка callback-запросов
            elif "callback_query" in update:
                callback_data = update["callback_query"]["data"]
                if callback_data in self.callback_handlers:
                    await self.callback_handlers[callback_data](update)
                    await self.answer_callback_query(update["callback_query"]["id"])
        
        except Exception as e:
            self.logger.error(f"Ошибка обработки обновления: {e}", exc_info=True)
    
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> Dict:
        """
        Создание inline-клавиатуры.
        
        Args:
            buttons: Массив массивов кнопок
                     Каждая кнопка: {"text": "Текст", "callback_data": "данные"}
        
        Returns:
            Объект inline_keyboard для reply_markup
        
        Example:
            >>> keyboard = bot.create_inline_keyboard([
            ...     [{"text": "Меню", "callback_data": "menu"}],
            ...     [{"text": "Бронирование", "callback_data": "booking"}]
            ... ])
        """
        return {"inline_keyboard": buttons}
    
    def create_reply_keyboard(
        self,
        buttons: List[List[str]],
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False
    ) -> Dict:
        """
        Создание reply-клавиатуры.
        
        Args:
            buttons: Массив массивов кнопок (строки с текстом)
            resize_keyboard: Автоматически подстраивать размер
            one_time_keyboard: Скрывать после использования
        
        Returns:
            Объект keyboard для reply_markup
        
        Example:
            >>> keyboard = bot.create_reply_keyboard([
            ...     ["📋 Меню", "📅 Бронирование"],
            ...     ["👤 Профиль"]
            ... ])
        """
        keyboard = [[{"text": btn} for btn in row] for row in buttons]
        return {
            "keyboard": keyboard,
            "resize_keyboard": resize_keyboard,
            "one_time_keyboard": one_time_keyboard
        }
    
    async def start_polling(self):
        """
        Запуск бота в режиме long polling.
        Бот будет получать и обрабатывать обновления от Telegram.
        """
        self.running = True
        self.logger.info(f"Запуск бота '{self.name}' в режиме polling...")
        
        while self.running:
            updates = await self.get_updates(offset=self.last_update_id + 1)
            
            for update in updates:
                self.last_update_id = update["update_id"]
                await self.process_update(update)
            
            await asyncio.sleep(0.1)  # Небольшая задержка между циклами
    
    def stop(self):
        """Остановка бота."""
        self.running = False
        self.logger.info(f"Бот '{self.name}' остановлен")
    
    def run(self):
        """
        Запуск бота (упрощенный метод).
        Создает event loop и запускает polling.
        """
        try:
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал остановки (Ctrl+C)")
            self.stop()
