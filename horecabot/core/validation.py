"""
Input Validation and Error Handling
====================================

Provides validation functions and error handling utilities
for user input processing.
"""

import re
from typing import Optional, Tuple, Any
from datetime import datetime, date, time
from enum import Enum


class ValidationError(Exception):
    """Ошибка валидации пользовательского ввода"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ErrorType(Enum):
    """Типы ошибок"""
    INVALID_FORMAT = "invalid_format"
    OUT_OF_RANGE = "out_of_range"
    REQUIRED_FIELD = "required_field"
    INVALID_CHOICE = "invalid_choice"
    DUPLICATE = "duplicate"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация номера телефона.
    
    Args:
        phone: Номер телефона
    
    Returns:
        Кортеж (валидность, сообщение об ошибке)
    
    Example:
        >>> valid, error = validate_phone("+79991234567")
        >>> print(valid)  # True
        >>> valid, error = validate_phone("invalid")
        >>> print(error)  # "Неверный формат номера телефона..."
    """
    # Удаляем пробелы и дефисы
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Проверяем формат
    # Поддерживаем форматы: +79991234567, 89991234567, 79991234567
    pattern = r'^(\+?7|8)?[0-9]{10}$'
    
    if not re.match(pattern, cleaned):
        return False, "Неверный формат номера телефона. Используйте формат: +79991234567"
    
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация email адреса.
    
    Args:
        email: Email адрес
    
    Returns:
        Кортеж (валидность, сообщение об ошибке)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Неверный формат email адреса"
    
    return True, None


def validate_date(date_str: str, date_format: str = "%d.%m.%Y") -> Tuple[bool, Optional[str], Optional[date]]:
    """
    Валидация даты.
    
    Args:
        date_str: Строка с датой
        date_format: Формат даты (по умолчанию DD.MM.YYYY)
    
    Returns:
        Кортеж (валидность, сообщение об ошибке, объект date)
    """
    try:
        parsed_date = datetime.strptime(date_str, date_format).date()
        
        # Проверяем, что дата не в прошлом
        if parsed_date < date.today():
            return False, "Дата не может быть в прошлом", None
        
        return True, None, parsed_date
    except ValueError:
        return False, f"Неверный формат даты. Используйте формат: {date_format}", None


def validate_time(time_str: str, time_format: str = "%H:%M") -> Tuple[bool, Optional[str], Optional[time]]:
    """
    Валидация времени.
    
    Args:
        time_str: Строка со временем
        time_format: Формат времени (по умолчанию HH:MM)
    
    Returns:
        Кортеж (валидность, сообщение об ошибке, объект time)
    """
    try:
        parsed_time = datetime.strptime(time_str, time_format).time()
        return True, None, parsed_time
    except ValueError:
        return False, f"Неверный формат времени. Используйте формат: {time_format}", None


def validate_integer(
    value: str,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Валидация целого числа.
    
    Args:
        value: Строка с числом
        min_value: Минимальное значение (опционально)
        max_value: Максимальное значение (опционально)
    
    Returns:
        Кортеж (валидность, сообщение об ошибке, значение)
    """
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            return False, f"Значение должно быть не меньше {min_value}", None
        
        if max_value is not None and int_value > max_value:
            return False, f"Значение должно быть не больше {max_value}", None
        
        return True, None, int_value
    except ValueError:
        return False, "Введите корректное целое число", None


def validate_float(
    value: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Валидация числа с плавающей точкой.
    
    Args:
        value: Строка с числом
        min_value: Минимальное значение (опционально)
        max_value: Максимальное значение (опционально)
    
    Returns:
        Кортеж (валидность, сообщение об ошибке, значение)
    """
    try:
        float_value = float(value.replace(',', '.'))
        
        if min_value is not None and float_value < min_value:
            return False, f"Значение должно быть не меньше {min_value}", None
        
        if max_value is not None and float_value > max_value:
            return False, f"Значение должно быть не больше {max_value}", None
        
        return True, None, float_value
    except ValueError:
        return False, "Введите корректное число", None


def validate_choice(value: str, choices: list) -> Tuple[bool, Optional[str]]:
    """
    Валидация выбора из списка.
    
    Args:
        value: Выбранное значение
        choices: Список допустимых значений
    
    Returns:
        Кортеж (валидность, сообщение об ошибке)
    """
    if value not in choices:
        return False, f"Выберите одно из: {', '.join(str(c) for c in choices)}"
    
    return True, None


def validate_text_length(
    text: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Валидация длины текста.
    
    Args:
        text: Текст для проверки
        min_length: Минимальная длина (опционально)
        max_length: Максимальная длина (опционально)
    
    Returns:
        Кортеж (валидность, сообщение об ошибке)
    """
    text_length = len(text)
    
    if min_length is not None and text_length < min_length:
        return False, f"Текст должен содержать не менее {min_length} символов"
    
    if max_length is not None and text_length > max_length:
        return False, f"Текст должен содержать не более {max_length} символов"
    
    return True, None


def validate_rating(rating: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Валидация рейтинга (1-5).
    
    Args:
        rating: Строка с рейтингом
    
    Returns:
        Кортеж (валидность, сообщение об ошибке, значение)
    """
    valid, error, value = validate_integer(rating, min_value=1, max_value=5)
    
    if not valid:
        return False, "Рейтинг должен быть от 1 до 5", None
    
    return True, None, value


def sanitize_input(text: str) -> str:
    """
    Санитизация пользовательского ввода.
    
    Удаляет потенциально опасные символы и последовательности.
    
    Args:
        text: Входной текст
    
    Returns:
        Очищенный текст
    """
    # Удаляем HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Удаляем управляющие символы
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Обрезаем пробелы
    text = text.strip()
    
    return text


class ErrorHandler:
    """
    Обработчик ошибок для бота.
    
    Предоставляет единообразный способ обработки и отображения ошибок.
    """
    
    # Словарь сообщений об ошибках
    ERROR_MESSAGES = {
        ErrorType.INVALID_FORMAT: "❌ Неверный формат данных. Попробуйте еще раз.",
        ErrorType.OUT_OF_RANGE: "❌ Значение вне допустимого диапазона.",
        ErrorType.REQUIRED_FIELD: "❌ Это обязательное поле. Пожалуйста, заполните его.",
        ErrorType.INVALID_CHOICE: "❌ Выберите один из предложенных вариантов.",
        ErrorType.DUPLICATE: "❌ Такая запись уже существует.",
        ErrorType.NOT_FOUND: "❌ Запрашиваемый объект не найден.",
        ErrorType.PERMISSION_DENIED: "❌ У вас нет прав для выполнения этого действия.",
        ErrorType.TIMEOUT: "⏱ Время ожидания истекло. Попробуйте еще раз.",
        ErrorType.NETWORK_ERROR: "🌐 Ошибка сети. Пожалуйста, повторите попытку позже.",
    }
    
    @staticmethod
    def format_error(error_type: ErrorType, details: Optional[str] = None) -> str:
        """
        Форматировать сообщение об ошибке.
        
        Args:
            error_type: Тип ошибки
            details: Дополнительные детали (опционально)
        
        Returns:
            Отформатированное сообщение
        """
        message = ErrorHandler.ERROR_MESSAGES.get(
            error_type,
            "❌ Произошла ошибка. Попробуйте еще раз."
        )
        
        if details:
            message += f"\n\n{details}"
        
        return message
    
    @staticmethod
    def handle_validation_error(error: ValidationError) -> str:
        """
        Обработать ошибку валидации.
        
        Args:
            error: Объект ValidationError
        
        Returns:
            Сообщение об ошибке для пользователя
        """
        return f"❌ {error.message}"
