"""
Тесты для HorecaBot
===================

Базовые тесты для проверки функциональности библиотеки.
"""

import unittest
from horecabot import RestaurantBot, HotelBot, CafeBot, BarBot, FastFoodBot
from horecabot.core import EstablishmentType
from horecabot.modules import (
    MenuModule, MenuItem,
    OrderModule,
    BookingModule, BookingType, Resource,
    QuizModule, Quiz, QuizQuestion,
    LoyaltyModule, LoyaltyType, GuestCard
)
from datetime import date, time


class TestHorecaBotBasics(unittest.TestCase):
    """Базовые тесты для HorecaBot"""
    
    def test_restaurant_bot_initialization(self):
        """Тест инициализации RestaurantBot"""
        bot = RestaurantBot(
            token="test_token",
            name="Test Restaurant",
            timezone="Europe/Moscow",
            currency="₽"
        )
        
        self.assertEqual(bot.name, "Test Restaurant")
        self.assertEqual(bot.currency, "₽")
        self.assertEqual(bot.establishment_type, EstablishmentType.RESTAURANT)
    
    def test_all_bot_types(self):
        """Тест инициализации всех типов ботов"""
        bots = [
            RestaurantBot(token="test", name="Restaurant"),
            HotelBot(token="test", name="Hotel"),
            CafeBot(token="test", name="Cafe"),
            BarBot(token="test", name="Bar"),
            FastFoodBot(token="test", name="FastFood"),
        ]
        
        for bot in bots:
            self.assertIsNotNone(bot)
            self.assertIsNotNone(bot.name)


class TestMenuModule(unittest.TestCase):
    """Тесты для MenuModule"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.menu = MenuModule()
    
    def test_add_category(self):
        """Тест добавления категории"""
        self.menu.add_category("salads", "Салаты", emoji="🥗")
        self.assertIn("salads", self.menu.categories)
    
    def test_add_item(self):
        """Тест добавления позиции"""
        item = MenuItem(
            id="caesar",
            name="Цезарь",
            description="Салат",
            price=450.0,
            category="salads",
            tags=["салат", "курица"]
        )
        
        self.menu.add_item(item)
        self.assertIn("caesar", self.menu.items)
        
        retrieved = self.menu.get_item("caesar")
        self.assertEqual(retrieved.name, "Цезарь")
        self.assertEqual(retrieved.price, 450.0)
    
    def test_search_by_tags(self):
        """Тест поиска по тегам"""
        # Добавляем несколько позиций
        items = [
            MenuItem(id="1", name="Item 1", description="", price=100, category="test", tags=["tag1", "tag2"]),
            MenuItem(id="2", name="Item 2", description="", price=200, category="test", tags=["tag2", "tag3"]),
            MenuItem(id="3", name="Item 3", description="", price=300, category="test", tags=["tag3"]),
        ]
        
        for item in items:
            self.menu.add_item(item)
        
        # Поиск по тегам
        results = self.menu.search_by_tags(["tag1", "tag2"], limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, "1")  # Больше совпадений


class TestOrderModule(unittest.TestCase):
    """Тесты для OrderModule"""
    
    def setUp(self):
        self.orders = OrderModule()
        self.item = MenuItem(
            id="test_item",
            name="Test",
            description="",
            price=100.0,
            category="test"
        )
    
    def test_create_order(self):
        """Тест создания заказа"""
        order = self.orders.create_order(user_id=123)
        self.assertIsNotNone(order)
        self.assertEqual(order.user_id, 123)
    
    def test_add_item_to_order(self):
        """Тест добавления позиции в заказ"""
        order = self.orders.create_order(user_id=123)
        order.add_item(self.item, quantity=2)
        
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)
        self.assertEqual(order.subtotal, 200.0)
    
    def test_confirm_order(self):
        """Тест подтверждения заказа"""
        order = self.orders.create_order(user_id=123)
        order.add_item(self.item, quantity=1)
        
        self.orders.confirm_order(order.id)
        
        confirmed = self.orders.get_order(order.id)
        self.assertEqual(confirmed.status, "confirmed")


class TestBookingModule(unittest.TestCase):
    """Тесты для BookingModule"""
    
    def setUp(self):
        self.booking = BookingModule()
        self.booking.set_working_hours(
            opening=time(10, 0),
            closing=time(22, 0),
            slot_duration=60
        )
        
        # Добавляем столики
        for i in range(1, 6):
            table = Resource(
                id=f"table_{i}",
                name=f"Столик {i}",
                resource_type=BookingType.TABLE,
                capacity=4
            )
            self.booking.add_resource(table)
    
    def test_add_resource(self):
        """Тест добавления ресурса"""
        self.assertEqual(len(self.booking.resources), 5)
    
    def test_get_available_slots(self):
        """Тест получения доступных слотов"""
        today = date.today()
        slots = self.booking.get_available_slots(today)
        
        self.assertGreater(len(slots), 0)
    
    def test_create_booking(self):
        """Тест создания бронирования"""
        today = date.today()
        slots = self.booking.get_available_slots(today)
        
        reservation = self.booking.create_booking(
            user_id=123,
            user_name="Test User",
            user_phone="+79991234567",
            booking_type=BookingType.TABLE,
            booking_date=today,
            guests_count=4,
            time_slot=slots[0]
        )
        
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.guests_count, 4)


class TestQuizModule(unittest.TestCase):
    """Тесты для QuizModule"""
    
    def setUp(self):
        self.menu = MenuModule()
        self.quiz_module = QuizModule(menu_module=self.menu)
        
        # Добавляем позиции с тегами
        self.menu.add_item(MenuItem(
            id="item1",
            name="Sweet Item",
            description="",
            price=100,
            category="test",
            tags=["sweet", "dessert"]
        ))
        
        # Создаем квиз
        self.quiz = Quiz(id="test_quiz", name="Test Quiz", description="")
        q1 = QuizQuestion(id="q1", text="Test question?")
        q1.add_answer("Sweet", ["sweet"])
        q1.add_answer("Sour", ["sour"])
        self.quiz.add_question(q1)
        
        self.quiz_module.add_quiz(self.quiz)
    
    def test_start_quiz(self):
        """Тест начала квиза"""
        session = self.quiz_module.start_quiz(user_id=123, quiz_id="test_quiz")
        self.assertIsNotNone(session)
        self.assertEqual(session.quiz_id, "test_quiz")
    
    def test_answer_question(self):
        """Тест ответа на вопрос"""
        self.quiz_module.start_quiz(user_id=123, quiz_id="test_quiz")
        continues = self.quiz_module.answer_question(user_id=123, tags=["sweet"])
        
        self.assertFalse(continues)  # Квиз из одного вопроса завершен
    
    def test_get_recommendations(self):
        """Тест получения рекомендаций"""
        self.quiz_module.start_quiz(user_id=123, quiz_id="test_quiz")
        self.quiz_module.answer_question(user_id=123, tags=["sweet"])
        
        recommendations = self.quiz_module.get_recommendations(user_id=123)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, "item1")


class TestLoyaltyModule(unittest.TestCase):
    """Тесты для LoyaltyModule"""
    
    def setUp(self):
        self.loyalty = LoyaltyModule(
            loyalty_type=LoyaltyType.POINTS,
            points_per_ruble=0.1
        )
    
    def test_create_guest_card(self):
        """Тест создания карточки гостя"""
        card = self.loyalty.create_guest_card(
            user_id=123,
            name="Test User",
            phone="+79991234567"
        )
        
        self.assertEqual(card.user_id, 123)
        self.assertEqual(card.name, "Test User")
        self.assertEqual(card.loyalty_points, 0)
    
    def test_process_order(self):
        """Тест обработки заказа"""
        self.loyalty.create_guest_card(user_id=123, name="Test")
        
        self.loyalty.process_order(
            user_id=123,
            order_amount=1000.0,
            item_ids=["item1"]
        )
        
        card = self.loyalty.get_guest_card(123)
        self.assertEqual(card.loyalty_points, 100)  # 10% от 1000
        self.assertEqual(card.total_orders, 1)
        self.assertEqual(card.total_spent, 1000.0)


if __name__ == '__main__':
    unittest.main()
