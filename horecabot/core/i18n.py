"""
Internationalization (i18n) Support
====================================

Multi-language support for the bot.
"""

from typing import Dict, Optional, Any
from enum import Enum


class Language(Enum):
    """Поддерживаемые языки"""
    RU = "ru"  # Русский
    EN = "en"  # English
    ES = "es"  # Español
    DE = "de"  # Deutsch
    FR = "fr"  # Français
    IT = "it"  # Italiano
    ZH = "zh"  # 中文


# Словари переводов
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Общие фразы
    "welcome": {
        "ru": "Добро пожаловать в {name}!",
        "en": "Welcome to {name}!",
        "es": "¡Bienvenido a {name}!",
        "de": "Willkommen bei {name}!",
        "fr": "Bienvenue à {name}!",
        "it": "Benvenuto a {name}!",
        "zh": "欢迎来到{name}！",
    },
    "main_menu": {
        "ru": "Главное меню",
        "en": "Main menu",
        "es": "Menú principal",
        "de": "Hauptmenü",
        "fr": "Menu principal",
        "it": "Menu principale",
        "zh": "主菜单",
    },
    "back": {
        "ru": "◀️ Назад",
        "en": "◀️ Back",
        "es": "◀️ Atrás",
        "de": "◀️ Zurück",
        "fr": "◀️ Retour",
        "it": "◀️ Indietro",
        "zh": "◀️ 返回",
    },
    "cancel": {
        "ru": "❌ Отмена",
        "en": "❌ Cancel",
        "es": "❌ Cancelar",
        "de": "❌ Abbrechen",
        "fr": "❌ Annuler",
        "it": "❌ Annulla",
        "zh": "❌ 取消",
    },
    
    # Меню и заказы
    "menu": {
        "ru": "📋 Меню",
        "en": "📋 Menu",
        "es": "📋 Menú",
        "de": "📋 Speisekarte",
        "fr": "📋 Menu",
        "it": "📋 Menu",
        "zh": "📋 菜单",
    },
    "cart": {
        "ru": "🛒 Корзина",
        "en": "🛒 Cart",
        "es": "🛒 Carrito",
        "de": "🛒 Warenkorb",
        "fr": "🛒 Panier",
        "it": "🛒 Carrello",
        "zh": "🛒 购物车",
    },
    "order": {
        "ru": "📦 Заказать",
        "en": "📦 Order",
        "es": "📦 Pedir",
        "de": "📦 Bestellen",
        "fr": "📦 Commander",
        "it": "📦 Ordinare",
        "zh": "📦 订购",
    },
    "add_to_cart": {
        "ru": "➕ Добавить в корзину",
        "en": "➕ Add to cart",
        "es": "➕ Añadir al carrito",
        "de": "➕ In Warenkorb",
        "fr": "➕ Ajouter au panier",
        "it": "➕ Aggiungi al carrello",
        "zh": "➕ 加入购物车",
    },
    "cart_empty": {
        "ru": "Ваша корзина пуста",
        "en": "Your cart is empty",
        "es": "Tu carrito está vacío",
        "de": "Ihr Warenkorb ist leer",
        "fr": "Votre panier est vide",
        "it": "Il tuo carrello è vuoto",
        "zh": "您的购物车是空的",
    },
    "total": {
        "ru": "Итого",
        "en": "Total",
        "es": "Total",
        "de": "Gesamt",
        "fr": "Total",
        "it": "Totale",
        "zh": "总计",
    },
    
    # Бронирование
    "booking": {
        "ru": "📅 Бронирование",
        "en": "📅 Booking",
        "es": "📅 Reserva",
        "de": "📅 Buchung",
        "fr": "📅 Réservation",
        "it": "📅 Prenotazione",
        "zh": "📅 预订",
    },
    "select_date": {
        "ru": "Выберите дату",
        "en": "Select date",
        "es": "Seleccione la fecha",
        "de": "Datum wählen",
        "fr": "Sélectionnez la date",
        "it": "Seleziona la data",
        "zh": "选择日期",
    },
    "select_time": {
        "ru": "Выберите время",
        "en": "Select time",
        "es": "Seleccione la hora",
        "de": "Zeit wählen",
        "fr": "Sélectionnez l'heure",
        "it": "Seleziona l'ora",
        "zh": "选择时间",
    },
    "guests_count": {
        "ru": "Количество гостей",
        "en": "Number of guests",
        "es": "Número de invitados",
        "de": "Anzahl der Gäste",
        "fr": "Nombre de personnes",
        "it": "Numero di ospiti",
        "zh": "客人数量",
    },
    "booking_confirmed": {
        "ru": "✅ Бронирование подтверждено!",
        "en": "✅ Booking confirmed!",
        "es": "✅ ¡Reserva confirmada!",
        "de": "✅ Buchung bestätigt!",
        "fr": "✅ Réservation confirmée!",
        "it": "✅ Prenotazione confermata!",
        "zh": "✅ 预订已确认！",
    },
    
    # Профиль и лояльность
    "profile": {
        "ru": "👤 Профиль",
        "en": "👤 Profile",
        "es": "👤 Perfil",
        "de": "👤 Profil",
        "fr": "👤 Profil",
        "it": "👤 Profilo",
        "zh": "👤 个人资料",
    },
    "loyalty_points": {
        "ru": "Баллы лояльности",
        "en": "Loyalty points",
        "es": "Puntos de fidelidad",
        "de": "Treuepunkte",
        "fr": "Points de fidélité",
        "it": "Punti fedeltà",
        "zh": "积分",
    },
    "total_orders": {
        "ru": "Всего заказов",
        "en": "Total orders",
        "es": "Total de pedidos",
        "de": "Bestellungen insgesamt",
        "fr": "Commandes totales",
        "it": "Ordini totali",
        "zh": "总订单数",
    },
    
    # Ошибки
    "error_occurred": {
        "ru": "❌ Произошла ошибка. Попробуйте позже.",
        "en": "❌ An error occurred. Please try again later.",
        "es": "❌ Ocurrió un error. Inténtalo más tarde.",
        "de": "❌ Ein Fehler ist aufgetreten. Bitte versuchen Sie es später.",
        "fr": "❌ Une erreur s'est produite. Veuillez réessayer plus tard.",
        "it": "❌ Si è verificato un errore. Riprova più tardi.",
        "zh": "❌ 发生错误。请稍后再试。",
    },
    "invalid_input": {
        "ru": "❌ Неверный ввод. Попробуйте еще раз.",
        "en": "❌ Invalid input. Please try again.",
        "es": "❌ Entrada no válida. Inténtalo de nuevo.",
        "de": "❌ Ungültige Eingabe. Bitte versuchen Sie es erneut.",
        "fr": "❌ Entrée invalide. Veuillez réessayer.",
        "it": "❌ Input non valido. Riprova.",
        "zh": "❌ 输入无效。请重试。",
    },
    
    # Квизы
    "quiz": {
        "ru": "🎯 Квиз",
        "en": "🎯 Quiz",
        "es": "🎯 Cuestionario",
        "de": "🎯 Quiz",
        "fr": "🎯 Quiz",
        "it": "🎯 Quiz",
        "zh": "🎯 测验",
    },
    "start_quiz": {
        "ru": "Начать квиз",
        "en": "Start quiz",
        "es": "Comenzar cuestionario",
        "de": "Quiz starten",
        "fr": "Commencer le quiz",
        "it": "Inizia il quiz",
        "zh": "开始测验",
    },
    "quiz_results": {
        "ru": "Результаты квиза",
        "en": "Quiz results",
        "es": "Resultados del cuestionario",
        "de": "Quiz-Ergebnisse",
        "fr": "Résultats du quiz",
        "it": "Risultati del quiz",
        "zh": "测验结果",
    },
    "recommendations": {
        "ru": "Рекомендуем вам:",
        "en": "We recommend:",
        "es": "Te recomendamos:",
        "de": "Wir empfehlen:",
        "fr": "Nous vous recommandons:",
        "it": "Ti consigliamo:",
        "zh": "我们推荐：",
    },
}


class I18n:
    """
    Класс для работы с переводами.
    
    Example:
        >>> i18n = I18n(Language.EN)
        >>> print(i18n.get("welcome", name="MyBot"))
        Welcome to MyBot!
        
        >>> i18n.set_language(Language.RU)
        >>> print(i18n.get("welcome", name="МойБот"))
        Добро пожаловать в МойБот!
    """
    
    def __init__(self, default_language: Language = Language.RU):
        """
        Инициализация i18n.
        
        Args:
            default_language: Язык по умолчанию
        """
        self.default_language = default_language
        self.user_languages: Dict[int, Language] = {}
    
    def set_language(self, language: Language):
        """Установить язык по умолчанию"""
        self.default_language = language
    
    def set_user_language(self, user_id: int, language: Language):
        """
        Установить язык для конкретного пользователя.
        
        Args:
            user_id: ID пользователя
            language: Язык
        """
        self.user_languages[user_id] = language
    
    def get_user_language(self, user_id: int) -> Language:
        """
        Получить язык пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Язык пользователя или язык по умолчанию
        """
        return self.user_languages.get(user_id, self.default_language)
    
    def get(
        self,
        key: str,
        user_id: Optional[int] = None,
        language: Optional[Language] = None,
        **kwargs
    ) -> str:
        """
        Получить перевод.
        
        Args:
            key: Ключ перевода
            user_id: ID пользователя (для определения языка)
            language: Язык (переопределяет язык пользователя)
            **kwargs: Параметры для форматирования строки
        
        Returns:
            Переведенная строка
        """
        # Определяем язык
        if language is None:
            if user_id is not None:
                language = self.get_user_language(user_id)
            else:
                language = self.default_language
        
        # Получаем перевод
        if key not in TRANSLATIONS:
            return key
        
        translation_dict = TRANSLATIONS[key]
        text = translation_dict.get(
            language.value,
            translation_dict.get(self.default_language.value, key)
        )
        
        # Форматируем, если есть параметры
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        
        return text
    
    def t(self, key: str, user_id: Optional[int] = None, **kwargs) -> str:
        """Короткий алиас для get()"""
        return self.get(key, user_id=user_id, **kwargs)


# Глобальный экземпляр i18n
_i18n_instance = I18n()


def get_i18n() -> I18n:
    """Получить глобальный экземпляр i18n"""
    return _i18n_instance


def translate(key: str, user_id: Optional[int] = None, **kwargs) -> str:
    """
    Глобальная функция для перевода.
    
    Example:
        >>> from horecabot.core.i18n import translate as _
        >>> print(_("welcome", name="Bot"))
    """
    return _i18n_instance.get(key, user_id=user_id, **kwargs)


# Короткий алиас
_ = translate
