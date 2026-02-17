"""
Menu Caching System
===================

Provides caching functionality for menu items and categories
to improve performance and reduce database queries.
"""

from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import hashlib


@dataclass
class CacheEntry:
    """Запись в кэше"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """Проверить, истекла ли запись"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def increment_hits(self):
        """Увеличить счетчик обращений"""
        self.hit_count += 1


class MenuCache:
    """
    Система кэширования меню.
    
    Кэширует меню, категории и часто запрашиваемые данные
    для уменьшения нагрузки и ускорения работы.
    
    Example:
        >>> cache = MenuCache(ttl=300)  # TTL 5 минут
        >>> 
        >>> # Кэшировать меню
        >>> cache.set("menu:full", menu_data)
        >>> 
        >>> # Получить из кэша
        >>> menu = cache.get("menu:full")
        >>> if menu is None:
        ...     menu = load_menu_from_db()
        ...     cache.set("menu:full", menu)
    """
    
    def __init__(
        self,
        ttl: int = 300,  # Time to live в секундах (5 минут по умолчанию)
        max_size: int = 1000  # Максимальный размер кэша
    ):
        """
        Инициализация кэша.
        
        Args:
            ttl: Время жизни записей в секундах
            max_size: Максимальное количество записей
        """
        self.ttl = ttl
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        
        # Статистика
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, namespace: str, identifier: str) -> str:
        """
        Создать ключ кэша.
        
        Args:
            namespace: Пространство имен (menu, category, item и т.д.)
            identifier: Идентификатор
        
        Returns:
            Ключ кэша
        """
        return f"{namespace}:{identifier}"
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Установить значение в кэш.
        
        Args:
            key: Ключ
            value: Значение
            ttl: Время жизни (переопределяет TTL по умолчанию)
        """
        # Проверяем размер кэша
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Вычисляем время истечения
        expires_at = None
        if ttl is not None or self.ttl > 0:
            ttl_seconds = ttl if ttl is not None else self.ttl
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        # Создаем запись
        entry = CacheEntry(
            key=key,
            value=value,
            expires_at=expires_at
        )
        
        self.cache[key] = entry
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша.
        
        Args:
            key: Ключ
        
        Returns:
            Значение или None если не найдено/истекло
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Проверяем истечение
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        # Обновляем статистику
        entry.increment_hits()
        self.hits += 1
        
        return entry.value
    
    def delete(self, key: str):
        """
        Удалить запись из кэша.
        
        Args:
            key: Ключ
        """
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Очистить весь кэш"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def clear_namespace(self, namespace: str):
        """
        Очистить все записи с определенным префиксом.
        
        Args:
            namespace: Пространство имен
        """
        keys_to_delete = [
            key for key in self.cache.keys()
            if key.startswith(f"{namespace}:")
        ]
        
        for key in keys_to_delete:
            del self.cache[key]
    
    def _evict_lru(self):
        """Удалить наименее используемую запись (LRU - Least Recently Used)"""
        if not self.cache:
            return
        
        # Находим запись с наименьшим hit_count
        lru_key = min(self.cache.items(), key=lambda x: x[1].hit_count)[0]
        del self.cache[lru_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику кэша.
        
        Returns:
            Словарь со статистикой
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "ttl": self.ttl,
        }
    
    def cleanup_expired(self):
        """Очистить истекшие записи"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]


class MenuCacheDecorator:
    """
    Декоратор для автоматического кэширования результатов функций.
    
    Example:
        >>> cache = MenuCache()
        >>> decorator = MenuCacheDecorator(cache)
        >>> 
        >>> @decorator.cached("menu", ttl=300)
        >>> def get_menu(menu_id):
        ...     return load_menu_from_db(menu_id)
    """
    
    def __init__(self, cache: MenuCache):
        """
        Инициализация декоратора.
        
        Args:
            cache: Экземпляр MenuCache
        """
        self.cache = cache
    
    def cached(
        self,
        namespace: str,
        ttl: Optional[int] = None,
        key_builder: Optional[callable] = None
    ):
        """
        Декоратор для кэширования.
        
        Args:
            namespace: Пространство имен для кэша
            ttl: Время жизни
            key_builder: Функция для построения ключа из аргументов
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Строим ключ кэша
                if key_builder:
                    cache_key = f"{namespace}:{key_builder(*args, **kwargs)}"
                else:
                    # По умолчанию используем хеш аргументов
                    args_str = json.dumps([str(arg) for arg in args], sort_keys=True)
                    kwargs_str = json.dumps(kwargs, sort_keys=True)
                    key_hash = hashlib.md5(f"{args_str}{kwargs_str}".encode()).hexdigest()
                    cache_key = f"{namespace}:{key_hash}"
                
                # Пытаемся получить из кэша
                cached_value = self.cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Вычисляем значение
                result = func(*args, **kwargs)
                
                # Сохраняем в кэш
                self.cache.set(cache_key, result, ttl=ttl)
                
                return result
            
            return wrapper
        return decorator


class SmartMenuCache:
    """
    Умный кэш меню с автоматической инвалидацией.
    
    Автоматически обновляет зависимые записи при изменении данных.
    """
    
    def __init__(self, ttl: int = 300):
        """
        Инициализация умного кэша.
        
        Args:
            ttl: Время жизни записей
        """
        self.cache = MenuCache(ttl=ttl)
        self.dependencies: Dict[str, List[str]] = {}  # key -> [dependent_keys]
    
    def set_with_dependencies(
        self,
        key: str,
        value: Any,
        depends_on: Optional[List[str]] = None
    ):
        """
        Установить значение с зависимостями.
        
        Args:
            key: Ключ
            value: Значение
            depends_on: Список ключей, от которых зависит данная запись
        """
        self.cache.set(key, value)
        
        if depends_on:
            for parent_key in depends_on:
                if parent_key not in self.dependencies:
                    self.dependencies[parent_key] = []
                if key not in self.dependencies[parent_key]:
                    self.dependencies[parent_key].append(key)
    
    def invalidate(self, key: str):
        """
        Инвалидировать запись и все зависимые.
        
        Args:
            key: Ключ
        """
        # Удаляем саму запись
        self.cache.delete(key)
        
        # Удаляем зависимые записи
        if key in self.dependencies:
            for dependent_key in self.dependencies[key]:
                self.invalidate(dependent_key)
            del self.dependencies[key]
    
    def invalidate_category(self, category_id: str):
        """
        Инвалидировать все записи, связанные с категорией.
        
        Args:
            category_id: ID категории
        """
        self.invalidate(f"category:{category_id}")
        self.cache.clear_namespace("menu")  # Очищаем полное меню
    
    def invalidate_item(self, item_id: str):
        """
        Инвалидировать все записи, связанные с позицией.
        
        Args:
            item_id: ID позиции
        """
        self.invalidate(f"item:{item_id}")
        self.cache.clear_namespace("menu")  # Очищаем полное меню
        self.cache.clear_namespace("category")  # Очищаем категории
