from posixpath import splitext
from pyrogram import Client, filters
from config import config
from settings import config_messages, markups, date_markup, time_markup
from db import db, User
import time
import datetime
from db import Order

app = Client("sessions/rovesnik", api_id = config.api_id, api_hash = config.api_hash, bot_token = config.bot_token)

user_states = ["hanging", "typing_is_today", "typing_name", "typing_n_guests", "typing_time", "typing_phone", "checking_info", "waiting_confirm", "sending_deposit", "typing_review"]

weekdays = [0, 1, 2, 3]
parties = [4, 5]
lives = [6]

weekdays_mapping = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}

orders = {}
# {"tg_id": {name: , time:, etc}}

def get_weekday(date: str):
    return datetime.datetime.strptime(f'{date}.{datetime.datetime.today().year}', '%d.%m.%Y').weekday()

def get_day_type(weekday: int, extra_search=False):
    if not extra_search:
        if weekday in [0, 1, 2, 3]:
            return "basic"
        elif weekday in [4, 5]:
            return "party"
        elif weekday == 6:
            return "live"

@app.on_message(filters.command("start"))
def start_command(client, message):
    if db.get_user(message.from_user.id):
        db.update_user_state(message.from_user.id, "hanging")
    else:
        db.add_user(message.from_user.id)
    if message.from_user.id in orders.keys():
        del orders[message.from_user.id]
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
    try:
        s = time.time()
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
                message.reply(config_messages.what_name, reply_markup=markups.typing_name_state)

        # Получаем ответ на имя
        elif current_state == 'typing_name':
            if message.text == 'Назад':
                message.reply(config_messages.book_today_message, reply_markup=markups.typing_is_today)
                db.update_user_state(message.from_user.id, "typing_is_today")
            elif message.text == 'Домой':
                message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
                db.update_user_state(user_id, 'hanging')
            elif message.text == 'Подсказка: введите имя выше': # Важно! При изменении подсказки не забыть ее тут поменять тоже
                message.reply(config_messages.what_name, reply_markup=markups.typing_name_state)
            else:
                db.update_user_state(user_id, 'typing_n_guests')
                orders[message.from_user.id] = Order(made_by_user=message.from_user.id, name=message.text, created=datetime.datetime.now())
                message.reply(config_messages.number_of_guests, reply_markup=markups.typing_n_guests)

        # Получаем ответ про количество гостей
        elif current_state == 'typing_n_guests':
            if message.text == 'Назад':
                db.update_user_state(user_id, 'typing_name')
                message.reply(config_messages.what_name, reply_markup=markups.typing_name_state)
            elif message.text == 'Домой':
                message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
                db.update_user_state(user_id, 'hanging')
            elif message.text == "От 10":
                message.reply("Для группы больше десяти человек у нас особые правила. Напечатайте количество, например, **13**", reply_markup=markups.minimal)
            elif message.text.isdigit():
                if 0 < int(message.text) < 10:
                    db.update_user_state(user_id, 'typing_date')
                    orders[message.from_user.id].n_guests = message.text
                    message.reply(config_messages.what_day, reply_markup=date_markup("current"))
                elif int(message.text) >= 10: # ситуация с 10+ гостями
                    db.update_user_state(user_id, 'typing_date')
                    orders[message.from_user.id].n_guests = message.text
                    orders[message.from_user.id].deposit = int(message.text) * 1000
                    message.reply(config_messages.what_day, reply_markup=date_markup("current"))
                else: 
                    message.reply("Некорректные данные")
            else: 
                message.reply("Некорректные данные")

        # Получаем ответ про дату прибытия
        elif current_state == 'typing_date':
            if message.text == 'Назад':
                db.update_user_state(user_id, 'typing_n_guests')
                message.reply(config_messages.number_of_guests, reply_markup=markups.typing_n_guests)
            elif message.text == 'Домой':
                message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
                db.update_user_state(user_id, 'hanging')
            elif message.text == "◀️◀️":
                message.reply(config_messages.what_day, reply_markup=date_markup("current"))
            elif message.text == "▶️" or message.text == "◀️◀️◀️":
                message.reply(config_messages.what_day, reply_markup=date_markup("next"))
            elif message.text == "▶️▶️":
                message.reply(config_messages.what_day, reply_markup=date_markup("next-next"))
            elif message.text in [(datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%d.%m') for i in range(1, 21)]:
                weekday = get_weekday(message.text)
                day_type = get_day_type(weekday)
                if day_type == 'basic':
                    message.reply(f"{weekdays_mapping[weekday]}, {message.text}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'party':
                    message.reply(f"{weekdays_mapping[weekday]}, {message.text}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'live':
                    message.reply(f"{weekdays_mapping[weekday]}, {message.text}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                orders[message.from_user.id].date = message.text
                orders[message.from_user.id].day_type = day_type
                orders[message.from_user.id].weekday = weekday
                db.update_user_state(user_id, 'typing_time')
            else:
                message.reply("Не получилось распознать дату. Если вы вводите данные вручную, проверьте правильность формата: ДД.ММ")

        # Получаем ответ про время приыбытия
        elif current_state == 'typing_time':
            weekday = orders[message.from_user.id].weekday
            day_type = orders[message.from_user.id].day_type
            date = orders[message.from_user.id].date
            if message.text == 'Доб. 30 минут':
                if orders[message.from_user.id].day_type == 'basic':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=True))

                elif orders[message.from_user.id].day_type == 'party':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=True))

                elif orders[message.from_user.id].day_type == 'live':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=True))
            elif message.text == 'Убр. 30 минут':
                if orders[message.from_user.id].day_type == 'basic':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif orders[message.from_user.id].day_type == 'party':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif orders[message.from_user.id].day_type == 'live':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))
            
            elif message.text == "Назад":
                db.update_user_state(user_id, 'typing_date')
                message.reply(config_messages.what_day, reply_markup=date_markup("current"))
            elif message.text == 'Домой':
                message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
                db.update_user_state(user_id, 'hanging')
            elif len(message.text) == 5 and ":" in message.text:
                splitted = message.text.split(":")
                if (9 < int(splitted[0]) < 24) and (splitted[1] == "30" or splitted[1] == "00"):
                    orders[message.from_user.id].time = message.text
                    message.reply(config_messages.phone, reply_markup=markups.minimal)
                    db.update_user_state(user_id, 'typing_phone')
                else:
                    message.reply("Не получилось распознать время. Если вы вводите данные самостоятельно, соблюдайте формат ЧЧ:ММ.")

            else:
                message.reply("Не получилось распознать время. Если вы вводите данные самостоятельно, соблюдайте формат ЧЧ:ММ.")

        elif current_state == 'typing_phone':
            phone = ''.join([n for n in message.text if n.isdigit()])
            if 7 < len(phone) < 15:
                orders[message.from_user.id].phone = phone
                message.reply("Проверим еще разок\n\n"
                            f"• Бронь на имя: **{orders[message.from_user.id].name}**\n"
                            f"• Дата: **{orders[message.from_user.id].date}**\n"
                            f"• Время: **{orders[message.from_user.id].time}**\n"
                            f"• Гостей будет:  **{orders[message.from_user.id].n_guests}**\n"
                            f"• Телефон:  **{orders[message.from_user.id].phone}**\n", reply_markup=markups.info_check)
                db.update_user_state(user_id, "checking_info")
            elif message.text == "Назад":
                weekday = orders[message.from_user.id].weekday
                day_type = orders[message.from_user.id].day_type
                date = orders[message.from_user.id].date
                if day_type == 'basic':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'party':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'live':
                    message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))
                db.update_user_state(user_id, 'typing_time')
            else:
                message.reply("Не похоже на номер телефона. Повторите попытку")

        elif current_state == 'checking_info':
            if message.text == 'Да':
                message.reply("Ваша заявка отправлена нашему сотруднику для подтверждения. В ближайшее время вы получите дальнейшие инструкции, так что не теряйте наш чат.")
                client.send_message(config.moders_chat_id,  f"• ТГ: **@{message.from_user.username}**\n"
                                                            f"• Имя: **{orders[message.from_user.id].name}**\n"
                                                            f"• Дата: **{orders[message.from_user.id].date}**\n"
                                                            f"• Время: **{orders[message.from_user.id].time}**\n"
                                                            f"• Человек:  **{orders[message.from_user.id].n_guests}**\n"
                                                            f"• Телефон:  **{orders[message.from_user.id].phone}**\n"
                                                            f"• Депозит:  **{orders[message.from_user.id].deposit}**\n")

        else:
            pass
    except:
        message.reply("У нас что-то пошло не так. Попробуйте нажать /start")
    
    print(time.time() - s)
    print(message.text, current_state)
    print(orders)

app.run()

