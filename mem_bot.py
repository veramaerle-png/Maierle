import telebot
import os
import random
import requests
import json
from collections import defaultdict

TOKEN = ""

bot = telebot.TeleBot(TOKEN)

# Система редкости мемов
MEME_RARITY = {
    "common": {"weight": 50, "emoji": "⚪", "name": "Обычный"},
    "uncommon": {"weight": 25, "emoji": "🟢", "name": "Необычный"},
    "rare": {"weight": 15, "emoji": "🔵", "name": "Редкий"},
    "epic": {"weight": 8, "emoji": "🟣", "name": "Эпический"},
    "legendary": {"weight": 2, "emoji": "🟡", "name": "Легендарный"}
}

META_FILE = 'images'

# Загрузка или создание метаданных мемов
def load_meme_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_meme_metadata(metadata):
    with open(META_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

# Инициализация метаданных
meme_metadata = load_meme_metadata()

# Функция для автоматического назначения категорий и редкости новым мемам
def assign_meme_properties(img_name):
    if img_name not in meme_metadata:
        # Определяем категорию по имени файла (простая логика)
        img_lower = img_name.lower()
        category = "other"
        
        if any(word in img_lower for word in ['cat', 'dog', 'animal', 'bird', 'pet']):
            category = "animals"
        elif any(word in img_lower for word in ['code', 'program', 'bug', 'hack', 'dev']):
            category = "programming"
        elif any(word in img_lower for word in ['game', 'play', 'gamer', 'quest']):
            category = "games"
        elif any(word in img_lower for word in ['funny', 'joke', 'lol', 'humor']):
            category = "funny"
        
        # Случайно назначаем редкость (можно заменить на более сложную логику)
        rarity = random.choices(
            list(MEME_RARITY.keys()),
            weights=[MEME_RARITY[r]["weight"] for r in MEME_RARITY],
            k=1
        )[0]
        
        meme_metadata[img_name] = {
            "category": category,
            "rarity": rarity,
            "sent_count": 0
        }
        save_meme_metadata(meme_metadata)
    
    return meme_metadata[img_name]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    🎭 Добро пожаловать в MEMbot - Бога-Коллекционера Мемов! 🎭

    Доступные команды:
    /mem - случайный мем
    /duck - случайная утка
    /animals - мемы с животными
    /programming - программистские мемы
    /games - игровые мемы
    /funny - смешные мемы
    /rare - редкий мем (с учётом редкости)
    /categories - все доступные категории
    /stats - статистика по мемам
    /rarities - информация о редкостях

    Да прибудут с тобой мемы! 🙏
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['mem'])
def send_mem(message):
    """Случайный мем из всех категорий"""
    if not os.listdir('images'):
        bot.reply_to(message, "В библиотеке нет мемов! 😢")
        return
    
    random_img_name = random.choice(os.listdir('images'))
    meme_info = assign_meme_properties(random_img_name)
    
    # Увеличиваем счётчик отправок
    meme_info["sent_count"] += 1
    save_meme_metadata(meme_metadata)
    
    rarity_info = MEME_RARITY[meme_info["rarity"]]
    caption = f"Категория: {meme_info['category'].title()}\n{rarity_info['emoji']} Редкость: {rarity_info['name']}\n📊 Отправлен раз: {meme_info['sent_count']}"
    
    with open(f'images/{random_img_name}', 'rb') as f:
        bot.send_photo(message.chat.id, f, caption=caption)

@bot.message_handler(commands=['animals', 'programming', 'games', 'funny'])
def send_category_mem(message):
    """Мемы по категориям"""
    category = message.text[1:]  # Убираем "/"
    
    # Получаем все файлы в категории
    category_memes = []
    for img_name in os.listdir('images'):
        meme_info = assign_meme_properties(img_name)
        if meme_info["category"] == category:
            category_memes.append((img_name, meme_info))
    
    if not category_memes:
        bot.reply_to(message, f"В категории '{category}' пока нет мемов! 😢")
        return
    
    # Выбираем случайный мем из категории
    img_name, meme_info = random.choice(category_memes)
    
    # Увеличиваем счётчик отправок
    meme_info["sent_count"] += 1
    save_meme_metadata(meme_metadata)
    
    rarity_info = MEME_RARITY[meme_info["rarity"]]
    caption = f"🎯 Категория: {category.title()}\n{rarity_info['emoji']} Редкость: {rarity_info['name']}"
    
    with open(f'images/{img_name}', 'rb') as f:
        bot.send_photo(message.chat.id, f, caption=caption)

@bot.message_handler(commands=['rare'])
def send_rare_mem(message):
    """Мем с учётом редкости (редкие выпадают реже)"""
    if not os.listdir('images'):
        bot.reply_to(message, "В библиотеке нет мемов! 😢")
        return
    
    # Собираем все мемы с их весами редкости
    memes_with_weights = []
    for img_name in os.listdir('images'):
        meme_info = assign_meme_properties(img_name)
        weight = MEME_RARITY[meme_info["rarity"]]["weight"]
        memes_with_weights.append((img_name, meme_info, weight))
    
    # Выбираем с учётом весов (редкие имеют меньший вес)
    img_name, meme_info, _ = random.choices(
        memes_with_weights,
        weights=[w for _, _, w in memes_with_weights],
        k=1
    )[0]
    
    # Увеличиваем счётчик отправок
    meme_info["sent_count"] += 1
    save_meme_metadata(meme_metadata)
    
    rarity_info = MEME_RARITY[meme_info["rarity"]]
    caption = f"✨ РЕДКИЙ МЕМ! ✨\nКатегория: {meme_info['category'].title()}\n{rarity_info['emoji']} Редкость: {rarity_info['name']}\n🎲 Шанс выпадения: {rarity_info['weight']}%"
    
    with open(f'images/{img_name}', 'rb') as f:
        bot.send_photo(message.chat.id, f, caption=caption)

@bot.message_handler(commands=['categories'])
def show_categories(message):
    """Показать все доступные категории"""
    categories = defaultdict(int)
    
    for img_name in os.listdir('images'):
        meme_info = assign_meme_properties(img_name)
        categories[meme_info["category"]] += 1
    
    if not categories:
        bot.reply_to(message, "Категорий пока нет!")
        return
    
    response = "📂 Доступные категории:\n\n"
    for category, count in sorted(categories.items()):
        response += f"/{category} - {count} мемов\n"
    
    response += "\nИспользуй команды выше для получения мемов по категориям!"
    bot.reply_to(message, response)

@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Статистика по мемам"""
    if not os.listdir('images'):
        bot.reply_to(message, "Нет статистики - мемов нет!")
        return
    
    total_memes = len(os.listdir('images'))
    total_sent = sum(m["sent_count"] for m in meme_metadata.values())
    
    categories = defaultdict(int)
    rarities = defaultdict(int)
    
    for meme_info in meme_metadata.values():
        categories[meme_info["category"]] += 1
        rarities[meme_info["rarity"]] += 1
    
    # Самый популярный мем
    most_popular = max(meme_metadata.items(), key=lambda x: x[1]["sent_count"]) if meme_metadata else ("Нет", {"sent_count": 0})
    
    response = f"""
📊 Статистика Бога-Коллекционера:

🎭 Всего мемов: {total_memes}
📤 Отправлено раз: {total_sent}

🏷️ По категориям:
"""
    for category, count in sorted(categories.items()):
        response += f"  • {category.title()}: {count}\n"
    
    response += "\n🎲 По редкости:\n"
    for rarity, count in sorted(rarities.items()):
        rarity_name = MEME_RARITY[rarity]["name"]
        emoji = MEME_RARITY[rarity]["emoji"]
        response += f"  • {emoji} {rarity_name}: {count}\n"
    
    response += f"\n🔥 Самый популярный мем: {most_popular[0]}\n📈 Отправлен {most_popular[1]['sent_count']} раз"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['rarities'])
def show_rarities(message):
    """Информация о системе редкости"""
    response = "🎲 Система редкости мемов:\n\n"
    
    for rarity_key, info in MEME_RARITY.items():
        response += f"{info['emoji']} {info['name']}\n"
        response += f"  Шанс выпадения: {info['weight']}%\n"
        response += f"  Ключ: {rarity_key}\n\n"
    
    response += "📝 Примечание: Чем меньше шанс выпадения, тем реже появляется мем!"
    bot.reply_to(message, response)

@bot.message_handler(commands=['duck'])
def duck(message):
    """Случайная утка (оставляем оригинальную функцию)"""
    def get_duck_image_url():    
        url = 'https://random-d.uk/api/random'
        res = requests.get(url)
        data = res.json()
        return data['url']
    
    image_url = get_duck_image_url()
    bot.reply_to(message, image_url)

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Обработка других сообщений"""
    if message.text.startswith('/'):
        bot.reply_to(message, "Неизвестная команда! Используй /start для списка команд.")
    else:
        bot.reply_to(message, "Отправь мне команду! /start - для списка доступных команд.")

if __name__ == "__main__":
    print("Бот запущен! Доступные изображения:", os.listdir('images'))
    print("Загружено метаданных мемов:", len(meme_metadata))
    bot.polling(none_stop=True)
