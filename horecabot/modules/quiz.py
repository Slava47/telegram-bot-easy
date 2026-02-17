"""
Модуль интерактивного подбора (квиз)
=====================================

Создание тестов для подбора блюд и напитков.
Вдохновлено проектом «Ли Бо».
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QuizQuestion:
    """
    Вопрос квиза.
    
    Attributes:
        id: Уникальный идентификатор вопроса
        text: Текст вопроса
        answers: Список вариантов ответов с тегами
    """
    id: str
    text: str
    answers: List[Dict[str, any]] = field(default_factory=list)
    # Формат answer: {"text": "Сладкий", "tags": ["sweet", "dessert"]}
    
    def add_answer(self, text: str, tags: List[str]):
        """Добавить вариант ответа"""
        self.answers.append({"text": text, "tags": tags})


@dataclass
class Quiz:
    """
    Квиз для подбора.
    
    Attributes:
        id: Уникальный идентификатор квиза
        name: Название квиза
        description: Описание
        questions: Список вопросов
        category: Категория меню для подбора (опционально)
    """
    id: str
    name: str
    description: str
    questions: List[QuizQuestion] = field(default_factory=list)
    category: Optional[str] = None
    
    def add_question(self, question: QuizQuestion):
        """Добавить вопрос в квиз"""
        self.questions.append(question)


@dataclass
class QuizSession:
    """
    Сессия прохождения квиза пользователем.
    
    Attributes:
        user_id: ID пользователя Telegram
        quiz_id: ID квиза
        current_question: Индекс текущего вопроса
        answers: Выбранные ответы (теги)
        completed: Завершен ли квиз
        started_at: Время начала
        completed_at: Время завершения
    """
    user_id: int
    quiz_id: str
    current_question: int = 0
    answers: List[str] = field(default_factory=list)
    completed: bool = False
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def add_answer(self, tags: List[str]):
        """Добавить ответ (теги) на текущий вопрос"""
        self.answers.extend(tags)
        self.current_question += 1
    
    def complete(self):
        """Завершить квиз"""
        self.completed = True
        self.completed_at = datetime.now()
    
    def get_duration(self) -> Optional[float]:
        """
        Получить длительность прохождения квиза в секундах.
        
        Returns:
            Длительность или None если не завершен
        """
        if not self.completed or not self.completed_at:
            return None
        
        return (self.completed_at - self.started_at).total_seconds()


class QuizModule:
    """
    Модуль интерактивного подбора.
    
    Позволяет создавать квизы, проводить тестирование
    и подбирать блюда/напитки на основе ответов.
    
    Example:
        >>> quiz_module = QuizModule()
        >>> 
        >>> # Создаем квиз для подбора коктейля
        >>> quiz = Quiz(
        ...     id="cocktail_quiz",
        ...     name="Подбери свой коктейль",
        ...     description="Ответьте на несколько вопросов"
        ... )
        >>> 
        >>> # Добавляем вопрос
        >>> q1 = QuizQuestion(id="q1", text="Какой вкус предпочитаете?")
        >>> q1.add_answer("Сладкий", ["sweet", "dessert"])
        >>> q1.add_answer("Кислый", ["sour", "citrus"])
        >>> q1.add_answer("Горький", ["bitter", "strong"])
        >>> quiz.add_question(q1)
        >>> 
        >>> quiz_module.add_quiz(quiz)
        >>> 
        >>> # Начинаем квиз для пользователя
        >>> session = quiz_module.start_quiz(user_id=123456, quiz_id="cocktail_quiz")
    """
    
    def __init__(self, menu_module=None, enable_cache: bool = True):
        """
        Инициализация модуля квизов.
        
        Args:
            menu_module: Ссылка на MenuModule для подбора позиций
            enable_cache: Включить кэширование результатов
        """
        self.quizzes: Dict[str, Quiz] = {}  # quiz_id -> Quiz
        self.sessions: Dict[int, QuizSession] = {}  # user_id -> QuizSession
        self.menu_module = menu_module
        
        # Статистика
        self.completed_count: Dict[int, int] = {}  # user_id -> количество пройденных квизов
        self.quiz_completion_times: Dict[str, List[float]] = {}  # quiz_id -> [durations]
        
        # Кэширование
        self.enable_cache = enable_cache
        self._recommendations_cache: Dict[int, List[Any]] = {}  # user_id -> recommendations
    
    def add_quiz(self, quiz: Quiz):
        """
        Добавить квиз.
        
        Args:
            quiz: Объект Quiz
        """
        self.quizzes[quiz.id] = quiz
    
    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Получить квиз по ID"""
        return self.quizzes.get(quiz_id)
    
    def start_quiz(self, user_id: int, quiz_id: str) -> Optional[QuizSession]:
        """
        Начать прохождение квиза.
        
        Args:
            user_id: ID пользователя Telegram
            quiz_id: ID квиза
        
        Returns:
            Объект QuizSession или None, если квиз не найден
        """
        if quiz_id not in self.quizzes:
            return None
        
        session = QuizSession(user_id=user_id, quiz_id=quiz_id)
        self.sessions[user_id] = session
        return session
    
    def get_session(self, user_id: int) -> Optional[QuizSession]:
        """Получить активную сессию пользователя"""
        return self.sessions.get(user_id)
    
    def answer_question(self, user_id: int, tags: List[str]) -> bool:
        """
        Ответить на текущий вопрос.
        
        Args:
            user_id: ID пользователя
            tags: Теги выбранного ответа
        
        Returns:
            True, если квиз продолжается, False если завершен
        """
        session = self.sessions.get(user_id)
        if not session:
            return False
        
        quiz = self.quizzes.get(session.quiz_id)
        if not quiz:
            return False
        
        # Добавляем ответ
        session.add_answer(tags)
        
        # Проверяем, закончились ли вопросы
        if session.current_question >= len(quiz.questions):
            session.complete()
            
            # Обновляем статистику
            self.completed_count[user_id] = self.completed_count.get(user_id, 0) + 1
            
            # Записываем время прохождения
            duration = session.get_duration()
            if duration:
                if session.quiz_id not in self.quiz_completion_times:
                    self.quiz_completion_times[session.quiz_id] = []
                self.quiz_completion_times[session.quiz_id].append(duration)
            
            return False
        
        return True
    
    def get_current_question(self, user_id: int) -> Optional[QuizQuestion]:
        """
        Получить текущий вопрос для пользователя.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Объект QuizQuestion или None
        """
        session = self.sessions.get(user_id)
        if not session:
            return None
        
        quiz = self.quizzes.get(session.quiz_id)
        if not quiz:
            return None
        
        if session.current_question >= len(quiz.questions):
            return None
        
        return quiz.questions[session.current_question]
    
    def get_recommendations(self, user_id: int, limit: int = 3) -> List:
        """
        Получить рекомендации по результатам квиза.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество рекомендаций
        
        Returns:
            Список рекомендованных позиций меню
        """
        # Проверяем кэш
        if self.enable_cache and user_id in self._recommendations_cache:
            cached = self._recommendations_cache[user_id]
            return cached[:limit]
        
        session = self.sessions.get(user_id)
        if not session or not session.completed:
            return []
        
        if not self.menu_module:
            return []
        
        # Подбираем позиции по тегам
        recommendations = self.menu_module.search_by_tags(
            tags=session.answers,
            limit=limit
        )
        
        # Кэшируем результат
        if self.enable_cache:
            self._recommendations_cache[user_id] = recommendations
        
        return recommendations
    
    def complete_quiz(self, user_id: int):
        """
        Завершить квиз и удалить сессию.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self.sessions:
            del self.sessions[user_id]
        
        # Очищаем кэш рекомендаций
        if user_id in self._recommendations_cache:
            del self._recommendations_cache[user_id]
    
    def get_user_quiz_count(self, user_id: int) -> int:
        """Получить количество пройденных пользователем квизов"""
        return self.completed_count.get(user_id, 0)
    
    def get_quiz_stats(self, quiz_id: str) -> Dict[str, Any]:
        """
        Получить статистику по квизу.
        
        Args:
            quiz_id: ID квиза
        
        Returns:
            Словарь со статистикой
        """
        quiz = self.quizzes.get(quiz_id)
        if not quiz:
            return {}
        
        completion_times = self.quiz_completion_times.get(quiz_id, [])
        
        stats = {
            "quiz_id": quiz_id,
            "quiz_name": quiz.name,
            "total_completions": len(completion_times),
            "questions_count": len(quiz.questions),
        }
        
        if completion_times:
            stats["avg_completion_time"] = sum(completion_times) / len(completion_times)
            stats["min_completion_time"] = min(completion_times)
            stats["max_completion_time"] = max(completion_times)
        
        return stats
    
    def get_all_quizzes_stats(self) -> List[Dict[str, Any]]:
        """
        Получить статистику по всем квизам.
        
        Returns:
            Список словарей со статистикой
        """
        return [
            self.get_quiz_stats(quiz_id)
            for quiz_id in self.quizzes.keys()
        ]


# Пример готового квиза для коктейлей
def create_cocktail_quiz() -> Quiz:
    """
    Создать готовый квиз для подбора коктейля.
    
    Returns:
        Объект Quiz
    """
    quiz = Quiz(
        id="cocktail_selector",
        name="Подбери свой коктейль 🍹",
        description="Ответь на 3 вопроса, и мы подберем идеальный коктейль для тебя!",
        category="drinks"
    )
    
    # Вопрос 1: Вкус
    q1 = QuizQuestion(id="q1", text="Какой вкус вы предпочитаете?")
    q1.add_answer("🍬 Сладкий", ["sweet", "dessert", "fruity"])
    q1.add_answer("🍋 Кислый", ["sour", "citrus", "fresh"])
    q1.add_answer("☕ Горький", ["bitter", "strong", "coffee"])
    quiz.add_question(q1)
    
    # Вопрос 2: Крепость
    q2 = QuizQuestion(id="q2", text="Какую крепость предпочитаете?")
    q2.add_answer("🔥 Крепкий", ["strong", "alcoholic", "spirit"])
    q2.add_answer("💧 Легкий", ["light", "low-alcohol", "refreshing"])
    q2.add_answer("🚫 Безалкогольный", ["non-alcoholic", "mocktail", "soft"])
    quiz.add_question(q2)
    
    # Вопрос 3: Основа
    q3 = QuizQuestion(id="q3", text="На какой основе?")
    q3.add_answer("🍹 Ром", ["rum", "caribbean", "tropical"])
    q3.add_answer("🍸 Водка", ["vodka", "classic", "neutral"])
    q3.add_answer("🥃 Виски", ["whiskey", "bourbon", "smoky"])
    q3.add_answer("🍊 Соки и сиропы", ["juice", "syrup", "mocktail"])
    quiz.add_question(q3)
    
    return quiz
