import telebot
import random


TOKEN = ""

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_password(message):
    bot.reply_to(message, "Hi! Ich bin deine BotTelegramm.")

@bot.message_handler(commands=["TikTok"])
def send_password(message):
    bot.reply_to(message, "Тикток заблокирован в РФ))")

def gen_pass(pass_length):
    elements = "+-/*!&$#?=@<>123456789"
    password = ""
    for i in range(pass_length):
        password += random.choice(elements)
    return password 

@bot.message_handler(commands=["Password"])
def zeig_password(message):
    password = gen_pass(8)
    bot.reply_to(message, f"Ваш новый пароль {password} ")

bot.polling()
