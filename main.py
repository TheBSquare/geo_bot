import os
import sys

import telebot
import csv
import random

bot = telebot.TeleBot(token="1919292713:AAFPDm-4XeyPN3uiuZNnbcWZ_V6ouXhx6kE")
users = {}

with open("countries.csv", "r", encoding="utf-8", newline="") as f:
    countries = [x for x in csv.DictReader(f, delimiter=';')]

countries_string = ['№. Город - Столица (континент)\n'] + \
    [f"<i>{i + 1}</i>. <b>{country['country_uk']}</b> - <b>{country['capital_uk']}</b> (<i>{country['continent']}</i>)\n" for i, country in enumerate(countries)]
countries_strings = [countries_string[x:x+len(countries_string)//7] for x in range(0, len(countries_string), len(countries_string)//7)]


@bot.message_handler(commands=['start'])
def start_message(message):
    user = users.get(message.chat.id)
    if user is None:
        users[message.chat.id] = {}

    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Начать')
    keyboard.row('Список всех стран')
    keyboard.row("Информация")

    message = bot.send_message(message.chat.id, 'Привет я помогу тебе выучить страны и их расположение ;)', reply_markup=keyboard)
    bot.register_next_step_handler(message, process_step)


def process_step(message):
    if message.text == "Начать":
        start_quiz(message)
    elif message.text == "Список всех стран":
        for part in countries_strings:
            string = ''.join(x for x in part)
            message = bot.send_message(message.chat.id, text=string, parse_mode="html")
        bot.register_next_step_handler(message, process_step)
    else:
        bot.register_next_step_handler(message, process_step)
        bot.delete_message(message.chat.id, message.message_id)


def ask_question(message):
    user = users[message.chat.id]

    question_type = random.choice(["country", "capital"])

    if len(user["countries"]) < 1:
        pass
    else:
        country = random.choice(user["countries"])

        if user.get("question") is None:
            user["question"] = {}

        user["question"]["country"] = country
        user["question"]["question_type"] = question_type
        user["question"]["message_id"] = message.message_id

        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Ответ')
        keyboard.row('Стоп')

        if question_type == "country":
            message = bot.send_message(
                chat_id=message.chat.id,
                text=f'{len(user["countries"])}. {country["country_uk"]} (Страна)',
                reply_markup=keyboard
            )

        elif question_type == "capital":
            message = bot.send_message(
                chat_id=message.chat.id,
                text=f'{len(user["countries"])}. {country["capital_uk"]} (Столица)',
                reply_markup=keyboard
            )

        bot.register_next_step_handler(message, answer_question)


def ask_question_wrapper(message):
    if message.text == "Cледующая страна":
        ask_question(message)
    elif message.text == 'Стоп':
        menu(message)
    else:
        bot.register_next_step_handler(message, ask_question_wrapper)
        bot.delete_message(message.chat.id, message.message_id)


def menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Начать заного')
    keyboard.row('Продолжить')
    keyboard.row('Список всех стран')
    keyboard.row("Информация")

    message = bot.send_message(message.chat.id, 'Меню', reply_markup=keyboard)
    bot.register_next_step_handler(message, process_menu)


def answer_question(message):
    if message.text == 'Ответ':
        user = users[message.chat.id]
        question = user["question"]
        country = question["country"]

        del user["countries"][user["countries"].index(country)]
        maps = f"https://www.google.com/maps/place/{country['country_en']}".replace(" ", "+")

        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Cледующая страна')
        keyboard.row('Стоп')

        message = bot.send_message(
            message.chat.id,
            f'Правильный ответ:\n<b>Cтрана</b>: <i>{country["country_uk"]}</i>'
            f'\n<b>Cтолица</b>: <i>{country["capital_uk"]}</i>'
            f'\n<b>Площадь страны</b>: <i>{country["area"]} м²</i>'
            f'\n<b>Количество населения</b>: <i>{country["population"]}</i>'
            f'\n<b>Расположение</b>: <i>{maps}</i>',
            reply_markup=keyboard,
            parse_mode="html"
        )

        country_map = open(f"./countries_maps/{country['country_en']}.png", "rb")
        bot.send_photo(message.chat.id, country_map, reply_to_message_id=message.message_id)

        bot.register_next_step_handler(message, ask_question_wrapper)
    elif message.text == 'Стоп':
        menu(message)
    else:
        bot.register_next_step_handler(message, answer_question)
        bot.delete_message(message.chat.id, message.message_id)


def process_menu(message):
    if message.text == "Начать заного":
        start_quiz(message)
    elif message.text == "Продолжить":
        ask_question(message)
    elif message.text == "Список всех стран":
        for part in countries_strings:
            string = ''.join(x for x in part)
            message = bot.send_message(message.chat.id, text=string, parse_mode="html")
        bot.register_next_step_handler(message, process_menu)
    else:
        bot.register_next_step_handler(message, process_menu)
        bot.delete_message(message.chat.id, message.message_id)


def start_quiz(message):
    user = users[message.chat.id]
    user["countries"] = countries.copy()

    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Стоп')

    message = bot.send_message(
        message.chat.id,
        'Я буду давать тебе название страны или её столицу и ты должен будешь ее угадать и найти на карте.'
        ' После того как нажмешь на кнопку <b>Ответ</b>, я дам правильный вариант, удачи!',
        reply_markup=keyboard,
        parse_mode="html"
    )
    ask_question(message)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.delete_message(message.chat.id, message.message_id)


if __name__ == '__main__':
    bot.polling()
