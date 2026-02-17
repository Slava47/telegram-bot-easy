# Changelog

All notable changes to HorecaBot will be documented in this file.

## [1.1.0] - 2024-02-17

### Added - Core Infrastructure

#### State Management System (`horecabot.core.states`)
- **StateManager** class for managing user conversation states
- Support for 20+ predefined states (browsing, ordering, booking, quiz, etc.)
- **StateContext** with automatic expiration and data storage
- Ability to go back to previous states
- Batch operations to get users in specific states

#### Input Validation (`horecabot.core.validation`)
- **validate_phone()** - Russian phone number validation
- **validate_email()** - Email validation with RFC compliance
- **validate_date()** - Date validation with future date checks
- **validate_time()** - Time format validation
- **validate_integer()** - Integer with range validation
- **validate_float()** - Float with range validation
- **validate_rating()** - Rating (1-5) validation
- **sanitize_input()** - HTML and control character removal
- **ValidationError** exception for validation failures
- **ErrorHandler** class with user-friendly error messages

#### Telegram API Wrapper (`horecabot.core.telegram_api`)
- **TelegramAPIWrapper** with automatic retry logic
- Configurable timeout and retry parameters
- Exponential backoff for failed requests
- Rate limiting to respect Telegram limits (~30 req/sec)
- Automatic handling of 429 (rate limit) errors
- Structured error types: TelegramError, TelegramTimeoutError, TelegramRateLimitError

#### Multi-Language Support (`horecabot.core.i18n`)
- **I18n** class for internationalization
- Support for 7 languages: Russian, English, Spanish, German, French, Italian, Chinese
- Per-user language preferences
- 30+ pre-translated common phrases
- Template string support with variable substitution

#### Menu Caching System (`horecabot.core.cache`)
- **MenuCache** for general-purpose caching with TTL
- **SmartMenuCache** with automatic dependency invalidation
- LRU eviction policy
- Cache statistics (hits, misses, hit rate)
- Automatic cleanup of expired entries

#### Advanced Callback Routing (`horecabot.core.callbacks`)
- **CallbackRouter** with pattern matching support
- **CallbackData** structured format (action:entity:id:params)
- **CallbackBuilder** helper for creating callback strings
- Middleware support for pre-processing
- Global error handler for callbacks
- Regex pattern support for flexible routing
- Built-in pagination and confirmation button builders

### Improved - Modules

#### Menu Module (`horecabot.modules.menu`)
- Added optional menu caching with automatic invalidation
- **Order.can_be_cancelled()** - Check if order can be cancelled
- **Order.cancel()** - Cancel order with reason tracking
- **OrderModule.cancel_order()** - Cancel order with validation
- **OrderModule.get_user_active_orders()** - Get only active orders
- **OrderModule.get_order_history()** - Get order history with limit
- Track order update timestamps and cancellation details

#### Quiz Module (`horecabot.modules.quiz`)
- Added recommendations caching to avoid repeated searches
- Track quiz completion times and durations
- **QuizSession.get_duration()** - Calculate quiz completion time
- **QuizModule.get_quiz_stats()** - Get statistics per quiz
- **QuizModule.get_all_quizzes_stats()** - Get all quiz statistics
- Automatic cache invalidation on session completion

#### Loyalty Module
- Already had comprehensive features (no changes needed)
- Works seamlessly with new state management

#### Booking Module  
- Already had comprehensive features (no changes needed)
- Works seamlessly with new state management

### Added - Web Templates

Created professional dashboard templates for each bot type:
- **base.html** - Base template with responsive design
- **dashboard_restaurant.html** - Restaurant-specific dashboard
- **dashboard_hotel.html** - Hotel-specific dashboard  
- **dashboard_cafe.html** - Cafe-specific dashboard
- **dashboard_bar.html** - Bar-specific dashboard
- **dashboard_fastfood.html** - Fast food-specific dashboard

Features:
- Responsive grid layouts
- Statistics cards with gradient backgrounds
- Professional table styling
- Badge system for statuses
- Empty state placeholders
- Consistent color scheme and typography

### Added - Documentation

#### API Reference (`docs/API.md`)
- Complete API documentation for all core modules
- Usage examples for each class and method
- Parameter descriptions and return types
- Code snippets for common use cases
- Examples for all bot types

#### Module Guide (`docs/MODULES.md`)
- Comprehensive guide for each module (7000+ words)
- Real-world usage examples
- Integration patterns
- Best practices
- Troubleshooting tips

### Added - Testing

Created comprehensive test suites:
- **test_states.py** - 12 tests for state management
- **test_validation.py** - 21 tests for validation functions
- **test_loyalty_extended.py** - 16 tests for loyalty module
- **test_horecabot.py** - Existing 12 tests

**Total: 61 tests, all passing**

Test coverage:
- State transitions and expiration
- Context data management
- All validation functions
- Loyalty points, stamps, and levels
- Guest card operations
- Error handling

### Added - Examples

#### advanced_restaurant_example.py
Complete example demonstrating:
- Proper callback routing with patterns
- State management for multi-step flows
- Error handling with user-friendly messages
- Input validation
- Menu browsing with inline buttons
- Shopping cart management
- Loyalty program integration
- Clean code structure

### Changed

#### Core Base (`horecabot.core.base`)
- No breaking changes
- Fully compatible with new modules

### Technical Improvements

#### Type Hints
- Added type hints to all new modules
- Improved IDE autocomplete support
- Better code documentation through types

#### Logging
- Added structured logging in TelegramAPIWrapper
- Added logging in CallbackRouter
- Consistent log format across modules

#### Error Handling
- Unified error handling approach
- User-friendly error messages
- Automatic error recovery where possible

#### Performance
- Menu caching reduces database queries
- Smart cache invalidation prevents stale data
- LRU eviction prevents memory bloat
- Rate limiting prevents API throttling

### Security

#### Input Sanitization
- HTML tag removal from user input
- Control character filtering
- Prevention of XSS attacks

#### Validation
- Phone number format validation
- Email format validation
- Integer range checks
- Prevention of invalid data

---

## [1.0.0] - 2024-01-01

Initial release with:
- Base bot classes for 5 establishment types
- Menu and order management
- Booking system
- Quiz module
- Loyalty program
- Basic web analytics

---

## Migration Guide from 1.0.0 to 1.1.0

### No Breaking Changes

Version 1.1.0 is fully backward compatible with 1.0.0. Existing code will continue to work without modifications.

### Recommended Updates

1. **Add State Management** (Optional but recommended):
   ```python
   from horecabot.core.states import StateManager, UserState
   
   state_manager = StateManager()
   ```

2. **Use Callback Router** (Optional but recommended):
   ```python
   from horecabot.core.callbacks import CallbackRouter, CallbackBuilder
   
   router = CallbackRouter()
   
   @router.callback("view:menu:*")
   async def view_menu(update, callback_data):
       # Handle callback
   ```

3. **Enable Menu Caching** (Recommended for better performance):
   ```python
   menu = MenuModule(enable_cache=True)
   quiz = QuizModule(menu_module=menu, enable_cache=True)
   ```

4. **Add Input Validation** (Recommended for better UX):
   ```python
   from horecabot.core.validation import validate_phone, sanitize_input
   
   valid, error = validate_phone(phone_input)
   if not valid:
       await bot.send_message(chat_id, error)
   ```

### New Features to Try

- Multi-language support with `I18n`
- Order cancellation with `OrderModule.cancel_order()`
- Quiz statistics with `QuizModule.get_quiz_stats()`
- Advanced callback routing with patterns

---

## Roadmap

### Version 1.2.0 (Planned)
- Database persistence layer (SQLAlchemy)
- Configuration management system
- Integration tests
- Webhook support (alternative to polling)
- Payment provider integrations

### Version 2.0.0 (Future)
- Web-based admin panel
- Real-time order tracking
- Push notifications
- Advanced analytics
- Mobile app integration

---

## Contributors

- HorecaBot Team
- Community contributors (thank you!)

## License

MIT License - see [LICENSE](LICENSE) file for details
