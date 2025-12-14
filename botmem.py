import telebot
import os
import random
import requests

TOKEN = ""

print(os.listdir('images'))

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(messege):
    bot.replay_to(messege, "HI! Ich bin MEMbot. Kanst du testen - schreib /mem")

@bot.message_handler(commands=['mem'])
def send_mem(message):

    random_img_name = random.choice(os.listdir('images'))

    with open(f'images/{random_img_name}', 'rb') as f:
        bot.send_photo(message.chat.id, f)


def get_duck_image_url():    
        url = 'https://random-d.uk/api/random'
        res = requests.get(url)
        data = res.json()
        return data['url']

@bot.message_handler(commands=['duck'])
def duck(message):
        '''По команде duck вызывает функцию get_duck_image_url и отправляет URL изображения утки'''
        image_url = get_duck_image_url()
        bot.reply_to(message, image_url)


bot.polling()            
