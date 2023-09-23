# Creates users for login page.

import sqlite3

with sqlite3.connect('user-data.db') as connection:
    cursor = connection.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS users(storeID INTEGER, username TEXT, password TEXT)""")
    data = [
        (800, 'kenjidoom', 'password')
    ]
    cursor.execute("INSERT INTO users VALUES(?, ?, ?)", data[0])
    connection.commit()