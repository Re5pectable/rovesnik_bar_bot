from pyrogram.types import ReplyKeyboardMarkup

class ConfigMessages:
    hello_message = "Привет, это Ровесник! Ниже кнопки для управления"
    book_today_message = "Если бронь на сегодня то сюда"
    what_name = "На какое имя бронь?"
    number_of_guests = "Сколько будет гостей?"
    what_day = "На какой день будет бронь?" 

class ConfigMarkups:
    basic_markup = ReplyKeyboardMarkup([["Главное меню", "Барное меню", "Б/а меню"], ["Мероприятия", "Забронировать"]], resize_keyboard=True)
    typing_is_today = ReplyKeyboardMarkup([["Да", "Нет"], ["Назад"]], resize_keyboard=True)
    typing_name_state = ReplyKeyboardMarkup([["Подсказка: введите имя выше"], ["Назад", "Домой"]], resize_keyboard=True)
    typing_n_guests = ReplyKeyboardMarkup([["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["Назад", "От 10", "Домой"]])

config_messages = ConfigMessages()
markups = ConfigMarkups()