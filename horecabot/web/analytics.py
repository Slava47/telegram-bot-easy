"""
Веб-панель аналитики
====================

Flask-приложение для администрирования и аналитики.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from functools import wraps
from typing import Optional
import os


def create_analytics_app(
    bot_instance,
    admin_login: str = "admin",
    admin_password: str = "admin123",
    secret_key: Optional[str] = None
):
    """
    Создать Flask-приложение для веб-аналитики.
    
    Args:
        bot_instance: Экземпляр бота (HorecaBot или его потомки)
        admin_login: Логин администратора
        admin_password: Пароль администратора
        secret_key: Секретный ключ для сессий
    
    Returns:
        Flask app
    
    Example:
        >>> from horecabot import RestaurantBot
        >>> from horecabot.web.analytics import create_analytics_app
        >>> 
        >>> bot = RestaurantBot(token="...", name="Мой Ресторан")
        >>> app = create_analytics_app(bot, admin_login="admin", admin_password="secure_pass")
        >>> app.run(host="0.0.0.0", port=5000)
    """
    app = Flask(__name__)
    app.secret_key = secret_key or os.urandom(24)
    
    # Функция проверки авторизации
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Страница входа"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username == admin_login and password == admin_password:
                session['logged_in'] = True
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Неверный логин или пароль")
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Выход"""
        session.pop('logged_in', None)
        return redirect(url_for('login'))
    
    @app.route('/')
    @login_required
    def dashboard():
        """Главная панель аналитики"""
        # Собираем статистику
        stats = {
            'establishment_name': bot_instance.name,
            'establishment_type': bot_instance.establishment_type.value,
            'total_guests': 0,
            'total_orders': 0,
            'total_revenue': 0.0,
            'total_quizzes': 0,
            'total_reviews': 0,
        }
        
        # Если есть модуль лояльности
        if hasattr(bot_instance, 'loyalty_module') and bot_instance.loyalty_module:
            guests = bot_instance.loyalty_module.get_all_guests()
            stats['total_guests'] = len(guests)
            stats['total_orders'] = sum(g.total_orders for g in guests)
            stats['total_revenue'] = sum(g.total_spent for g in guests)
            stats['total_quizzes'] = sum(g.quiz_completions for g in guests)
            stats['total_reviews'] = sum(g.reviews_count for g in guests)
        
        return render_template('dashboard.html', stats=stats)
    
    @app.route('/api/guests')
    @login_required
    def api_guests():
        """API: Список всех гостей"""
        if not hasattr(bot_instance, 'loyalty_module') or not bot_instance.loyalty_module:
            return jsonify([])
        
        guests = bot_instance.loyalty_module.get_all_guests()
        guests_data = [
            {
                'user_id': g.user_id,
                'name': g.name,
                'phone': g.phone,
                'loyalty_level': g.loyalty_level,
                'loyalty_points': g.loyalty_points,
                'total_orders': g.total_orders,
                'total_spent': g.total_spent,
                'quiz_completions': g.quiz_completions,
                'reviews_count': g.reviews_count,
                'last_visit': g.last_visit.isoformat() if g.last_visit else None,
            }
            for g in guests
        ]
        
        return jsonify(guests_data)
    
    @app.route('/api/guests/<int:user_id>')
    @login_required
    def api_guest_detail(user_id):
        """API: Детальная информация о госте"""
        if not hasattr(bot_instance, 'loyalty_module') or not bot_instance.loyalty_module:
            return jsonify({'error': 'Loyalty module not available'}), 404
        
        guest = bot_instance.loyalty_module.get_guest_card(user_id)
        if not guest:
            return jsonify({'error': 'Guest not found'}), 404
        
        return jsonify({
            'user_id': guest.user_id,
            'name': guest.name,
            'phone': guest.phone,
            'email': guest.email,
            'created_at': guest.created_at.isoformat(),
            'loyalty_level': guest.loyalty_level,
            'loyalty_points': guest.loyalty_points,
            'stamps': guest.stamps,
            'total_orders': guest.total_orders,
            'total_spent': guest.total_spent,
            'quiz_completions': guest.quiz_completions,
            'reviews_count': guest.reviews_count,
            'average_rating': guest.average_rating,
            'last_visit': guest.last_visit.isoformat() if guest.last_visit else None,
            'preferences': guest.preferences,
            'favorite_items': guest.favorite_items,
        })
    
    @app.route('/api/menu/popular')
    @login_required
    def api_popular_menu():
        """API: Популярные позиции меню"""
        # Здесь можно добавить логику подсчета популярности на основе заказов
        return jsonify([])
    
    @app.route('/api/bookings/today')
    @login_required
    def api_bookings_today():
        """API: Бронирования на сегодня"""
        if not hasattr(bot_instance, 'booking_module') or not bot_instance.booking_module:
            return jsonify([])
        
        from datetime import date
        today = date.today()
        bookings = bot_instance.booking_module.get_bookings_by_date(today)
        
        bookings_data = [b.to_dict() for b in bookings]
        return jsonify(bookings_data)
    
    @app.route('/guests')
    @login_required
    def guests_page():
        """Страница списка гостей"""
        return render_template('guests.html')
    
    @app.route('/menu')
    @login_required
    def menu_page():
        """Страница управления меню"""
        return render_template('menu.html')
    
    @app.route('/bookings')
    @login_required
    def bookings_page():
        """Страница бронирований"""
        return render_template('bookings.html')
    
    return app


# Простые HTML-шаблоны (для базовой функциональности)
def create_default_templates():
    """Создать базовые HTML-шаблоны"""
    templates = {
        'login.html': """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход - HorecaBot</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
        h2 { text-align: center; color: #333; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: red; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>🍽 HorecaBot</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Логин" required>
            <input type="password" name="password" placeholder="Пароль" required>
            <button type="submit">Войти</button>
        </form>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
        """,
        
        'dashboard.html': """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Панель управления - {{ stats.establishment_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #007bff; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { margin: 0; }
        .nav { background: white; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav a { margin-right: 1rem; text-decoration: none; color: #007bff; }
        .nav a:hover { text-decoration: underline; }
        .container { padding: 2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { margin: 0 0 0.5rem 0; color: #666; font-size: 14px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #007bff; }
        .logout { background: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; }
        .logout:hover { background: #c82333; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🍽 {{ stats.establishment_name }}</h1>
        <a href="/logout" class="logout">Выход</a>
    </div>
    <div class="nav">
        <a href="/">Главная</a>
        <a href="/guests">Гости</a>
        <a href="/menu">Меню</a>
        <a href="/bookings">Бронирования</a>
    </div>
    <div class="container">
        <h2>Статистика</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>Всего гостей</h3>
                <div class="value">{{ stats.total_guests }}</div>
            </div>
            <div class="stat-card">
                <h3>Заказов</h3>
                <div class="value">{{ stats.total_orders }}</div>
            </div>
            <div class="stat-card">
                <h3>Выручка</h3>
                <div class="value">{{ "%.2f"|format(stats.total_revenue) }}₽</div>
            </div>
            <div class="stat-card">
                <h3>Пройдено квизов</h3>
                <div class="value">{{ stats.total_quizzes }}</div>
            </div>
            <div class="stat-card">
                <h3>Отзывов</h3>
                <div class="value">{{ stats.total_reviews }}</div>
            </div>
        </div>
    </div>
</body>
</html>
        """,
        
        'guests.html': """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Гости - HorecaBot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #007bff; color: white; padding: 1rem 2rem; }
        .nav { background: white; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav a { margin-right: 1rem; text-decoration: none; color: #007bff; }
        .container { padding: 2rem; }
        table { width: 100%; background: white; border-collapse: collapse; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header"><h1>👥 Гости</h1></div>
    <div class="nav">
        <a href="/">Главная</a>
        <a href="/guests">Гости</a>
        <a href="/menu">Меню</a>
        <a href="/bookings">Бронирования</a>
    </div>
    <div class="container">
        <h2>Список гостей</h2>
        <table id="guests-table">
            <thead>
                <tr>
                    <th>Имя</th>
                    <th>Телефон</th>
                    <th>Уровень</th>
                    <th>Заказов</th>
                    <th>Потрачено</th>
                    <th>Квизов</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
    <script>
        fetch('/api/guests')
            .then(r => r.json())
            .then(guests => {
                const tbody = document.querySelector('#guests-table tbody');
                guests.forEach(g => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${g.name}</td>
                        <td>${g.phone || '—'}</td>
                        <td>${g.loyalty_level}</td>
                        <td>${g.total_orders}</td>
                        <td>${g.total_spent.toFixed(2)}₽</td>
                        <td>${g.quiz_completions}</td>
                    `;
                });
            });
    </script>
</body>
</html>
        """
    }
    
    return templates
