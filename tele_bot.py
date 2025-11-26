import telebot


TOKEN = ""

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_password(message):
    bot.reply_to(message, "Hi! Ich bin deine BotTelegramm.")

@bot.message_handler(commands=["TikTok"])
def send_password(message):
    bot.reply_to(message, "Тикток заблокирован в РФ))")

bot.polling()
