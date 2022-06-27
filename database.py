# -*- coding: utf-8 -*-

from sqlite3 import connect
from time import strftime


class DataBase: # КЛАСС БАЗЫ ДАННЫХ;
    def __init__(self):
        self.conn = connect('data/data.db')
        self.c = self.conn.cursor()
        self.c.execute(''' CREATE TABLE IF NOT EXISTS data
                       (id integer primary key, status text, number integer, author integer, datetime text) ''')
        self.conn.commit()

    def add_data(self, number, author):
        self.c.execute(''' INSERT INTO data (status, number, author, datetime) VALUES (?, ?, ?, ?) ''',
                       ('✅', number, author, strftime('%d-%m-%Y «%H:%M:%S»')))
        self.conn.commit()

    def __del__(self):
        self.conn.close()