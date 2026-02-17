"""
Tests for State Management
===========================

Tests for the state management system.
"""

import unittest
from horecabot.core.states import StateManager, UserState, StateContext
from datetime import datetime, timedelta


class TestStateManager(unittest.TestCase):
    """Tests for StateManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = StateManager(default_timeout=10)
    
    def test_set_and_get_state(self):
        """Test setting and getting state"""
        user_id = 12345
        
        self.state_manager.set_state(user_id, UserState.BROWSING_MENU)
        state = self.state_manager.get_state(user_id)
        
        self.assertEqual(state, UserState.BROWSING_MENU)
    
    def test_default_state(self):
        """Test default state is IDLE"""
        state = self.state_manager.get_state(99999)
        self.assertEqual(state, UserState.IDLE)
    
    def test_context_data(self):
        """Test storing and retrieving context data"""
        user_id = 12345
        
        self.state_manager.set_state(
            user_id,
            UserState.BROWSING_MENU,
            category="main_dishes"
        )
        
        context = self.state_manager.get_context(user_id)
        self.assertIsNotNone(context)
        self.assertEqual(context.get_data("category"), "main_dishes")
    
    def test_update_context(self):
        """Test updating context data"""
        user_id = 12345
        
        self.state_manager.set_state(user_id, UserState.IN_CART)
        self.state_manager.update_context(user_id, item_count=3, total=1500.0)
        
        context = self.state_manager.get_context(user_id)
        self.assertEqual(context.get_data("item_count"), 3)
        self.assertEqual(context.get_data("total"), 1500.0)
    
    def test_reset_state(self):
        """Test resetting state to IDLE"""
        user_id = 12345
        
        self.state_manager.set_state(user_id, UserState.BROWSING_MENU)
        self.assertEqual(self.state_manager.get_state(user_id), UserState.BROWSING_MENU)
        
        self.state_manager.reset_state(user_id)
        self.assertEqual(self.state_manager.get_state(user_id), UserState.IDLE)
    
    def test_go_back(self):
        """Test going back to previous state"""
        user_id = 12345
        
        self.state_manager.set_state(user_id, UserState.BROWSING_MENU)
        self.state_manager.set_state(user_id, UserState.VIEWING_ITEM)
        
        # Go back
        result = self.state_manager.go_back(user_id)
        self.assertTrue(result)
        
        state = self.state_manager.get_state(user_id)
        self.assertEqual(state, UserState.BROWSING_MENU)
    
    def test_state_expiration(self):
        """Test state expiration"""
        user_id = 12345
        
        # Set state with very short timeout
        self.state_manager.set_state(
            user_id,
            UserState.BROWSING_MENU,
            timeout=1  # 1 second
        )
        
        # State should exist
        self.assertEqual(self.state_manager.get_state(user_id), UserState.BROWSING_MENU)
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # State should be reset to IDLE
        self.assertEqual(self.state_manager.get_state(user_id), UserState.IDLE)
    
    def test_cleanup_expired(self):
        """Test cleanup of expired states"""
        user_id1 = 12345
        user_id2 = 67890
        
        # Set expired state
        self.state_manager.set_state(user_id1, UserState.BROWSING_MENU, timeout=1)
        
        # Set non-expired state
        self.state_manager.set_state(user_id2, UserState.IN_CART, timeout=60)
        
        # Wait for first one to expire
        import time
        time.sleep(2)
        
        # Cleanup
        self.state_manager.cleanup_expired()
        
        # First should be gone, second should remain
        self.assertEqual(self.state_manager.get_state(user_id1), UserState.IDLE)
        self.assertEqual(self.state_manager.get_state(user_id2), UserState.IN_CART)
    
    def test_get_users_in_state(self):
        """Test getting users in specific state"""
        user_id1 = 12345
        user_id2 = 67890
        user_id3 = 11111
        
        self.state_manager.set_state(user_id1, UserState.BROWSING_MENU)
        self.state_manager.set_state(user_id2, UserState.BROWSING_MENU)
        self.state_manager.set_state(user_id3, UserState.IN_CART)
        
        users_browsing = self.state_manager.get_users_in_state(UserState.BROWSING_MENU)
        self.assertEqual(len(users_browsing), 2)
        self.assertIn(user_id1, users_browsing)
        self.assertIn(user_id2, users_browsing)
        
        users_in_cart = self.state_manager.get_users_in_state(UserState.IN_CART)
        self.assertEqual(len(users_in_cart), 1)
        self.assertIn(user_id3, users_in_cart)


class TestStateContext(unittest.TestCase):
    """Tests for StateContext"""
    
    def test_context_creation(self):
        """Test creating a context"""
        context = StateContext(state=UserState.BROWSING_MENU)
        self.assertEqual(context.state, UserState.BROWSING_MENU)
        self.assertIsNotNone(context.created_at)
    
    def test_context_data_operations(self):
        """Test data operations on context"""
        context = StateContext(state=UserState.IN_CART)
        
        context.set_data("item_id", "item_123")
        context.set_data("quantity", 2)
        
        self.assertEqual(context.get_data("item_id"), "item_123")
        self.assertEqual(context.get_data("quantity"), 2)
        self.assertIsNone(context.get_data("non_existent"))
    
    def test_context_clear_data(self):
        """Test clearing context data"""
        context = StateContext(
            state=UserState.IN_CART,
            data={"item_id": "123", "quantity": 2}
        )
        
        self.assertEqual(len(context.data), 2)
        
        context.clear_data()
        self.assertEqual(len(context.data), 0)


if __name__ == '__main__':
    unittest.main()
