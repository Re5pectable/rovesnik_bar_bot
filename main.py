from pyrogram import Client, filters
from config import config
from settings import config_messages, markups
from db import db
import time
import datetime

app = Client("sessions/rovesnik", api_id = config.api_id, api_hash = config.api_hash, bot_token = config.bot_token)

user_states = ["hanging", "typing_is_today", "typing_name", "typing_n_guests", "typing_time", "typing_phone", "waiting_confirm", "sending_deposit", "typing_review"]


@app.on_message(filters.command("start"))
def start_command(client, message):
    if db.get_user(message.from_user.id):
        db.update_user_state(message.from_user.id, "hanging")
    else:
        db.add_user(message.from_user.id)
    message.reply(config_messages.hello_message,
    reply_markup=markups.basic_markup)

@app.on_message(filters.regex("Главное меню"))
def show_main_menu(client, message):
    message.reply("Вот главное меню")

@app.on_message(filters.regex("Барное меню"))
def show_bar_menu(client, message):
    message.reply("Вот барное меню")

@app.on_message(filters.regex("Б/а меню"))
def show_nonalchive_menu(client, message):
    message.reply("Вот безалкогольное меню")

@app.on_message(filters.regex("Мероприятия"))
def show_events(client, message):
    message.reply("Мероприятия")

@app.on_message(filters.regex("Забронировать"))
def show_book(client, message):
    db.update_user_state(message.from_user.id, "typing_is_today")
    message.reply("Бронируете на сегодня?", reply_markup=markups.typing_is_today)

@app.on_message()
def messages(client, message):
    user_id = message.from_user.id
    current_state = db.get_user(user_id).current_state

    # Получаем ответ про бронь на сегодня
    if current_state == 'typing_is_today':
        if message.text == "Да":
            message.reply(config_messages.book_today_message, reply_markup=markups.basic_markup)
            db.update_user_state(user_id, 'hanging')
        elif message.text == "Назад":
            message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
            db.update_user_state(user_id, 'hanging')
        elif message.text == "Нет":
            db.update_user_state(user_id, 'typing_name')
            message.reply("На какое имя бронь?", reply_markup=markups.typing_name_state)

    # Получаем ответ на имя
    elif current_state == 'typing_name':
        if message.text == 'Назад':
            message.reply("Бронируете на сегодня?", reply_markup=markups.typing_is_today)
            db.update_user_state(message.from_user.id, "typing_is_today")
        elif message.text == 'Домой':
            message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
            db.update_user_state(user_id, 'hanging')
        elif message.text == 'Подсказка: введите имя выше': # Важно! При изменении подсказки не забыть ее тут поменять тоже
            message.reply("На какое имя бронь?", reply_markup=markups.typing_name_state)
        else:
            db.update_user_state(user_id, 'typing_n_guests')
            message.reply("Сколько будет гостей?", reply_markup=markups.typing_n_guests)

    # Получаем ответ про количество гостей
    elif current_state == 'typing_n_guests':
        if message.text == 'Назад':
            db.update_user_state(user_id, 'typing_name')
            message.reply("На какое имя бронь?", reply_markup=markups.typing_name_state)
        elif message.text == 'Домой':
            message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
            db.update_user_state(user_id, 'hanging')
        elif message.text == "От 10":
            pass
        elif message.text in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            db.update_user_state(user_id, 'typing_date')
            message.reply("Когда хотите прибыть?")
            message.reply("P.S. дальше я пока не сделал")

    # Получаем ответ про дату прибытия
    elif current_state == 'typing_date':
        if message.text == 'Назад':
            db.update_user_state(user_id, 'typing_n_guests')
            message.reply("Сколько будет гостей?", reply_markup=markups.typing_n_guests)
        elif message.text == 'Домой':
            message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
            db.update_user_state(user_id, 'hanging')
    
    # Получаем ответ про время приыбытия
            
app.run()

