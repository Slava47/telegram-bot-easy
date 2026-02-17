"""
Модуль бронирования
===================

Управление бронированием столиков, номеров и других ресурсов.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from enum import Enum


class BookingStatus(Enum):
    """Статусы бронирования"""
    PENDING = "pending"  # Ожидает подтверждения
    CONFIRMED = "confirmed"  # Подтверждено
    CANCELLED = "cancelled"  # Отменено
    COMPLETED = "completed"  # Завершено


class BookingType(Enum):
    """Типы бронирования"""
    TABLE = "table"  # Столик в ресторане/кафе/баре
    ROOM = "room"  # Номер в отеле
    VIP_ZONE = "vip_zone"  # VIP-зона в баре/клубе


@dataclass
class TimeSlot:
    """Временной слот"""
    start_time: time
    end_time: time
    
    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


@dataclass
class Booking:
    """
    Бронирование.
    
    Attributes:
        id: Уникальный идентификатор
        user_id: ID пользователя Telegram
        user_name: Имя гостя
        user_phone: Телефон гостя
        booking_type: Тип бронирования
        resource_id: ID ресурса (столик, номер и т.д.)
        booking_date: Дата бронирования
        time_slot: Временной слот (для столиков)
        check_in: Дата заезда (для отелей)
        check_out: Дата выезда (для отелей)
        guests_count: Количество гостей
        special_requests: Особые пожелания
        status: Статус бронирования
        deposit_amount: Сумма депозита (для VIP-зон)
        created_at: Время создания
    """
    id: str
    user_id: int
    user_name: str
    user_phone: str
    booking_type: BookingType
    resource_id: str
    booking_date: date
    guests_count: int
    status: BookingStatus = BookingStatus.PENDING
    
    # Опциональные поля
    time_slot: Optional[TimeSlot] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    special_requests: str = ""
    deposit_amount: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_phone": self.user_phone,
            "booking_type": self.booking_type.value,
            "resource_id": self.resource_id,
            "booking_date": self.booking_date.isoformat(),
            "guests_count": self.guests_count,
            "status": self.status.value,
            "time_slot": str(self.time_slot) if self.time_slot else None,
            "check_in": self.check_in.isoformat() if self.check_in else None,
            "check_out": self.check_out.isoformat() if self.check_out else None,
            "special_requests": self.special_requests,
            "deposit_amount": self.deposit_amount,
        }


@dataclass
class Resource:
    """
    Ресурс для бронирования (столик, номер и т.д.).
    
    Attributes:
        id: Уникальный идентификатор
        name: Название (например, "Столик №5", "Люкс")
        resource_type: Тип ресурса
        capacity: Вместимость (количество гостей)
        price_per_night: Цена за ночь (для номеров)
        min_deposit: Минимальный депозит (для VIP-зон)
        features: Особенности (у окна, с видом на море и т.д.)
    """
    id: str
    name: str
    resource_type: BookingType
    capacity: int
    price_per_night: float = 0.0
    min_deposit: float = 0.0
    features: List[str] = field(default_factory=list)


class BookingModule:
    """
    Модуль бронирования.
    
    Управление бронированиями столиков, номеров и других ресурсов.
    
    Example:
        >>> booking = BookingModule()
        >>> 
        >>> # Добавляем ресурсы (столики)
        >>> booking.add_resource(Resource(
        ...     id="table_1",
        ...     name="Столик №1",
        ...     resource_type=BookingType.TABLE,
        ...     capacity=4,
        ...     features=["у окна"]
        ... ))
        >>> 
        >>> # Настраиваем рабочие часы
        >>> booking.set_working_hours(
        ...     time(10, 0),  # открытие
        ...     time(22, 0),  # закрытие
        ...     slot_duration=60  # слоты по 60 минут
        ... )
        >>> 
        >>> # Создаем бронирование
        >>> booking_obj = booking.create_booking(
        ...     user_id=123456,
        ...     user_name="Иван Иванов",
        ...     user_phone="+79991234567",
        ...     booking_type=BookingType.TABLE,
        ...     booking_date=date.today(),
        ...     guests_count=4
        ... )
    """
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}  # resource_id -> Resource
        self.bookings: Dict[str, Booking] = {}  # booking_id -> Booking
        self.user_bookings: Dict[int, List[str]] = {}  # user_id -> [booking_ids]
        
        # Настройки рабочего времени
        self.opening_time: time = time(10, 0)
        self.closing_time: time = time(22, 0)
        self.slot_duration: int = 60  # минуты
        self.booking_depth_days: int = 30  # на сколько дней вперед можно бронировать
    
    def add_resource(self, resource: Resource):
        """
        Добавить ресурс для бронирования.
        
        Args:
            resource: Объект Resource
        """
        self.resources[resource.id] = resource
    
    def set_working_hours(
        self,
        opening: time,
        closing: time,
        slot_duration: int = 60
    ):
        """
        Установить рабочие часы.
        
        Args:
            opening: Время открытия
            closing: Время закрытия
            slot_duration: Длительность слота в минутах
        """
        self.opening_time = opening
        self.closing_time = closing
        self.slot_duration = slot_duration
    
    def get_available_slots(
        self,
        booking_date: date,
        resource_id: Optional[str] = None
    ) -> List[TimeSlot]:
        """
        Получить доступные временные слоты на дату.
        
        Args:
            booking_date: Дата бронирования
            resource_id: ID ресурса (опционально)
        
        Returns:
            Список доступных TimeSlot
        """
        slots = []
        
        # Генерируем все возможные слоты
        current_time = datetime.combine(booking_date, self.opening_time)
        end_time = datetime.combine(booking_date, self.closing_time)
        
        while current_time < end_time:
            slot_start = current_time.time()
            slot_end = (current_time + timedelta(minutes=self.slot_duration)).time()
            
            time_slot = TimeSlot(start_time=slot_start, end_time=slot_end)
            
            # Проверяем, не занят ли слот
            if self._is_slot_available(booking_date, time_slot, resource_id):
                slots.append(time_slot)
            
            current_time += timedelta(minutes=self.slot_duration)
        
        return slots
    
    def _is_slot_available(
        self,
        booking_date: date,
        time_slot: TimeSlot,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Проверить, свободен ли слот.
        
        Args:
            booking_date: Дата
            time_slot: Временной слот
            resource_id: ID ресурса (если не указан, проверяем любой)
        
        Returns:
            True если слот свободен
        """
        for booking in self.bookings.values():
            # Пропускаем отмененные брони
            if booking.status == BookingStatus.CANCELLED:
                continue
            
            # Проверяем дату
            if booking.booking_date != booking_date:
                continue
            
            # Проверяем ресурс
            if resource_id and booking.resource_id != resource_id:
                continue
            
            # Проверяем пересечение временных слотов
            if booking.time_slot:
                if self._slots_overlap(booking.time_slot, time_slot):
                    return False
        
        return True
    
    def _slots_overlap(self, slot1: TimeSlot, slot2: TimeSlot) -> bool:
        """Проверить, пересекаются ли два временных слота"""
        return not (slot1.end_time <= slot2.start_time or slot2.end_time <= slot1.start_time)
    
    def create_booking(
        self,
        user_id: int,
        user_name: str,
        user_phone: str,
        booking_type: BookingType,
        booking_date: date,
        guests_count: int,
        resource_id: Optional[str] = None,
        time_slot: Optional[TimeSlot] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        special_requests: str = ""
    ) -> Optional[Booking]:
        """
        Создать бронирование.
        
        Args:
            user_id: ID пользователя
            user_name: Имя гостя
            user_phone: Телефон
            booking_type: Тип бронирования
            booking_date: Дата бронирования
            guests_count: Количество гостей
            resource_id: ID ресурса (опционально, можно подобрать автоматически)
            time_slot: Временной слот (для столиков)
            check_in: Дата заезда (для отелей)
            check_out: Дата выезда (для отелей)
            special_requests: Особые пожелания
        
        Returns:
            Объект Booking или None если не удалось создать
        """
        # Если ресурс не указан, подбираем автоматически
        if not resource_id:
            resource_id = self._find_available_resource(
                booking_type, booking_date, guests_count, time_slot
            )
            if not resource_id:
                return None
        
        # Создаем бронирование
        booking_id = f"booking_{user_id}_{int(datetime.now().timestamp())}"
        
        booking = Booking(
            id=booking_id,
            user_id=user_id,
            user_name=user_name,
            user_phone=user_phone,
            booking_type=booking_type,
            resource_id=resource_id,
            booking_date=booking_date,
            guests_count=guests_count,
            time_slot=time_slot,
            check_in=check_in,
            check_out=check_out,
            special_requests=special_requests
        )
        
        self.bookings[booking_id] = booking
        
        # Добавляем в список бронирований пользователя
        if user_id not in self.user_bookings:
            self.user_bookings[user_id] = []
        self.user_bookings[user_id].append(booking_id)
        
        return booking
    
    def _find_available_resource(
        self,
        booking_type: BookingType,
        booking_date: date,
        guests_count: int,
        time_slot: Optional[TimeSlot] = None
    ) -> Optional[str]:
        """
        Найти доступный ресурс.
        
        Args:
            booking_type: Тип бронирования
            booking_date: Дата
            guests_count: Количество гостей
            time_slot: Временной слот (опционально)
        
        Returns:
            ID ресурса или None
        """
        for resource in self.resources.values():
            if resource.resource_type != booking_type:
                continue
            
            if resource.capacity < guests_count:
                continue
            
            # Проверяем доступность
            if time_slot:
                if self._is_slot_available(booking_date, time_slot, resource.id):
                    return resource.id
            else:
                # Для отелей просто проверяем, что номер свободен
                return resource.id
        
        return None
    
    def confirm_booking(self, booking_id: str):
        """Подтвердить бронирование"""
        if booking_id in self.bookings:
            self.bookings[booking_id].status = BookingStatus.CONFIRMED
    
    def cancel_booking(self, booking_id: str):
        """Отменить бронирование"""
        if booking_id in self.bookings:
            self.bookings[booking_id].status = BookingStatus.CANCELLED
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Получить бронирование по ID"""
        return self.bookings.get(booking_id)
    
    def get_user_bookings(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[Booking]:
        """
        Получить бронирования пользователя.
        
        Args:
            user_id: ID пользователя
            active_only: Только активные (не отмененные)
        
        Returns:
            Список Booking
        """
        booking_ids = self.user_bookings.get(user_id, [])
        bookings = [self.bookings[bid] for bid in booking_ids if bid in self.bookings]
        
        if active_only:
            bookings = [
                b for b in bookings
                if b.status not in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]
            ]
        
        return bookings
    
    def get_bookings_by_date(self, booking_date: date) -> List[Booking]:
        """Получить все бронирования на дату"""
        return [
            booking for booking in self.bookings.values()
            if booking.booking_date == booking_date
            and booking.status != BookingStatus.CANCELLED
        ]
