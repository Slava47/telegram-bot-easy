"""
Extended Tests for Loyalty Module
==================================

Comprehensive tests for the loyalty system.
"""

import unittest
from horecabot.modules.loyalty import (
    LoyaltyModule, LoyaltyType, GuestCard
)


class TestLoyaltyModulePoints(unittest.TestCase):
    """Tests for points-based loyalty program"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loyalty = LoyaltyModule(
            loyalty_type=LoyaltyType.POINTS,
            points_per_ruble=0.1  # 10% cashback
        )
    
    def test_create_guest_card(self):
        """Test creating a guest card"""
        card = self.loyalty.create_guest_card(
            user_id=123456,
            name="Ivan Ivanov",
            phone="+79991234567",
            email="ivan@example.com"
        )
        
        self.assertIsNotNone(card)
        self.assertEqual(card.user_id, 123456)
        self.assertEqual(card.name, "Ivan Ivanov")
        self.assertEqual(card.phone, "+79991234567")
        self.assertEqual(card.email, "ivan@example.com")
        self.assertEqual(card.loyalty_points, 0)
        self.assertEqual(card.total_orders, 0)
    
    def test_process_order_points(self):
        """Test processing an order with points"""
        self.loyalty.create_guest_card(user_id=123456, name="Test User")
        
        # Process order
        self.loyalty.process_order(
            user_id=123456,
            order_amount=1000.0,
            item_ids=["item1", "item2"]
        )
        
        card = self.loyalty.get_guest_card(123456)
        
        # Check points (10% of 1000 = 100 points)
        self.assertEqual(card.loyalty_points, 100)
        self.assertEqual(card.total_orders, 1)
        self.assertEqual(card.total_spent, 1000.0)
    
    def test_multiple_orders(self):
        """Test multiple orders accumulation"""
        self.loyalty.create_guest_card(user_id=123456, name="Test User")
        
        # First order
        self.loyalty.process_order(123456, 1000.0, ["item1"])
        
        # Second order
        self.loyalty.process_order(123456, 500.0, ["item2"])
        
        card = self.loyalty.get_guest_card(123456)
        
        self.assertEqual(card.loyalty_points, 150)  # 100 + 50
        self.assertEqual(card.total_orders, 2)
        self.assertEqual(card.total_spent, 1500.0)
    
    def test_spend_points(self):
        """Test spending loyalty points"""
        card = self.loyalty.create_guest_card(user_id=123456, name="Test User")
        card.add_points(500)
        
        # Spend 200 points
        success = card.spend_points(200)
        self.assertTrue(success)
        self.assertEqual(card.loyalty_points, 300)
        
        # Try to spend more than available
        success = card.spend_points(400)
        self.assertFalse(success)
        self.assertEqual(card.loyalty_points, 300)  # Should remain unchanged


class TestLoyaltyModuleStamps(unittest.TestCase):
    """Tests for stamps-based loyalty program"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loyalty = LoyaltyModule(
            loyalty_type=LoyaltyType.STAMPS,
            stamps_for_reward=6  # 6th coffee free
        )
    
    def test_process_order_stamps(self):
        """Test processing an order with stamps"""
        self.loyalty.create_guest_card(user_id=123456, name="Test User")
        
        # Process order - should get 1 stamp
        self.loyalty.process_order(123456, 250.0, ["coffee"])
        
        card = self.loyalty.get_guest_card(123456)
        self.assertEqual(card.stamps, 1)
    
    def test_reward_available(self):
        """Test checking if reward is available"""
        card = self.loyalty.create_guest_card(user_id=123456, name="Test User")
        
        # Add stamps one by one
        for i in range(5):
            card.add_stamp()
            available = self.loyalty.check_reward_available(123456)
            self.assertFalse(available)
        
        # 6th stamp - reward should be available
        card.add_stamp()
        available = self.loyalty.check_reward_available(123456)
        self.assertTrue(available)
    
    def test_claim_reward(self):
        """Test claiming a reward"""
        card = self.loyalty.create_guest_card(user_id=123456, name="Test User")
        
        # Add 6 stamps
        for i in range(6):
            card.add_stamp()
        
        # Claim reward
        success = self.loyalty.claim_reward(123456)
        self.assertTrue(success)
        
        # Stamps should be reset
        self.assertEqual(card.stamps, 0)


class TestLoyaltyModuleLevels(unittest.TestCase):
    """Tests for levels-based loyalty program"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loyalty = LoyaltyModule(loyalty_type=LoyaltyType.LEVELS)
    
    def test_level_progression(self):
        """Test progression through loyalty levels"""
        card = self.loyalty.create_guest_card(user_id=123456, name="Test User")
        
        # Start at bronze
        self.assertEqual(card.loyalty_level, "bronze")
        
        # Process orders to reach silver (20,000)
        self.loyalty.process_order(123456, 20000.0, ["item1"])
        self.assertEqual(card.loyalty_level, "silver")
        
        # Reach gold (50,000)
        self.loyalty.process_order(123456, 30000.0, ["item2"])
        self.assertEqual(card.loyalty_level, "gold")
        
        # Reach platinum (100,000)
        self.loyalty.process_order(123456, 50000.0, ["item3"])
        self.assertEqual(card.loyalty_level, "platinum")


class TestGuestCard(unittest.TestCase):
    """Tests for GuestCard class"""
    
    def test_add_order(self):
        """Test adding order to guest card"""
        card = GuestCard(user_id=123456, name="Test User")
        
        card.add_order(1000.0, ["item1", "item2"])
        
        self.assertEqual(card.total_orders, 1)
        self.assertEqual(card.total_spent, 1000.0)
        self.assertIsNotNone(card.last_visit)
        self.assertIn("item1", card.favorite_items)
        self.assertIn("item2", card.favorite_items)
    
    def test_add_quiz_completion(self):
        """Test adding quiz completion"""
        card = GuestCard(user_id=123456, name="Test User")
        
        card.add_quiz_completion(["sweet", "dessert", "chocolate"])
        
        self.assertEqual(card.quiz_completions, 1)
        self.assertIn("sweet", card.preferences)
        self.assertIn("dessert", card.preferences)
        self.assertIn("chocolate", card.preferences)
    
    def test_add_review(self):
        """Test adding review"""
        card = GuestCard(user_id=123456, name="Test User")
        
        # Add first review (5 stars)
        card.add_review(5.0)
        self.assertEqual(card.reviews_count, 1)
        self.assertEqual(card.average_rating, 5.0)
        
        # Add second review (3 stars)
        card.add_review(3.0)
        self.assertEqual(card.reviews_count, 2)
        self.assertEqual(card.average_rating, 4.0)  # (5 + 3) / 2
    
    def test_update_level(self):
        """Test manual level update"""
        card = GuestCard(user_id=123456, name="Test User")
        
        card.total_spent = 25000.0
        card.update_level()
        self.assertEqual(card.loyalty_level, "silver")
        
        card.total_spent = 60000.0
        card.update_level()
        self.assertEqual(card.loyalty_level, "gold")


class TestLoyaltyModuleAnalytics(unittest.TestCase):
    """Tests for loyalty analytics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loyalty = LoyaltyModule(loyalty_type=LoyaltyType.POINTS)
    
    def test_get_top_guests(self):
        """Test getting top guests by spending"""
        # Create multiple guests
        for i in range(5):
            card = self.loyalty.create_guest_card(
                user_id=i,
                name=f"User {i}"
            )
            # Give them different spending amounts
            card.total_spent = (i + 1) * 1000.0
        
        # Get top 3
        top_guests = self.loyalty.get_top_guests(limit=3)
        
        self.assertEqual(len(top_guests), 3)
        # Should be sorted by total_spent (highest first)
        self.assertEqual(top_guests[0].user_id, 4)  # 5000
        self.assertEqual(top_guests[1].user_id, 3)  # 4000
        self.assertEqual(top_guests[2].user_id, 2)  # 3000
    
    def test_get_all_guests(self):
        """Test getting all guests"""
        # Create guests
        for i in range(3):
            self.loyalty.create_guest_card(user_id=i, name=f"User {i}")
        
        all_guests = self.loyalty.get_all_guests()
        self.assertEqual(len(all_guests), 3)


if __name__ == '__main__':
    unittest.main()
