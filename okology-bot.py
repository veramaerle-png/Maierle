#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram-бот "Вторая жизнь вещей" с оценкой сложности
"""

import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Эмодзи для сложности
DIFFICULTY_EMOJIS = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
DIFFICULTY_LEVELS = {
    1: "Начинающий (1-2 часа)",
    2: "Легкий (2-4 часа)",
    3: "Средний (полдня)",
    4: "Сложный (целый день)",
    5: "Эксперт (несколько дней)"
}

# База данных идей с уровнем сложности (1-5)
IDEAS_DATABASE = {
    "одежда": [
        {
            "idea": "📌 **Старая футболка** → сделай многоразовые сумки для покупок! Просто разрежь по швам и сшей ручки.",
            "difficulty": 2,
            "time": "1-2 часа",
            "tools": "Ножницы, нитки, иголка"
        },
        {
            "idea": "📌 **Джинсы с дырками** → преврати в стильную сумку или органайзер для инструментов.",
            "difficulty": 3,
            "time": "3-4 часа",
            "tools": "Ножницы, швейная машинка, фурнитура"
        },
        {
            "idea": "📌 **Старый свитер** → сделай уютный чехол для горячей кружки или грелку для чайника.",
            "difficulty": 2,
            "time": "1-2 часа",
            "tools": "Ножницы, нитки, наполнитель"
        },
        {
            "idea": "📌 **Ненужные носки** → идеальные чехлы для стеклянных банок (термосы) или игрушки для питомца.",
            "difficulty": 1,
            "time": "30 минут",
            "tools": "Ножницы, нитки, пуговицы для глаз"
        },
        {
            "idea": "📌 **Рубашка с пятном** → вырежи хорошие части и сделай patchwork-подушку или коврик.",
            "difficulty": 4,
            "time": "5-6 часов",
            "tools": "Ножницы, швейная машинка, наполнитель"
        },
    ],
    "посуда": [
        {
            "idea": "🍶 **Стеклянные банки** → стильные вазы, контейнеры для круп, или подсвечники.",
            "difficulty": 1,
            "time": "20-30 минут",
            "tools": "Краска, кисточка, декор"
        },
        {
            "idea": "☕ **Старые чашки** → мини-горшки для суккулентов или держатели для кистей/карандашей.",
            "difficulty": 1,
            "time": "15 минут",
            "tools": "Дренаж, земля, растения"
        },
        {
            "idea": "🍽️ **Треснутая тарелка** → красивая подставка под мыло или основа для мозаики.",
            "difficulty": 2,
            "time": "1-2 часа",
            "tools": "Клей для керамики, затирка"
        },
        {
            "idea": "🥛 **Ненужные ложки/вилки** → сделай крючки для ключей или украшения для сада.",
            "difficulty": 3,
            "time": "2-3 часа",
            "tools": "Плоскогубцы, дрель, краска"
        },
        {
            "idea": "🍵 **Чайник с отбитым носиком** → оригинальный цветочный горшок с дренажом уже готов!",
            "difficulty": 1,
            "time": "10 минут",
            "tools": "Земля, растение"
        },
    ],
    "мебель": [
        {
            "idea": "🪑 **Старый стул** → сними сиденье и сделай полку для книг или вешалку.",
            "difficulty": 3,
            "time": "3-4 часа",
            "tools": "Отвертка, шурупы, краска"
        },
        {
            "idea": "🚪 **Деревянная дверь** → отличный стол, изголовье кровати или вертикальный сад.",
            "difficulty": 4,
            "time": "6-8 часов",
            "tools": "Пила, шуруповерт, морилка"
        },
        {
            "idea": "🛏️ **Деревянная кровать** → разбери на доски и сделай скамейку для сада или полки.",
            "difficulty": 4,
            "time": "1 день",
            "tools": "Молоток, гвозди, пила, краска"
        },
        {
            "idea": "🗄️ **Комод с отваливающимися ящиками** → каждый ящик можно превратить в отдельную полку или ящик для рассады.",
            "difficulty": 2,
            "time": "1-2 часа",
            "tools": "Крючки, краска, кисточка"
        },
        {
            "idea": "🪞 **Старое зеркало** → сделай рамку для фотографий или мозаичный столик.",
            "difficulty": 5,
            "time": "2-3 дня",
            "tools": "Стеклорез, клей, мозаика, затирка"
        },
    ],
    "садовые": [
        {
            "idea": "🌿 **Старая лестница** → вертикальная подставка для цветов в саду или вешалка для полотенец.",
            "difficulty": 2,
            "time": "1-2 часа",
            "tools": "Краска, кисточка, крючки"
        },
        {
            "idea": "🚲 **Велосипедная шина** → качели для детей или основа для вьющихся растений.",
            "difficulty": 3,
            "time": "2-3 часа",
            "tools": "Веревка, дрель, краска"
        },
        {
            "idea": "🌧️ **Резиновые сапоги** → необычные горшки для цветов на заборе или у входа.",
            "difficulty": 1,
            "time": "15 минут",
            "tools": "Гвоздь для дренажа, земля, цветы"
        },
        {
            "idea": "🪣 **Дырявое ведро** → переверни и сделай стол для сада или дом для ёжика.",
            "difficulty": 2,
            "time": "1 час",
            "tools": "Краска, стекло для столешницы"
        },
        {
            "idea": "🌼 **Старый унитаз** → звучит странно, но получается отличная клумба для петуний!",
            "difficulty": 2,
            "time": "1 час",
            "tools": "Краска, земля, цветы"
        },
    ],
    "техника": [
        {
            "idea": "💻 **Старый монитор** → убери электронику, добавь полочку — получится аквариум для кота или полка.",
            "difficulty": 4,
            "time": "4-5 часов",
            "tools": "Отвертки, стеклорез, клей"
        },
        {
            "idea": "📺 **Не рабочий телевизор** → сделай книжный шкаф или домик для кошки.",
            "difficulty": 4,
            "time": "5-6 часов",
            "tools": "Отвертки, дрель, фанера"
        },
        {
            "idea": "⌨️ **Клавиатура** → сними клавиши и сделай брелоки, магниты или мозаику.",
            "difficulty": 2,
            "time": "1-2 часа",
            "tools": "Отвертка, суперклей, магниты"
        },
        {
            "idea": "💿 **CD/DVD диски** → моби для отпугивания птиц в саду или элементы декора.",
            "difficulty": 1,
            "time": "30 минут",
            "tools": "Ножницы, нитка, дырокол"
        },
        {
            "idea": "🔌 **Старые провода** → сплети кашпо для растений или органайзер для проводов.",
            "difficulty": 3,
            "time": "2-3 часа",
            "tools": "Плоскогубцы, клей"
        },
    ],
}

# Фразы для случайных приветствий
GREETINGS = [
    "Привет! Я помогу дать вторую жизнь твоим старым вещам 🛠️",
    "Здравствуй! Готов превратить хлам в сокровище? 💎",
    "Приветствую! У меня есть идеи для переделки всего на свете! ✨",
    "Привет! Скажи, что у тебя пылится без дела, и я найду ему применение 🔍",
]

# Список ключевых слов для автоматического определения категории
KEYWORDS_TO_CATEGORY = {
    "футболка": "одежда",
    "джинсы": "одежда", 
    "свитер": "одежда",
    "носки": "одежда",
    "рубашка": "одежда",
    "одежда": "одежда",
    
    "банка": "посуда",
    "чашка": "посуда",
    "тарелка": "посуда",
    "ложка": "посуда",
    "вилка": "посуда",
    "чайник": "посуда",
    "посуда": "посуда",
    
    "стул": "мебель",
    "дверь": "мебель",
    "кровать": "мебель",
    "комод": "мебель",
    "зеркало": "мебель",
    "мебель": "мебель",
    
    "лестница": "садовые",
    "велосипед": "садовые",
    "сапоги": "садовые",
    "ведро": "садовые",
    "унитаз": "садовые",
    "сад": "садовые",
    
    "монитор": "техника",
    "телевизор": "техника",
    "клавиатура": "техника",
    "диск": "техника",
    "провода": "техника",
    "техника": "техника",
}

class SecondLifeBot:
    """Основной класс бота с оценкой сложности"""
    
    def __init__(self, token: str):
        self.token = token
        self.user_data_file = "user_ideas.json"
        self.user_ideas = self.load_user_ideas()
        
    def load_user_ideas(self) -> Dict:
        """Загрузка пользовательских идей из файла"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки файла идей: {e}")
        return {}
    
    def save_user_ideas(self):
        """Сохранение пользовательских идей в файл"""
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_ideas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения файла идей: {e}")
    
    def detect_category(self, text: str) -> Optional[str]:
        """Определение категории по тексту сообщения"""
        text_lower = text.lower()
        for keyword, category in KEYWORDS_TO_CATEGORY.items():
            if keyword in text_lower:
                return category
        return None
    
    def format_idea_with_difficulty(self, idea_dict: Dict) -> str:
        """Форматирование идеи с информацией о сложности"""
        difficulty_stars = DIFFICULTY_EMOJIS[idea_dict["difficulty"] - 1]
        difficulty_text = DIFFICULTY_LEVELS[idea_dict["difficulty"]]
        
        formatted = f"{idea_dict['idea']}\n\n"
        formatted += f"📊 **Сложность:** {difficulty_stars} ({idea_dict['difficulty']}/5)\n"
        formatted += f"⏱️ **Время:** {idea_dict['time']}\n"
        
        if idea_dict.get('tools'):
            formatted += f"🛠️ **Инструменты:** {idea_dict['tools']}\n"
        
        formatted += f"📝 **Уровень:** {difficulty_text}"
        
        return formatted
    
    def get_random_idea(self, category: Optional[str] = None, max_difficulty: Optional[int] = None) -> Tuple[Dict, str]:
        """Получение случайной идеи с фильтром по сложности"""
        if category and category in IDEAS_DATABASE:
            ideas = IDEAS_DATABASE[category]
        else:
            # Если категория не указана, выбираем из всех
            all_ideas = []
            for cat_ideas in IDEAS_DATABASE.values():
                all_ideas.extend(cat_ideas)
            ideas = all_ideas
        
        # Фильтрация по сложности если указана
        if max_difficulty:
            ideas = [idea for idea in ideas if idea["difficulty"] <= max_difficulty]
        
        if ideas:
            idea_dict = random.choice(ideas)
            formatted = self.format_idea_with_difficulty(idea_dict)
            return idea_dict, formatted
        
        return None, "Пока нет идей для этой категории. Попробуйте другую!"
    
    def get_ideas_by_difficulty(self, category: str, difficulty: int, count: int = 3) -> List[str]:
        """Получение идей определенной сложности"""
        if category in IDEAS_DATABASE:
            ideas = [idea for idea in IDEAS_DATABASE[category] if idea["difficulty"] == difficulty]
            if len(ideas) > count:
                selected = random.sample(ideas, count)
            else:
                selected = ideas
            
            formatted_ideas = []
            for idea in selected:
                formatted_ideas.append(self.format_idea_with_difficulty(idea))
            return formatted_ideas
        
        return [f"Категория '{category}' не найдена."]
    
    def get_category_stats(self, category: str) -> Dict:
        """Получение статистики по категории"""
        if category in IDEAS_DATABASE:
            ideas = IDEAS_DATABASE[category]
            total = len(ideas)
            difficulty_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            
            for idea in ideas:
                difficulty_counts[idea["difficulty"]] += 1
            
            avg_difficulty = sum(idea["difficulty"] for idea in ideas) / total
            
            return {
                "total": total,
                "difficulty_counts": difficulty_counts,
                "avg_difficulty": round(avg_difficulty, 1),
                "easiest": min(ideas, key=lambda x: x["difficulty"]),
                "hardest": max(ideas, key=lambda x: x["difficulty"])
            }
        return {}
    
    def add_user_idea(self, user_id: int, idea: str, difficulty: int = 3):
        """Добавление пользовательской идеи"""
        if str(user_id) not in self.user_ideas:
            self.user_ideas[str(user_id)] = []
        
        self.user_ideas[str(user_id)].append({
            "idea": idea,
            "difficulty": difficulty,
            "date": datetime.now().isoformat(),
            "user_rated": False
        })
        self.save_user_ideas()
    
    def get_user_ideas(self, user_id: int) -> List[Dict]:
        """Получение идей пользователя"""
        return self.user_ideas.get(str(user_id), [])

# Создаем экземпляр бота
bot_instance = SecondLifeBot("YOUR_BOT_TOKEN_HERE")

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    greeting = random.choice(GREETINGS)
    keyboard = [
        [InlineKeyboardButton("🎯 Случайная идея", callback_data='random')],
        [InlineKeyboardButton("📂 Все категории", callback_data='categories')],
        [InlineKeyboardButton("⭐ Простые идеи (1-2⭐)", callback_data='easy_ideas')],
        [InlineKeyboardButton("🛠️ Сложные идеи (4-5⭐)", callback_data='hard_ideas')],
        [InlineKeyboardButton("💡 Мои идеи", callback_data='my_ideas')],
        [InlineKeyboardButton("➕ Добавить идею", callback_data='add_idea')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{greeting}\n\n"
        "Я помогу найти новое применение старым вещам!\n\n"
        "📊 **Каждая идея теперь имеет оценку сложности (1-5 звезд)**\n\n"
        "Выбери действие ниже или напиши название предмета",
        reply_markup=reply_markup
    )

async def difficulty_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /difficulty - показывает шкалу сложности"""
    difficulty_text = "📊 **Шкала сложности проектов:**\n\n"
    
    for level, description in DIFFICULTY_LEVELS.items():
        stars = DIFFICULTY_EMOJIS[level-1]
        difficulty_text += f"{stars} **Уровень {level}:** {description}\n\n"
    
    difficulty_text += "🎯 **Как выбрать?**\n"
    difficulty_text += "• 1-2⭐ - Отлично для начинающих\n"
    difficulty_text += "• 3⭐ - Нужен небольшой опыт\n"
    difficulty_text += "• 4-5⭐ - Для опытных мастеров\n\n"
    difficulty_text += "Используй кнопки фильтрации для поиска идей нужной сложности!"
    
    keyboard = [
        [InlineKeyboardButton("⭐ Простые идеи", callback_data='easy_ideas'),
         InlineKeyboardButton("⭐⭐⭐ Средние", callback_data='medium_ideas')],
        [InlineKeyboardButton("⭐⭐⭐⭐⭐ Сложные", callback_data='hard_ideas')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(difficulty_text, reply_markup=reply_markup, parse_mode='Markdown')

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /categories с показом статистики"""
    categories_text = "📂 **Категории идей:**\n\n"
    
    for i, category in enumerate(IDEAS_DATABASE.keys(), 1):
        stats = bot_instance.get_category_stats(category)
        emoji = "👕" if category == "одежда" else \
                "🍶" if category == "посуда" else \
                "🪑" if category == "мебель" else \
                "🌿" if category == "садовые" else \
                "💻" if category == "техника" else \
                "🎨"
        
        if stats:
            avg_stars = "⭐" * round(stats["avg_difficulty"])
            categories_text += f"{i}. {emoji} **{category.capitalize()}**\n"
            categories_text += f"   📊 {stats['total']} идей | ⌀ {stats['avg_difficulty']}/5 {avg_stars}\n\n"
    
    categories_text += "📝 **Нажми на категорию чтобы увидеть идеи с фильтрацией по сложности!**"
    
    keyboard = []
    for category in IDEAS_DATABASE.keys():
        stats = bot_instance.get_category_stats(category)
        avg_diff = round(stats["avg_difficulty"]) if stats else 3
        stars = "⭐" * avg_diff
        
        keyboard.append([InlineKeyboardButton(
            f"📁 {category.capitalize()} ({stars})",
            callback_data=f"cat_{category}"
        )])
    
    keyboard.append([
        InlineKeyboardButton("📊 Шкала сложности", callback_data='show_difficulty_scale'),
        InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(categories_text, reply_markup=reply_markup, parse_mode='Markdown')

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /random с фильтрацией сложности"""
    # Проверяем, указал ли пользователь максимальную сложность
    max_difficulty = None
    if context.args:
        try:
            max_difficulty = int(context.args[0])
            if max_difficulty < 1 or max_difficulty > 5:
                max_difficulty = None
        except ValueError:
            pass
    
    idea_dict, idea_text = bot_instance.get_random_idea(max_difficulty=max_difficulty)
    
    if max_difficulty:
        idea_text = f"🎲 **Случайная идея (макс. сложность: {max_difficulty}⭐):**\n\n{idea_text}"
    else:
        idea_text = f"🎲 **Случайная идея:**\n\n{idea_text}"
    
    # Кнопки для фильтрации по сложности
    keyboard = []
    if idea_dict:
        current_diff = idea_dict["difficulty"]
        keyboard.append([
            InlineKeyboardButton(f"🤔 Слишком { 'сложно' if current_diff > 3 else 'просто' }?", 
                               callback_data=f"diff_filter_{max(1, current_diff-1)}"),
            InlineKeyboardButton("🎯 Еще такую же", callback_data=f"same_diff_{current_diff}")
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("⭐ Простые (1-2⭐)", callback_data='easy_ideas'),
         InlineKeyboardButton("⭐⭐⭐ Средние", callback_data='medium_ideas')],
        [InlineKeyboardButton("📂 Все категории", callback_data='categories')]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"{idea_text}\n\n💬 Хочешь другую сложность? Используй кнопки ниже!", 
                                   reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_message = update.message.text.lower()
    user_id = update.effective_user.id
    
    # Проверка на запрос определенной сложности
    difficulty_filter = None
    for i in range(1, 6):
        if f"{i} звезд" in user_message or f"{i}⭐" in user_message or f"сложность {i}" in user_message:
            difficulty_filter = i
            break
    
    # Ответ на "еще", "дай идею" и подобные
    if any(word in user_message for word in ['еще', 'ещё', 'дай идею', 'хочу идею', 'идею']):
        if difficulty_filter:
            idea_dict, idea_text = bot_instance.get_random_idea(max_difficulty=difficulty_filter)
            idea_text = f"🎯 **Идея (макс. {difficulty_filter}⭐):**\n\n{idea_text}"
        else:
            idea_dict, idea_text = bot_instance.get_random_idea()
            idea_text = f"🎯 **Вот идея:**\n\n{idea_text}"
        
        await update.message.reply_text(idea_text, parse_mode='Markdown')
        return
    
    # Определяем категорию
    category = bot_instance.detect_category(user_message)
    
    if category:
        # Если есть фильтр сложности
        if difficulty_filter:
            ideas = bot_instance.get_ideas_by_difficulty(category, difficulty_filter, count=1)
            if ideas and ideas[0]:
                response = f"🔍 **Нашел для '{user_message}' ({difficulty_filter}⭐):**\n\n{ideas[0]}"
            else:
                response = f"😕 В категории '{category}' нет идей сложностью {difficulty_filter}⭐\nПопробуйте другую сложность или категорию."
        else:
            # Без фильтра - случайная идея из категории
            idea_dict, idea_text = bot_instance.get_random_idea(category)
            if idea_dict:
                response = f"🔍 **Нашел для '{user_message}':**\n\n{idea_text}"
            else:
                response = f"Пока нет идей для '{user_message}'. Попробуйте другую категорию!"
        
        # Добавляем кнопки для фильтрации по сложности
        keyboard = []
        if category and not difficulty_filter:
            keyboard.append([
                InlineKeyboardButton("⭐ Простые", callback_data=f"cat_{category}_diff_1"),
                InlineKeyboardButton("⭐⭐ Средние", callback_data=f"cat_{category}_diff_3"),
                InlineKeyboardButton("⭐⭐⭐⭐⭐ Сложные", callback_data=f"cat_{category}_diff_5")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📂 Все категории", callback_data='categories'),
            InlineKeyboardButton("🎯 Случайная", callback_data='random')
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        # Если категория не определена
        if difficulty_filter:
            # Если указана только сложность
            idea_dict, idea_text = bot_instance.get_random_idea(max_difficulty=difficulty_filter)
            response = f"🎯 **Идея ({difficulty_filter}⭐ максимум):**\n\n{idea_text}"
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            # Полная помощь
            await update.message.reply_text(
                f"🤔 Не совсем понял про '{user_message}'.\n\n"
                "Можешь указать сложность:\n"
                "• 'идея на 2 звезды'\n"
                "• 'простая идея для футболки'\n"
                "• 'сложный проект из дерева'\n\n"
                "Или выбери действие из меню!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 Шкала сложности", callback_data='show_difficulty_scale')],
                    [InlineKeyboardButton("⭐ Простые идеи", callback_data='easy_ideas')],
                    [InlineKeyboardButton("🎯 Случайная", callback_data='random')]
                ])
            )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Обработка кнопки сложности
    if data == 'show_difficulty_scale':
        difficulty_text = "📊 **Шкала сложности:**\n\n"
        for level, description in DIFFICULTY_LEVELS.items():
            stars = DIFFICULTY_EMOJIS[level-1]
            difficulty_text += f"{stars} **Уровень {level}:** {description}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("⭐ Простые идеи", callback_data='easy_ideas'),
             InlineKeyboardButton("⭐⭐⭐ Средние", callback_data='medium_ideas')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=difficulty_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    # Простые идеи (1-2 звезды)
    elif data == 'easy_ideas':
        idea_dict, idea_text = bot_instance.get_random_idea(max_difficulty=2)
        idea_text = f"⭐ **Простая идея (1-2⭐):**\n\n{idea_text}"
        
        keyboard = [
            [InlineKeyboardButton("🎯 Еще простую", callback_data='easy_ideas'),
             InlineKeyboardButton("⭐⭐⭐ Среднюю", callback_data='medium_ideas')],
            [InlineKeyboardButton("📂 Все категории", callback_data='categories')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=idea_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    # Средние идеи (3 звезды)
    elif data == 'medium_ideas':
        idea_dict, idea_text = bot_instance.get_random_idea(max_difficulty=3)
        # Фильтруем чтобы не было слишком простых
        if idea_dict and idea_dict["difficulty"] < 2:
            idea_dict, idea_text = bot_instance.get_random_idea(max_difficulty=3)
        
        idea_text = f"⭐⭐⭐ **Средняя идея (3⭐):**\n\n{idea_text}"
        
        keyboard = [
            [InlineKeyboardButton("🎯 Еще среднюю", callback_data='medium_ideas'),
             InlineKeyboardButton("⭐⭐⭐⭐⭐ Сложную", callback_data='hard_ideas')],
            [InlineKeyboardButton("📂 Все категории", callback_data='categories')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=idea_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    # Сложные идеи (4-5 звезд)
    elif data == 'hard_ideas':
        idea_dict, idea_text = bot_instance.get_random_idea()
        # Ищем действительно сложные
        if idea_dict and idea_dict["difficulty"] < 4:
            # Пробуем еще раз найти сложную
            for _ in range(5):  # Несколько попыток
                idea_dict, idea_text = bot_instance.get_random_idea()
                if idea_dict and idea_dict["difficulty"] >= 4:
                    break
        
        idea_text = f"⭐⭐⭐⭐⭐ **Сложная идея (4-5⭐):**\n\n{idea_text}"
        
        keyboard = [
            [InlineKeyboardButton("🎯 Еще сложную", callback_data='hard_ideas'),
             InlineKeyboardButton("⭐ Простую", callback_data='easy_ideas')],
            [InlineKeyboardButton("📂 Все категории", callback_data='categories')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=idea_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    # Фильтр по сложности для категории (cat_одежда_diff_3)
    elif data.startswith('cat_') and '_diff_' in data:
        parts = data.split('_')
        if len(parts) >= 4:
            category = parts[1]
            try:
                difficulty = int(parts[3])
            except:
                difficulty = 3
            
            ideas = bot_instance.get_ideas_by_difficulty(category, difficulty, count=1)
            
            if ideas and ideas[0]:
                response = f"📁 **{category.capitalize()}** • {DIFFICULTY_EMOJIS[difficulty-1]}\n\n{ideas[0]}"
            else:
                response = f"В категории '{category}' нет идей сложностью {difficulty}⭐"
            
            keyboard = [
                [InlineKeyboardButton(f"🎯 Еще {difficulty}⭐", callback_data=data),
                 InlineKeyboardButton("📂 Все категории", callback_data='categories')],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{category}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text=response, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    # Выбор категории (показывает статистику и кнопки сложности)
    elif data.startswith('cat_') and '_diff_' not in data:
        category = data[4:]  # Убираем 'cat_'
        if category in IDEAS_DATABASE:
            stats = bot_instance.get_category_stats(category)
            
            emoji = "👕" if category == "одежда" else \
                    "🍶" if category == "посуда" else \
                    "🪑" if category == "мебель" else \
                    "🌿" if category == "садовые" else \
                    "💻" if category == "техника" else \
                    "🎨"
            
            response = f"{emoji} **{category.capitalize()}**\n\n"
            
            if stats:
                response += f"📊 **Статистика:**\n"
                response += f"• Всего идей: {stats['total']}\n"
                response += f"• Средняя сложность: {stats['avg_difficulty']}/5\n"
                response += f"• Самая простая: {stats['easiest']['difficulty']}⭐\n"
                response += f"• Самая сложная: {stats['hardest']['difficulty']}⭐\n\n"
            
            response += "🎯 **Выбери уровень сложности:**"
            
            keyboard = []
            # Кнопки для разных уровней сложности
            for diff in [1, 2, 3, 4, 5]:
                count = stats['difficulty_counts'].get(diff, 0) if stats else 0
                if count > 0:
                   
