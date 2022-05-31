import sqlite3
from unittest.mock import Base
from pydantic import BaseModel
import datetime
import aiosqlite
import asyncio
from typing import List
import time

class User(BaseModel):
    id: int = None
    tg_id: int
    current_state: str = "hanging"
    last_activity: datetime.datetime
    was_asked: bool = False

class Order(BaseModel):
    id: int = None
    made_by_user: int = None
    user_login: str = None
    name: str = None
    n_guests: int = None
    phone: str = None
    date: str = None
    day_type: str = None
    weekday: int = None
    time: str = None
    deposit: int = None
    ten_offer: bool = None
    confirmed: bool = False
    deposit_sent: bool = None
    created: datetime.datetime = None

class Event(BaseModel):
    id: int = None
    date: datetime.datetime
    title: str
    description: str
    event_type: str

class ScheduledMessage(BaseModel):
    id: int = None
    to_id: int
    time: datetime.datetime
    type: int

class Coupon(BaseModel):
    tg_id: int
    type: int = None
    text: str

class Admin(BaseModel):
    tg_id: int
    tg_name: str
    added: datetime.datetime

CREATE_TABLE_USERS = "create table if not exists users \
    (id integer primary key autoincrement, \
    made_by_id int, \
    name varchar(32), \
    n_guests int, \
    phone varchar(16), \
    date datetime, \
    time datetime, \
    deposit tinyint(1), \
    confirmed tinyint(1));"
CREATE_TABLE_EVENTS = "create table if not exists events \
    (id integer primary key autoincrement, \
    date datetime, \
    title text, \
    description text, \
    event_type tinyint(3));"
CREATE_TABLE_SCHEDULED = "create table if not exists scheduled \
    (id integer primary key autoincrement, \
    to_id int, \
    time datetime, \
    type int);"
CREATE_TABLE_COUPONS = "create table if not exists coupons \
    (id integer primary key autoincrement, \
    tg_id int, \
    type int, \
    text varchar(5));"
CREATE_TABLE_ADMINS = "create table if not exists admins \
    (id integer primary key autoincrement,\
    tg_id int,\
    tg_name varchar(32),\
    added datetime);"

class DB:
    def __init__(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute(CREATE_TABLE_EVENTS)
            c.execute(CREATE_TABLE_USERS)
            c.execute(CREATE_TABLE_SCHEDULED)
            c.execute(CREATE_TABLE_COUPONS)
            c.execute(CREATE_TABLE_ADMINS)

    # ===============
    # CREATING TABLES
    # ===============
    async def create_table_orders(self, recreate=False):
        async with aiosqlite.connect("database.sqlite") as db:
            if recreate:
                await db.execute("drop table if exists orders")
            await db.execute(CREATE_TABLE_USERS)
            await db.commit()

    async def create_table_users(self, recreate=False):
        async with aiosqlite.connect("database.sqlite") as db:
            if recreate:
                await db.execute("drop table if exists users")
            await db.execute(CREATE_TABLE_USERS)
            await db.commit()

    async def create_table_events(self, recreate=False):
        async with aiosqlite.connect("database.sqlite") as db:
            if recreate:
                await db.execute("drop table if exists events")
            await db.execute(CREATE_TABLE_EVENTS)
            await db.commit()

    async def create_table_coupons(self, recreate=False):
        async with aiosqlite.connect("database.sqlite") as db:
            if recreate:
                await db.execute("drop table if exists coupons")
            await db.execute(CREATE_TABLE_COUPONS)
            await db.commit()

    async def create_table_admins(self, recreate=False):
        async with aiosqlite.connect("database.sqlite") as db:
            if recreate:
                await db.execute("drop table if exists admins")
            await db.execute(CREATE_TABLE_ADMINS)
            await db.commit()

    # ADMINS
    def start_get_admins(self):
        with sqlite3.connect("database.sqlite") as db:
            res = db.execute("select tg_id from admins").fetchall()
            return [r[0] for r in res]

    async def get_admins(self):
        async with aiosqlite.connect("database.sqlite") as db:
            res = await (await db.execute("select * from admins")).fetchall()
            return [Admin(tg_id=r[1], tg_name=r[2], added=r[3]) for r in res]

    async def add_admin(self, admin: Admin):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"insert into admins (tg_id, tg_name, added) values ({admin.tg_id}, '@{admin.tg_name}', '{admin.added}')")
            await db.commit()

    async def delete_admin(self, tg_id):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"delete from admins where tg_id='{tg_id}'")
            await db.commit()
    

    # =====
    # USERS
    # =====
    async def add_user(self, tg_id: int, current_state: str = "hanging"):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"insert into users (tg_id, current_state) values ('{tg_id}', '{current_state}')")
            await db.commit()

    async def get_user(self, tg_id: int):
        async with aiosqlite.connect("database.sqlite") as db:
            r = await (await db.execute(f"select * from users where tg_id = '{tg_id}'")).fetchone()
            if r: return User(id=r[0], tg_id=r[1], current_state=r[2], last_activity=r[3], was_asked=r[4])

    async def update_user_state(self, tg_id: int, current_state: str):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"update users set current_state='{current_state}' where tg_id='{tg_id}'")
            await db.commit()

    async def update_user(self, user: User):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"update users set current_state='{user.current_state}', \
                last_activity='{user.last_activity}', \
                    was_asked={user.was_asked} \
                        where tg_id='{user.tg_id}';")
            await db.commit()


    # =======
    # COUPONS
    # =======
    async def add_coupon(self, coupon: Coupon):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"insert into coupons (tg_id, type, text) values ('{coupon.tg_id}','{coupon.type}', '{coupon.text}')")
            await db.commit()

    async def get_coupons_by_id(self, tg_id: int):
        async with aiosqlite.connect("database.sqlite") as db:
            res = await (await db.execute(f"select type, text from coupons where tg_id = '{tg_id}'")).fetchall()
            return [Coupon(tg_id=tg_id, type=r[0], text=r[1]) for r in res]

    async def delete_coupon(self, coupon: Coupon):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"delete from coupons where tg_id='{coupon.tg_id}' and text='{coupon.text}'")
            await db.commit()


    # ==================
    # SCHEDULED MESSAGES
    # ==================
    async def add_scheduled_message(self, message: ScheduledMessage):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"insert into scheduled (to_id, time, type) values ('{message.to_id}', '{message.time}', '{message.type}')")
            await db.commit()

    async def get_all_scheduled(self):
        async with aiosqlite.connect("database.sqlite") as db:
            res = await (await db.execute(f"select * from scheduled")).fetchall()
            return [ScheduledMessage(id=r[0], to_id=r[1], time=r[2], type=r[3]) for r in res]
    
    async def delete_scheduled_messages(self, messages: List[ScheduledMessage]):
        async with aiosqlite.connect("database.sqlite") as db:
            await db.execute(f"delete from scheduled where id in ({', '.join([str(mes.id) for mes in messages])})")
            await db.commit()

    # ======
    # EVENTS
    # ======
    async def get_events_in_date(self, date: datetime.datetime):
        async with aiosqlite.connect("database.sqlite") as db:
            res = await (await db.execute(f"select * from events where \
                strftime('%Y-%m-%d', date) = date('{date.strftime('%Y-%m-%d')}')")).fetchall()
            return [Event(id=r[0], date=r[1], title=r[2], description=r[3], event_type=r[4]) for r in res]

    async def get_next_events(self, date: datetime.datetime):
        async with aiosqlite.connect("database.sqlite") as db:
            res = await (await db.execute(f"select * from events where strftime('%Y-%m-%d', date) > date({date.strftime('%Y-%m-%d')}) ORDER BY date ASC;")).fetchall()
            return [Event(id=r[0], date=r[1], title=r[2], description=r[3], event_type=r[4]) for r in res[:12]]
    
    async def get_event_by_id(self, event_id: int):
        async with aiosqlite.connect("database.sqlite") as db:
            res = await (await db.execute(f"select * from events where id = {event_id}")).fetchone()
            return Event(date=res[1], title=res[2], description=res[3], event_type=res[4])

    async def add_events(self, events: List[Event]):
        async with aiosqlite.connect("database.sqlite") as db:
            query = ""
            for event in events:
                query += f"{event.date.strftime('%Y-%m-%d %H:%M'), event.title, event.description, event.event_type},"
            await db.execute(f"insert into events (date, title, description, event_type) values\
                {query[:-1]};")
            await db.commit()

    # ===
    # AFK
    # ===
    async def get_afk(self):
        async with aiosqlite.connect("database.sqlite") as db:
            res = await (await db.execute(f"select * from users where strftime('%s', last_activity) \
                                                BETWEEN strftime('%s', '2022-01-01 00:00:00.000000') \
                                                AND strftime('%s', '{datetime.datetime.now() - datetime.timedelta(hours=12)}') \
                                                and was_asked={False}")).fetchall()
            return [User(id=r[0], tg_id=r[1], current_state=r[2], last_activity=r[3], was_asked=r[4]) for r in res]


# async def main():
#     db = DB()
#     await db.create_table_admins(recreate=True)

# asyncio.run(main())