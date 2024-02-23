import telebot
import requests
import time
from datetime import datetime, timedelta
import json

bot = telebot.TeleBot('6633029686:AAEkFyZVM4duVa0xL12m2O9QaMrhqy1pYU0')

all_anecdotes = []
flagP = False

try:
    with open('users', 'r') as file:
        users_data = json.load(file)
except FileNotFoundError:
    users_data = {}


def add_to_json(user_id, current_time, end_time):
    users_data[user_id] = {
        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open('users.json', 'w') as file:
        json.dump(users_data, file, indent=2)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = telebot.types.KeyboardButton('Получить анекдот')
    bt2 = telebot.types.KeyboardButton('Получать анекдот через интервал времени')
    markup.add(bt1, bt2)
    bot.send_message(message.chat.id, text="Привет! Я смешной бот! Когда вы хотите первую получить шутку?",
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    global flagP
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == "Получить анекдот":
        get_anekdot(message, True)

    elif message.text == 'Получать анекдот через интервал времени':
        bt1 = telebot.types.KeyboardButton('Получить анекдот')
        bt3 = telebot.types.KeyboardButton('Отменить получение анекдота')
        markup.add(bt1, bt3)
        bot.send_message(message.chat.id,
                         text="Введите, пожалуйста, с какой периодичностью присылать шутки. Время указывается в минутах.",
                         reply_markup=markup)

    elif message.text.isdigit() and int(message.text) > 0:
        n = int(message.text)
        bot.send_message(message.chat.id, text=f"Вам будет приходить анекдот в выбранный интервал :)",
                         reply_markup=markup)
        bt1 = telebot.types.KeyboardButton('Получить анекдот')
        bt3 = telebot.types.KeyboardButton('Отменить получение анекдота')
        markup.add(bt1, bt3)
        flagP = True
        get_periodic_anekdot(message, n)

    elif message.text == 'Отменить получение анекдота':
        bt2 = telebot.types.KeyboardButton('Получать анекдот через интервал времени')
        bt1 = telebot.types.KeyboardButton('Получить анекдот')
        markup.add(bt1, bt2)
        bot.send_message(message.chat.id, text='Отправка анекдотов отключена', reply_markup=markup)
        flagP = False
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда.', reply_markup=markup)


@bot.message_handler(commands=['get_anekdot', 'anekdot'])
def get_anekdot(message, flag):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if flag:
        url = 'http://rzhunemogu.ru/Rand.aspx?CType=1'
        r = requests.get(url)
        bot.send_message(message.chat.id, r.text[53:-17], reply_markup=markup)
        all_anecdotes.append(r.text[53:-17])
    else:
        return False


def get_periodic_anekdot(message, n):
    end_minutes = n
    end_hours = 0
    if end_minutes > 60:
        end_hours = end_minutes // 60
        end_minutes = n - 60
    current_time = datetime.now()

    end_time = current_time + timedelta(hours=end_hours, minutes=end_minutes)
    while flagP:
        if datetime.now() >= end_time and flagP == True:
            get_anekdot(message, flagP)
            end_time = datetime.now() + timedelta(hours=end_hours, minutes=end_minutes)
        time.sleep(1)
        add_to_json(user_id=message.chat.id, current_time=current_time, end_time=end_time)


bot.polling(none_stop=True)
