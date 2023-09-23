# Creates users for login page.
import sqlite3, os
from main import * 

def create_user_data():
    with sqlite3.connect('user-data.db') as connection:
        cursor = connection.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS users(storeID INTEGER, username TEXT, password TEXT)""")
        data = [
            (800, 'kenjidoom', 'password')
        ]
        cursor.execute("INSERT INTO users VALUES(?, ?, ?)", data[0])
        connection.commit()

def create_product_data():
    with sqlite3.connect('product_information_database.db') as connection:
        cursor = connection.cursor()
        generate_qr_codes_for_database('product_information_database.db', 'product_info')
        cursor.execute("create table product_info(SKU integer, DESCRIPTION text, PRICE integer, UNIQUE_CODE integer)")
        data = [
            (10034, 'Gaming key binds', 10, 3236630686),
            (40456, 'Mousepad', 5, 2761298854),
            (68896, 'Headset', 15, 5609943232),
        ]
        cursor.executemany('INSERT INTO product_info VALUES(?,?,?,?)', data)
        connection.commit()
        cursor.execute("SELECT * FROM product_info")
        rows = cursor.fetchall()
        print(rows)
        connection.commit()
        
print('1. Create product information database')
print('2. Create users for website..')

user_option = input('Enter 1/2: ')

if user_option == '1':
    create_product_data()
elif user_option == '2':
    create_user_data()