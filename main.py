from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from config import config
from settings import *
from db import *
import time, datetime
import asyncio
from services import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler

print("--- START")
app = Client("sessions/rovesnik_bot", api_id = config.api_id, api_hash = config.api_hash, bot_token=config.bot_token)

try: app.disconnect()
except: pass

try: app.stop()
except: pass

print("--- Client is ready")


"hanging", "typing_is_today", "typing_name", "typing_n_guests", "typing_time", "typing_phone", "checking_info", "waiting_confirm", "sending_deposit", "typing_review_u"

# 0- до часа 
# 1- до 6 утра 
# 2- до часа

weekdays_mapping = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}
orders = {}

db = DB()
print("--- Database is ready")


# Админка
@app.on_message(filters.command("test") & filters.private & admin_filter)
async def test(client, message):
    test_order = Order(id=None, made_by_user=253410446, user_login='g1e6_b', name='fvg', n_guests='20', phone="2828127182", date='28.04', day_type='basic', weekday=3, time='11:00', deposit=20000, ten_offer=None, confirmed=False, deposit_sent=None, created=datetime.datetime(2022, 4, 25, 19, 5, 14, 522086))
    orders[message.from_user.id] = test_order
    await message.reply("Проверим еще разок\n\n"
                f"• Бронь на имя: **{orders[message.from_user.id].name}**\n"
                f"• Дата: **{orders[message.from_user.id].date}**\n"
                f"• Время: **{orders[message.from_user.id].time}**\n"
                f"• Количество гостей:  **{orders[message.from_user.id].n_guests}**\n"
                f"• Телефон:  **{orders[message.from_user.id].phone}**\n", reply_markup=markups.info_check)
    await db.update_user_state(message.from_user.id, "checking_info")

@app.on_message(filters.command("add_events") & admin_filter & filters.private)
async def add_events(client, message):
    if message.document:
        if ".xlsx" not in message.document.file_name:
            await message.reply("Отправьте файл в формате .xlsx (Столбцы: Дата, Формат, Название, Описание)")
            return
        await message.download()
        events = create_updates_list(message.document.file_name)
        await db.add_events(events)
        await message.reply(f"Добавлено {len(events)} событий!")
    else:
        await message.reply("Вы не отправили документ")

@app.on_message(filters.command("change_main_menu") & admin_filter & filters.private)
async def change_main_menu(client, message):
    if message.document:
        if message.document.file_name == "main_menu.pdf":
            await message.download("media/main_menu.pdf")
            await message.reply("Файл главного меню измнен")
        else:
            await message.reply("Пришлите файл **main_menu.pdf**")
    else:
        await message.reply("Вы не отправили документ")

@app.on_message(filters.command("change_bar") & admin_filter & filters.private)
async def change_bar(client, message):
    if message.document:
        if message.document.file_name == "bar.pdf":
            await message.download("media/bar.pdf")
            await message.reply("Файл бара измнен")
        else:
            await message.reply("Пришлите файл **bar.pdf**")
    else:
        await message.reply("Вы не отправили документ")

@app.on_message(filters.command("change_na_bar") & admin_filter & filters.private)
async def change_na_bar(client, message):
    if message.document:
        if message.document.file_name == "na_bar.pdf":
            await message.download("media/na_bar.pdf")
            await message.reply("Файл безалкогольного бара изменен")
        else:
            await message.reply("Пришлите файл **na_bar.pdf**")
    else:
        await message.reply("Вы не отправили документ")

@app.on_message(filters.command("admins") & admin_filter & filters.private)
async def get_all_admins(client, message):
    admins = await db.get_admins()
    text = ""
    for admin in admins:
        text += f"**tg_id**: {admin.tg_id}\n**tg_name**: {admin.tg_name}\n**added as admin**: {admin.added.strftime('%Y-%m-%d %H:%M')}\n\n"
    await message.reply(text)


@app.on_message(filters.command("add_admin") & admin_filter & filters.private)
async def add_admin(client, message):
    try:
        tg_id = int(message.text.split(" ")[1])
        tg_name = (await client.get_users(tg_id)).username
        await db.add_admin(Admin(tg_id=tg_id, tg_name=tg_name, added=datetime.datetime.now()))
        await message.reply(f"Пользователь {tg_id} (@{tg_name}) добавлен в администраторы")
    except Exception as e:
        await message.reply("После команды укажите ID пользователя (не @). Пример **/add_admin 123456789**. Также, такое сообщение может появиться, если пользователь не найден. Воспользуйтесь @getmyid_bot")

@app.on_message(filters.command("del_admin") & admin_filter & filters.private)
async def del_amin(client, message):
        try:
            tg_id = int(message.text.split(" ")[1])
            await db.delete_admin(tg_id)
            await message.reply(f"Пользователь {tg_id} удален из списка админов")
        except: 
            await message.reply("После команды укажите ID пользователя (не @). Пример **/del_admin 123456789**")

# Команды
@app.on_message(filters.command("activate") & filters.private)
async def activate_coupon(client, message):
    coupon = Coupon(tg_id=message.from_user.id, text=message.text.replace("/activate ", "").upper())
    users_coupons = await db.get_coupons_by_id(message.from_user.id)
    for c in users_coupons:
        if coupon.text == c.text:
            await db.delete_coupon(coupon)
            await message.reply_photo("media/type_1_promo.jpeg", caption=f"Прмокод **{coupon.text}** активирован!")
            return 
    await message.reply("У вас нет такого промокода")

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    if await db.get_user(message.from_user.id):
        await db.update_user(User(tg_id=message.from_user.id, current_state="hanging", last_activity=datetime.datetime.now()))
    else:
        await db.add_user(message.from_user.id)
    if message.from_user.id in orders.keys():
        del orders[message.from_user.id]
    await message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)

# Отзывы
@app.on_message(filters.private & filters.reply & review_filter)
async def review(client, message):
    try:
        await client.send_message(config.feedback_chat_id, f"[Купонный отзыв] \n\n{message.text}")
        reply = await message.reply("Спасибо за ваш отзыв! Вам добавлен промокод, его можно найти в главном меню.")
        await asyncio.sleep(3)
        await reply.delete()
        await client.delete_messages(chat_id=message.chat.id, message_ids=[message.message_id, message.reply_to_message_id])
        await db.add_coupon(Coupon(
            tg_id=message.from_user.id,
            text=gen_coupon(),
            type=1
        ))
    except:
        pass

@app.on_message(filters.regex("Главное меню") & filters.private)
async def show_main_menu(client, message):
    await client.send_document(message.from_user.id, "media/main_menu.pdf")
    await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))


@app.on_message(filters.regex("Барное меню") & filters.private)
async def show_bar_menu(client, message):
    await client.send_document(message.from_user.id, "media/bar.pdf")
    await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))


@app.on_message(filters.regex("Б/а меню") & filters.private)
async def show_nonalchive_menu(client, message):
    await client.send_document(message.from_user.id, "media/na_bar.pdf")
    await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))


@app.on_message(filters.regex("Мероприятия") & filters.private)
async def show_events(client, message):
    events = (await db.get_next_events(datetime.datetime.now()))
    await message.reply(f"Вот наши ближайшие мероприятия: \n\n{gen_events_text(events)}", reply_markup=events_markup(events))
    await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))

@app.on_message(filters.regex("Написать отзыв") & filters.private)
async def show_events(client, message):
    await message.reply("Поделитесь своим опытом от пребывания в нашем баре.", reply_markup=markups.usual_review)
    await db.update_user(User(tg_id=message.from_user.id, current_state="typing_review_u", last_activity=datetime.datetime.now()))

@app.on_message(filters.regex("Мои промокоды") & filters.private)
async def show_promocodes(client, message):
    promos = await db.get_coupons_by_id(message.from_user.id)
    if promos:
        await message.reply(gen_coupons_message(promos))
    else:
        await message.reply("У вас пока нет промокодов. Их можно получить, например, посетив наш бар и оставив отзыв.")


@app.on_message(filters.regex("Домой") & filters.private)
async def go_home(client, message):
    if message.from_user.id in orders.keys():
        del orders[message.from_user.id]
    await message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
    await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))


@app.on_message(filters.regex("Забронировать") & filters.private)
async def show_book(client, message):
    if message.from_user.id in orders.keys():
        await message.reply("У вас уже есть одна активная бронь. Дождитесь, когда придет подтверждение от модератора, это недолго :)")
    else:
        await db.update_user(User(tg_id=message.from_user.id, current_state="typing_is_today", last_activity=datetime.datetime.now()))
        await message.reply("Бронируете на сегодня?", reply_markup=markups.typing_is_today)

@app.on_message(filters.private)
async def activity(client, message):
    try:
        user_id = message.from_user.id
        current_state = (await db.get_user(user_id)).current_state

        # Получаем ответ про бронь на сегодня
        if current_state == 'typing_is_today':
            if message.text == "Да":
                await message.reply(config_messages.book_today_message, reply_markup=markups.basic_markup)
                await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))
            elif message.text == "Назад":
                await message.reply(config_messages.hello_message, reply_markup=markups.basic_markup)
                await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))
            elif message.text == "Нет":
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_name", last_activity=datetime.datetime.now()))
                await message.reply(config_messages.what_name, reply_markup=markups.typing_name_state)

        # Получаем ответ на имя
        elif current_state == 'typing_name':
            if message.text == 'Назад':
                await message.reply(config_messages.book_today_message, reply_markup=markups.typing_is_today)
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_is_today", last_activity=datetime.datetime.now()))
            elif message.text == 'Подсказка: введите имя выше': # Важно! При изменении подсказки не забыть ее тут поменять тоже
                await message.reply(config_messages.what_name, reply_markup=markups.typing_name_state)
            else:
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_n_guests", last_activity=datetime.datetime.now()))
                orders[message.from_user.id] = Order(made_by_user=message.from_user.id,user_login=message.from_user.username, name=message.text, created=datetime.datetime.now())
                await message.reply(config_messages.number_of_guests, reply_markup=markups.typing_n_guests)

        # Получаем ответ про количество гостей
        elif current_state == 'typing_n_guests':
            if message.text == 'Назад':
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_name", last_activity=datetime.datetime.now()))
                await message.reply(config_messages.what_name, reply_markup=markups.typing_name_state)
            elif message.text == "От 10":
                await message.reply("Для компаний от 10 человек у нас действует система депозита — 1000₽ с человека. Бронь вносим после оплаты. Если вам подходит, напишите, пожалуйста, точное количество человек например, **13**", reply_markup=markups.minimal)
            elif message.text.isdigit():
                if 0 < int(message.text) < 10:
                    await db.update_user(User(tg_id=message.from_user.id, current_state="typing_date", last_activity=datetime.datetime.now()))
                    orders[message.from_user.id].n_guests = message.text
                    await message.reply(config_messages.what_day, reply_markup=date_markup("current"))
                elif int(message.text) >= 10: # ситуация с 10+ гостями
                    await db.update_user(User(tg_id=message.from_user.id, current_state="typing_date", last_activity=datetime.datetime.now()))
                    orders[message.from_user.id].n_guests = message.text
                    orders[message.from_user.id].deposit = int(message.text) * 1000
                    await message.reply(config_messages.what_day, reply_markup=date_markup("current"))
                else: 
                    await message.reply("Некорректные данные")
            else: 
                await message.reply("Некорректные данные")

        # Получаем ответ про дату прибытия
        elif current_state == 'typing_date':
            if message.text == 'Назад':
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_n_guests", last_activity=datetime.datetime.now()))
                await message.reply(config_messages.number_of_guests, reply_markup=markups.typing_n_guests)
            elif message.text == "◀️◀️":
                await message.reply(config_messages.what_day, reply_markup=date_markup("current"))
            elif message.text == "▶️" or message.text == "◀️◀️◀️":
                await message.reply(config_messages.what_day, reply_markup=date_markup("next"))
            elif message.text == "▶️▶️":
                await message.reply(config_messages.what_day, reply_markup=date_markup("next-next"))
            elif message.text in [(datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%d.%m') for i in range(1, 21)]:
                weekday = get_weekday(message.text)
                day_type = get_day_type(weekday)
                if day_type == 'basic':
                    await message.reply(f"{weekdays_mapping[weekday]}, {message.text}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'party':
                    await message.reply(f"{weekdays_mapping[weekday]}, {message.text}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'live':
                    await message.reply(f"{weekdays_mapping[weekday]}, {message.text}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                orders[message.from_user.id].date = message.text
                orders[message.from_user.id].day_type = day_type
                orders[message.from_user.id].weekday = weekday
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_time", last_activity=datetime.datetime.now()))
            else:
                await message.reply("Не получилось распознать дату. Если вы вводите данные вручную, проверьте правильность формата: ДД.ММ")

        # Получаем ответ про время приыбытия
        elif current_state == 'typing_time':
            weekday = orders[message.from_user.id].weekday
            day_type = orders[message.from_user.id].day_type
            date = orders[message.from_user.id].date
            if message.text == 'Доб. 30 минут':
                if orders[message.from_user.id].day_type == 'basic':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=True))

                elif orders[message.from_user.id].day_type == 'party':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=True))

                elif orders[message.from_user.id].day_type == 'live':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=True))
            elif message.text == 'Убр. 30 минут':
                if orders[message.from_user.id].day_type == 'basic':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif orders[message.from_user.id].day_type == 'party':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif orders[message.from_user.id].day_type == 'live':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))
            
            elif message.text == "Назад":
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_date", last_activity=datetime.datetime.now()))
                await message.reply(config_messages.what_day, reply_markup=date_markup("current"))
            elif len(message.text) == 5 and ":" in message.text:
                splitted = message.text.split(":")
                if (9 <= int(splitted[0]) < 24) and (splitted[1] == "30" or splitted[1] == "00"):
                    orders[message.from_user.id].time = message.text
                    await message.reply(config_messages.phone, reply_markup=markups.minimal)
                    await db.update_user(User(tg_id=message.from_user.id, current_state="typing_phone", last_activity=datetime.datetime.now()))
                else:
                    await message.reply("Таких слотов у нас нет. Мы размещаем только в XX:00 или в XX:30 и лишь в определенные часы. Рекомендуем воспользоваться вспомогательными кнопками")

            else:
                await message.reply("Не получилось распознать время. Если вы вводите данные самостоятельно, соблюдайте формат ЧЧ:ММ.")

        elif current_state == 'typing_phone':
            phone = ''.join([n for n in message.text if n.isdigit()])
            if 7 < len(phone) < 15 and (phone.startswith('7') or phone.startswith('+7') or phone.startswith('8')):
                orders[message.from_user.id].phone = phone
                await message.reply("Проверим еще разок\n\n"
                            f"• Бронь на имя: **{orders[message.from_user.id].name}**\n"
                            f"• Дата: **{orders[message.from_user.id].date}**\n"
                            f"• Время: **{orders[message.from_user.id].time}**\n"
                            f"• Количество гостей:  **{orders[message.from_user.id].n_guests}**\n"
                            f"• Телефон:  **{orders[message.from_user.id].phone}**\n", reply_markup=markups.info_check)
                await db.update_user(User(tg_id=message.from_user.id, current_state="checking_info", last_activity=datetime.datetime.now()))
            elif message.text == "Назад":
                weekday = orders[message.from_user.id].weekday
                day_type = orders[message.from_user.id].day_type
                date = orders[message.from_user.id].date
                if day_type == 'basic':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'party':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 06. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))

                elif day_type == 'live':
                    await message.reply(f"{weekdays_mapping[weekday]}, {date}\n\n"
                                "Напоминаем, Мы работаем с 09 до 01. Какое время вас интересует?", reply_markup=time_markup(day_type=day_type, halved=False))
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_time", last_activity=datetime.datetime.now()))
            else:
                await message.reply("Не похоже на номер телефона. Повторите попытку")

        elif current_state == 'checking_info':
            if message.text == 'Да':
                await message.reply("Ваша заявка отправлена нашему сотруднику для подтверждения. В ближайшее время вы получите дальнейшие инструкции, так что не теряйте наш чат.", reply_markup=markups.basic_markup)
                await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))
                await client.send_message(config.moders_chat_id, gen_moder_conf(orders[message.from_user.id]), reply_markup=moder_markup(orders[message.from_user.id]))
            elif message.text == 'Назад':
                await db.update_user(User(tg_id=message.from_user.id, current_state="typing_phone", last_activity=datetime.datetime.now()))
                await message.reply(config_messages.phone, reply_markup=markups.minimal)

        elif current_state == 'typing_review_u':
            await client.send_message(config.feedback_chat_id, gen_usual_review(message))
            await message.reply("Спасибо за ваш отзыв!", reply_markup=markups.basic_markup)
            await db.update_user(User(tg_id=message.from_user.id, last_activity=datetime.datetime.now()))
            
    except Exception as e:
        print(e)
        await message.reply("У нас что-то пошло не так. Попробуйте нажать /start")


@app.on_callback_query()
async def calbacks(client, callback_query):
    # === Базовое для брони ===
    # Подтверждение брони
    if callback_query.data[:2] == 'BC':
        await callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("ПОДТВЕРЖДЕНО", callback_data="pass")]]))
        user_id = int(callback_query.data[2:])
        await client.send_message(user_id, f"Ждем в Ровеснике **{orders[user_id].date}** в **{orders[user_id].time}**!\nЕсли вы задерживаетесь больше, чем на 15 минут, позвоните, пожалуйста, по телефону **8 (999) 912-72-85**, иначе нам придётся снять бронь. Как придете, обратитесь к менеджеру – вас посадят (можно попросить позвать на баре)")
        await db.add_scheduled_message(ScheduledMessage(
            to_id=user_id,
            time=datetime.datetime.strptime(f'{orders[user_id].date}.{datetime.datetime.today().year} {orders[user_id].time}', '%d.%m.%Y %H:%M') + datetime.timedelta(hours=24),
            type=1
        ))
        del orders[user_id]
    # Отказ в брони
    elif callback_query.data[:2] == 'BR':
        await callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("ОТКАЗАНО", callback_data="pass")]]))
        user_id = int(callback_query.data[2:])
        await client.send_message(user_id, f"Ваше бронирование отменилось")
        del orders[user_id]
        

    # === Предложение пересесть в 10 ===
    # Предложение
    elif callback_query.data[:2] == 'TO':
        user_id = int(callback_query.data[2:])
        orders[user_id].ten_offer = False
        await callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("Ждем ответа про 22:00", callback_data="pass")]]))
        await client.send_message(user_id, f"В пятницу и субботу мы заканчиваем обслуживание в зале, убираем часть столов и начинаем готовиться к вечеринке. Вам подойдёт, если ваш столик будет до 22:00?", reply_markup=client_ten_clock_markup(user_id))
    
    # Принятие
    elif callback_query.data[:2] == 'TA':
        user_id = int(callback_query.data[2:])
        orders[user_id].ten_offer = True
        await callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("Вы согласились", callback_data="pass")]]))
        await client.send_message(config.moders_chat_id, gen_moder_conf(orders[user_id]), reply_markup=moder_markup(orders[user_id]))

    # Отказ
    elif callback_query.data[:2] == 'TD':
        user_id = int(callback_query.data[2:])
        orders[user_id].ten_offer = False
        await callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("Вы отказались", callback_data="pass")]]))
        await client.send_message(config.moders_chat_id, gen_moder_conf(orders[user_id]), reply_markup=moder_markup(orders[user_id]))

    # === Все про депозит ===
    # Потребовать депозит
    elif callback_query.data[:2] == 'DD':
        user_id = int(callback_query.data[2:])
        await callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[InlineKeyboardButton("Ждем депозит", callback_data="pass")]]))
        await client.send_message(user_id, f"Переведите, пожалуйста, депозит нам по номеру телефона ниже и пришлите скриншот:\nСБЕРБАНК\n89151549863\nЛюбовь Ю. Ю.", reply_markup=client_deposit_markup(user_id))
    
    # Клиент нажал отправлено
    elif callback_query.data[:2] == 'DC':
        user_id = int(callback_query.data[2:])
        orders[user_id].deposit_sent = True
        await client.send_message(config.moders_chat_id, gen_moder_conf(orders[user_id]), reply_markup=moder_markup(orders[user_id]))

    # Клиент отказался
    elif callback_query.data[:2] == 'DR':
        user_id = int(callback_query.data[2:])
        orders[user_id].deposit_sent = False
        await client.send_message(config.moders_chat_id, gen_moder_conf(orders[user_id]), reply_markup=moder_markup(orders[user_id]))

    # === Мероприятия ===
    # Получить данные о мероприятии
    elif callback_query.data[:2] == 'GE':
        event_id = callback_query.data[2:]
        event = await db.get_event_by_id(event_id)
        await client.send_message(callback_query.from_user.id, gen_event_text(event))

print("--- Methods are loaded")

async def bot_service():
    temp = []   
    for message in await db.get_all_scheduled():
        if message.time < datetime.datetime.now():
            temp.append(message)
            if message.type == 1: # Через 24 часа после посещения
                await app.send_message(message.to_id, "Как прошёл ваш вечер в Ровеснике? (Чтобы ваш отзыв засчитался, пожалуйста ОТВЕТЬТЕ на это сообщение. Для этого можно потянуть сообщение вправо или воспользоваться долгим нажатием)")
    await db.delete_scheduled_messages(temp)

    for person in await db.get_afk():
        await db.update_user(User(tg_id=person.tg_id, last_activity=datetime.datetime.now(), was_asked=True))
        await app.send_message(person.tg_id, "Просто напоминаем о себе :) \n\nНе хотите ли забронировать столик?", reply_markup=markups.basic_markup)
        if person.tg_id in orders.keys():
            del orders[person.tg_id]


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(bot_service, "interval", seconds=20)
    
    scheduler.start()
    print("--- Bot is ready")
    app.run()