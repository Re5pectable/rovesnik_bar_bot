import sqlite3
from unittest.mock import Base
from pydantic import BaseModel
import datetime
from typing import Union

class User(BaseModel):
    id: int = None
    tg_id: int
    current_state: str = "hanging"

class Order(BaseModel):
    id: int = None
    made_by_user: int = None
    name: str = None
    n_guests: int = None
    phone: str = None
    date: str = None
    day_type: str = None
    weekday: int = None
    time: str = None
    deposit: int = None
    confirmed: bool = False
    deposit_sent: bool = False
    created: datetime.datetime = None

class Event(BaseModel):
    id: int = None
    date: str
    time: str
    title: str
    event_type: str

class DB:
    def __init__(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("create table if not exists users (id integer primary key autoincrement, tg_id int, current_state varchar(16));")
            c.execute("create table if not exists orders (id integer primary key autoincrement, made_by_id int, name varchar(32), n_guests int, phone varchar(16), date datetime, time datetime, deposit tinyint(1), confirmed tinyint(1));")
            c.execute("create table if not exists events (id integer primary key autoincrement, date datetime, time datetime, title text, event_type varchar(16));")    

    def recreate_table_orders(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("drop table if exists orders")
            c.execute("create table orders (id integer primary key autoincrement, made_by_id int, name varchar(32), n_guests int, phone varchar(16), date datetime, time datetime, deposit tinyint(1), confirmed tinyint(1));")

    def recreate_table_users(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("drop table if exists users")
            c.execute("create table users (id integer primary key autoincrement, tg_id int, current_state varchar(16));")

    def recreate_table_events(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("drop table if exists events")
            c.execute("create table events (id integer primary key autoincrement, date datetime, time datetime, title text, event_type varchar(16));")            

    def add_user(self, tg_id: int, current_state: str = "hanging"):
        with sqlite3.connect("database.sqlite") as c:
            c.execute(f"insert into users (tg_id, current_state) values ('{tg_id}', '{current_state}')")

    def get_user(self, tg_id: int):
        with sqlite3.connect("database.sqlite") as c:
            r = c.execute(f"select * from users where tg_id = '{tg_id}'").fetchone()
            if r:
                return User(id=r[0], tg_id=r[1], current_state=r[2])

    def update_user_state(self, tg_id: int, current_state: str):
        with sqlite3.connect("database.sqlite") as c:
            c.execute(f"update users set current_state='{current_state}' where tg_id='{tg_id}'")

    def add_order(self, tg_id: int, name: str = None):
        with sqlite3.connect("database.sqlite") as c:
            if name:    
                c.execute(f"insert into orders (made_by_id, name) values ('{tg_id}', '{name}')")
            else:
                c.execute(f"insert into orders (made_by_id) values ('{tg_id}')")

    def update_order(self, made_by_user: int, param_name: str, value):
        with sqlite3.connect("database.sqlite") as c:
            c.execute(f"update orders set '{param_name}'='{value}' where made_by_id='{made_by_user}'")

    def get_orders_by_user_id(self, user_id: int):
        with sqlite3.connect("database.sqlite") as c:
            r = c.execute(f"SELECT * FROM orders where made_by_id = '{user_id}' ORDER BY id DESC").fetchall()
            return r

    def add_event(self, event: Event):
        with sqlite3.connect("database.sqlite") as c:
            c.execute(f"insert into events (date, time, title, event_type) values ('{event.date}', '{event.time}', '{event.title}', '{event.event_type}')")

    def get_events_by_date(self, date: str):
        with sqlite3.connect("database.sqlite") as c:
            res = c.execute(f"select * from events where date='{date}'").fetchall()
            return [Event(id=r[0], date=r[1], time=r[2], title=r[3], event_type=r[4]) for r in res]

    def execute(self, command: str):
        with sqlite3.connect("database.sqlite") as c:
            return c.execute(command).fetchall()

db = DB()
