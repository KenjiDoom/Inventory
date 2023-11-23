# Creates users for login page.
import sqlite3, os
import json
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
        try:
            cursor.execute("create table product_info(SKU integer, DESCRIPTION text, PRICE integer, UNIQUE_CODE integer, CAPACITY integer, LOCATION string)")
            data = [
                (10034, 'Gaming key binds', 10, 3236630686, 7, 'Asile 3, Section 3, Peg #10'),
                (40456, 'Mousepad', 5, 2761298854, 10, 'Asile 2, Section 1, Peg #2'),
                (68896, 'Headset', 15, 5609943232, 4, 'Asile 1, Section 2, Peg #3'),
            ]

            cursor.executemany('INSERT INTO product_info VALUES(?,?,?,?,?,?)', data)
            connection.commit()
            cursor.execute("SELECT * FROM product_info")
            rows = cursor.fetchall()
            print(rows)
            connection.commit()
        except sqlite3.OperationalError:
            print('File already exists...')

def create_image_file_location():
    dictionary = {
        '10034': 'static/images/key-switches.jpg',
        '40456': 'static/image/mouse_pad.jpg'
    }
    
    json_object = json.dumps(dictionary, indent=4)

    with open('Sku_image_locations.json', 'w') as output_file:
        output_file.write(json_object)

        
print('1. Create product information database')
print('2. Create users for website..')
print('3. Create Image file location json file..')

user_option = input('Enter 1/2: ')

if user_option == '1':
    create_product_data()
elif user_option == '2':
    create_user_data()
elif user_option == '3':
    create_image_file_location()
