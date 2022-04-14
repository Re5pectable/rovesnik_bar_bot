import sqlite3
from unittest.mock import Base
from pydantic import BaseModel
import datetime

class User(BaseModel):
    id: int
    tg_id: int
    current_state: str

class Order(BaseModel):
    id: int
    made_by_user: int
    name: str
    n_guests: int
    phone: str
    date: datetime.datetime
    time: datetime.datetime
    deposit: bool
    confirmed: bool

class DB:
    def __init__(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("create table if not exists users (id integer primary key autoincrement, tg_id int, current_state varchar(16));")
            c.execute("create table if not exists orders (id integer primary key autoincrement, made_by_id int, name varchar(32), n_guests int, phone varchar(16), date datetime, time datetime, deposit tinyint(1), confirmed tinyint(1));")

    def recreate_table_orders(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("drop table if exists orders")
            c.execute("create table orders (id integer primary key autoincrement, made_by_id int, name varchar(32), n_guests int, phone varchar(16), date datetime, time datetime, deposit tinyint(1), confirmed tinyint(1));")
    def recreate_table_users(self):
        with sqlite3.connect("database.sqlite") as c:
            c.execute("drop table if exists users")
            c.execute("create table users (id integer primary key autoincrement, tg_id int, current_state varchar(16));")

    def add_user(self, tg_id, state='hanging'):
        with sqlite3.connect("database.sqlite") as c:
            c.execute(f"insert into users (tg_id, current_state) values ('{tg_id}', '{state}')")

    def get_user(self, tg_id):
        with sqlite3.connect("database.sqlite") as c:
            r = c.execute(f"select * from users where tg_id = '{tg_id}'").fetchone()
            if r:
                return User(id=r[0], tg_id=r[1], current_state=r[2])

    def get_orders_by_user_id(self, user_id):
        with sqlite3.connect("database.sqlite") as c:
            r = c.execute("SELECT * FROM orders where made_by_user = '{user_id}' ORDER BY id DESC").fetchall()
            return r

    def update_user_state(self, user_id, state):
        with sqlite3.connect("database.sqlite") as c:
            c.execute(f"update users set current_state='{state}' where tg_id='{user_id}'")

db = DB()