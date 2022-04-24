from pyrogram.types import ReplyKeyboardMarkup
import time
class ConfigMessages:
    hello_message = "Привет, это Ровесник! Ниже кнопки для управления"
    book_today_message = "Если бронь на сегодня то сюда"
    what_name = "На какое имя бронь?"
    number_of_guests = "Сколько будет гостей?"
    what_day = "На какой день будет бронь?"
    phone = "Введите номер телефона"

class ConfigMarkups:
    basic_markup = ReplyKeyboardMarkup([["Главное меню", "Барное меню", "Б/а меню"], ["Мероприятия", "Забронировать"]], resize_keyboard=True)
    typing_is_today = ReplyKeyboardMarkup([["Да", "Нет"], ["Назад"]], resize_keyboard=True)
    typing_name_state = ReplyKeyboardMarkup([["Подсказка: введите имя выше"], ["Назад", "Домой"]], resize_keyboard=True)
    typing_n_guests = ReplyKeyboardMarkup([["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["Назад", "От 10", "Домой"]], resize_keyboard=True)
    minimal = ReplyKeyboardMarkup([["Назад", "Домой"]], resize_keyboard=True)
    info_check = ReplyKeyboardMarkup([["Да", "Нет"], ["Назад", "Домой"]], resize_keyboard=True)

config_messages = ConfigMessages()
markups = ConfigMarkups()

import datetime

def date_markup(week="current"):
    m = [[], []]
    if week == "current":
        for i in range(1, 7):
            day = datetime.datetime.now() + datetime.timedelta(days=i)
            m[0].append(day.strftime('%d.%m'))
        m[1] = ["Назад", "▶️", "Домой"]
    elif week == 'next':
        for i in range(7, 14):
            day = datetime.datetime.now() + datetime.timedelta(days=i)
            m[0].append(day.strftime('%d.%m'))
        m[1] = ["Назад", "◀️◀️", "▶️▶️", "Домой"]
    elif week == 'next-next':
        for i in range(14, 21):
            day = datetime.datetime.now() + datetime.timedelta(days=i)
            m[0].append(day.strftime('%d.%m'))
        m[1] = ["Назад", "◀️◀️◀️", "Домой"]
    return ReplyKeyboardMarkup(m, resize_keyboard=True)


def time_markup(day_type: str = 'basic', halved: bool = False):
    t = [[], [], [], []]
    temp = []
    if day_type == 'basic':
        if not halved:
            for i in range(15):
                h = datetime.datetime.strptime("09:00", "%H:%M") + datetime.timedelta(hours=i)
                temp.append(h.strftime("%H:%M"))
            temp.append("23:55")
            t[3] = ["Назад", "Доб. 30 минут", "Домой"]
        else: 
            for i in range(15):
                h = datetime.datetime.strptime("09:30", "%H:%M") + datetime.timedelta(hours=i)
                temp.append(h.strftime("%H:%M"))
            t[3] = ["Назад", "Убр. 30 минут", "Домой"]
    elif day_type == 'live' or "party":
        if not halved:
            for i in range(13):
                h = datetime.datetime.strptime("09:00", "%H:%M") + datetime.timedelta(hours=i)
                temp.append(h.strftime("%H:%M"))
            t[3] = ["Назад", "Доб. 30 минут", "Домой"]
        else: 
            for i in range(12):
                h = datetime.datetime.strptime("09:30", "%H:%M") + datetime.timedelta(hours=i)
                temp.append(h.strftime("%H:%M"))
            t[3] = ["Назад", "Убр. 30 минут", "Домой"]
    t[0] = temp[:5]
    t[1] = temp[5:10]
    t[2] = temp[10:]
    return ReplyKeyboardMarkup(t, resize_keyboard=True)