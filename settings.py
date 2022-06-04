from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import time
from db import Order

class ConfigMessages:
    hello_message = "Привет, это Ровесник! Меню управления ⬇️"
    book_today_message = "Для брони день в день позвоните, пожалуйста, по номеру телефона с 12:00 – +7(999)912-72-85"
    what_name = "На какое имя бронь?"
    number_of_guests = "Сколько будет гостей?"
    what_day = "На какой день будет бронь?"
    phone = "Введите номер телефона"

class ConfigMarkups:
    basic_markup = ReplyKeyboardMarkup([["Меню"], ['Написать отзыв', "Забронировать"], ["Мероприятия", "FAQ" ,"Мои промокоды"]], resize_keyboard=True)
    typing_is_today = ReplyKeyboardMarkup([["Да", "Нет"], ["Назад"]], resize_keyboard=True)
    typing_name_state = ReplyKeyboardMarkup([["Подсказка: введите имя выше"], ["Назад", "Домой"]], resize_keyboard=True)
    typing_n_guests = ReplyKeyboardMarkup([["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["Назад", "От 10", "Домой"]], resize_keyboard=True)
    minimal = ReplyKeyboardMarkup([["Назад", "Домой"]], resize_keyboard=True)
    info_check = ReplyKeyboardMarkup([["Да"], ["Назад", "Домой"]], resize_keyboard=True)
    usual_review = ReplyKeyboardMarkup([["Домой"]], resize_keyboard=True)

config_messages = ConfigMessages()
markups = ConfigMarkups()