import sqlite3
from unittest.mock import Base
from pydantic import BaseModel
import datetime
from typing import Union
import aiosqlite
import asyncio

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
    date: str
    time: str
    title: str
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



class DB:
    def __init__(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("create table if not exists users (id integer primary key autoincrement, made_by_id int, name varchar(32), n_guests int, phone varchar(16), date datetime, time datetime, deposit tinyint(1), confirmed tinyint(1));")
            c.execute("create table if not exists orders (id integer primary key autoincrement, made_by_id int, name varchar(32), n_guests int, phone varchar(16), date datetime, time datetime, deposit tinyint(1), confirmed tinyint(1));")
            c.execute("create table if not exists events (id integer primary key autoincrement, date datetime, time datetime, title text, event_type varchar(16));")
            c.execute("create table if not exists scheduled (id integer primary key autoincrement, to_id int, time datetime, type int);")
            c.execute("create table if not exists coupons (id integer primary key autoincrement, tg_id int, type int, text varchar(5));")


    async def initialize_db(self):
        self.con  = await aiosqlite.connect("database.sqlite")

    async def recreate_table_orders(self):
        await self.con.execute("drop table if exists orders")
        await self.con.execute("create table orders (id integer primary key autoincrement, made_by_id int, name varchar(32), n_guests int, phone varchar(16), date datetime, time datetime, deposit tinyint(1), confirmed tinyint(1));")
        await self.con.commit()

    async def recreate_table_users(self):
            await self.con.execute("drop table if exists users")
            await self.con.execute("create table users (id integer primary key autoincrement, tg_id int, current_state varchar(16), last_activity datetime, was_asked tinyint(1));")
            await self.con.commit()

    async def recreate_table_events(self):
        await self.con.execute("drop table if exists events")
        await self.con.execute("create table events (id integer primary key autoincrement, date datetime, time datetime, title text, event_type varchar(16));")            
        await self.con.commit()

    async def add_user(self, tg_id: int, current_state: str = "hanging"):
        await self.con.execute(f"insert into users (tg_id, current_state) values ('{tg_id}', '{current_state}')")
        await self.con.commit()

    async def get_user(self, tg_id: int):
        r = await (await self.con.execute(f"select * from users where tg_id = '{tg_id}'")).fetchone()
        if r: return User(id=r[0], tg_id=r[1], current_state=r[2], last_activity=r[3], was_asked=r[4])

    async def update_user_state(self, tg_id: int, current_state: str):
        await self.con.execute(f"update users set current_state='{current_state}' where tg_id='{tg_id}'")
        await self.con.commit()

    async def update_user(self, user: User):
        await self.con.execute(f"update users set current_state='{user.current_state}', \
            last_activity='{user.last_activity}', \
                was_asked={user.was_asked} \
                    where tg_id='{user.tg_id}';")
        await self.con.commit()

    async def add_coupon(self, coupon: Coupon):
        await self.con.execute(f"insert into coupons (tg_id, type, text) values ('{coupon.tg_id}','{coupon.type}', '{coupon.text}')")
        await self.con.commit()

    async def get_coupons_by_id(self, tg_id: int):
        res = await (await self.con.execute(f"select type, text from coupons where tg_id = '{tg_id}'")).fetchall()
        return [Coupon(tg_id=tg_id, type=r[0], text=r[1]) for r in res]

    async def delete_coupon(self, coupon: Coupon):
        await self.con.execute(f"delete from coupons where tg_id='{coupon.tg_id}' and text='{coupon.text}'")
        await self.con.commit()

    async def add_scheduled_message(self, message: ScheduledMessage):
        await self.con.execute(f"insert into scheduled (to_id, time, type) values ('{message.to_id}', '{message.time}', '{message.type}')")
        await self.con.commit()

    async def get_all_scheduled(self):
        res = await (await self.con.execute(f"select * from scheduled")).fetchall()
        return [ScheduledMessage(id=r[0], to_id=r[1], time=r[2], type=r[3]) for r in res]
    
    async def delete_scheduled_messages(self, messages: list[ScheduledMessage]):
        await self.con.execute(f"delete from scheduled where id in ({', '.join([str(mes.id) for mes in messages])})")
        await self.con.commit()
 
    async def get_afk(self):
        res = await (await self.con.execute(f"select * from users where strftime('%s', last_activity) BETWEEN strftime('%s', '2022-01-01 00:00:00.000000') AND strftime('%s', '{datetime.datetime.now() - datetime.timedelta(seconds=60)}') and was_asked={False}")).fetchall()
        return [User(id=r[0], tg_id=r[1], current_state=r[2], last_activity=r[3], was_asked=r[4]) for r in res]

    async def execute(self, command: str):
        await self.con.execute(command)
    
    async def commit(self):
        await self.con.commit()


async def get_db():
    db = DB()
    await db.initialize_db()
    return db

# asyncio.run(get_db())