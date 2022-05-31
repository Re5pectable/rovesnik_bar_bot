from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import time
from db import Order, Event, DB
from random import randint
from pyrogram import filters
import pandas as pd
from typing import List
from config import config

# BR - BOOK REFUSE  - отказатьс в бронировании
# BC - BOOK CONFIRM - подтвердить бронь

# DD - DEPOSIT DEMAND - запросить депозит
# DR - DEPOSIT REFUSED - клиент отказаться платить депоз
# DS - DEPOSIT SEND - клиент отправли депозит
# DC - DEPOSIT CONFIRMED - модер подтвердил депозит

# TO - TEN OFFER - встать в 10 вечера из-за стола
# TA - TEN ACCEPTED
# TD - TEN DECLINED

# GE - GET EVENT

def moder_markup(order: Order, confirmed=None):
    k = []
    if order.ten_offer:
        k.append([InlineKeyboardButton("Готов уйти в 10", callback_data="pass")])
    elif order.ten_offer is False:
        k.append([InlineKeyboardButton("❌ Отказался уйти в 10", callback_data="pass")])
    elif order.ten_offer is None:
        k.append([InlineKeyboardButton("Попросить уйти в 10", callback_data=f"TO{str(order.made_by_user)}")])

    if order.deposit and order.deposit_sent is None:
        k.append([InlineKeyboardButton("Попросить депозит", callback_data=f"DD{str(order.made_by_user)}")])
    elif order.deposit and order.deposit_sent:
        k.append([InlineKeyboardButton("Деп. отправлен", callback_data="pass")])
    elif order.deposit and order.deposit_sent is False:
        k.append([InlineKeyboardButton("❌ Отказался вносить деп.", callback_data="pass")])

    k.append([InlineKeyboardButton("🔴 Отказать", callback_data=f"BR{str(order.made_by_user)}")])
    k.append([InlineKeyboardButton("🟢 Подтвердить", callback_data=f"BC{str(order.made_by_user)}")])
    return InlineKeyboardMarkup(k)

def client_deposit_markup(user_id: int):
    k = []
    k.append([InlineKeyboardButton("Готово", callback_data=f"DC{str(user_id)}")])
    k.append([InlineKeyboardButton("Отказаться", callback_data=f"DR{str(user_id)}")])
    return InlineKeyboardMarkup(k)

def client_ten_clock_markup(user_id: int):
    k = []
    k.append([InlineKeyboardButton("Хорошо", callback_data=f"TA{str(user_id)}")])
    k.append([InlineKeyboardButton("Отказаться", callback_data=f"TD{str(user_id)}")])
    return InlineKeyboardMarkup(k)


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

def gen_moder_conf(order: Order):
    return f"• ТГ: **@{order.user_login}**\n" + \
           f"• Имя: **{order.name}**\n" + \
           f"• Дата: **{order.date}**\n" + \
           f"• Время: **{order.time}**\n" + \
           f"• Человек:  **{order.n_guests}**\n" + \
           f"• Телефон:  **{order.phone}**\n" + \
           f"• Депозит:  **{order.deposit}**"

def gen_usual_review(message):
    return f"[Беcкупонный отзыв]\n\n{message.text}"

def gen_coupon():
    res = ""
    let = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(5):
        res += let[randint(0, len(let)-1)]
    return res

def gen_coupons_message(coupons: list):
    res = ""
    for coupon in coupons:
        if coupon.type == 1:
            res += f"**{coupon.text}** - бесплатный кофе\n"
    res += "\nЧтобы активировать промокод, введите **/activate** [промокод]"
    res += "\nПосле этого подарок можно будет получить на кассе"
    return res

def create_updates_list(file_name: str):
    data = pd.read_excel(f"downloads/{file_name}")
    events = []
    for _, row in data.iterrows():
        events.append(Event(date=row[0],event_type=row[1],title=row[2],description=row[3]))
    return events

def events_markup(events: List[Event]):
    markup = []
    for i in range(len(events)):
        markup.append(InlineKeyboardButton(f"#{i+1}", callback_data=f"GE{events[i].id}"))
    return InlineKeyboardMarkup([markup[i:i + 4] for i in range(0, len(markup), 4)])

def gen_events_text(events: List[Event]):
    text = ""
    for i in range(len(events)):
        text += f"**#{i+1}** - {events[i].title} ({events[i].date.strftime('%d.%m')})\n\n"
    return text

def gen_event_text(event: Event):
    return f"**{event.title}**\n{event.date.strftime('%d.%m')}\n\n{event.description}"

def admin_filter(fit, _, message):
    res = DB().start_get_admins()
    if message.from_user.id in res:
        return True
    else:
        message.reply("Вас нет в списке администраторов")
        return False

def review_filter(fit, _, message):
    return message.reply_to_message.text.startswith("Как прошёл ваш вечер в Ровеснике?") and \
        message.reply_to_message.from_user.username.lower() == config.bot_name.lower()

admin_filter = filters.create(admin_filter)
review_filter = filters.create(review_filter)