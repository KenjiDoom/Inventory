import sqlite3, os

def database_creation():
    if os.path.isfile('Inven-database.db'):
        with sqlite3.connect("Inven-database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM inventory")
            rows = cursor.fetchall()
            print('Pre-existing file found...')
            print(rows)
    else:
        with sqlite3.connect('Inven-database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("create table inventory(SKU integer, DESCRIPTION text, PRICE integer)")
            data = [
                (10034, 'Gaming key binds', 10)
            ]
            cursor.executemany('INSERT INTO inventory VALUES(?,?,?)', data)
            connection.commit()

            cursor.execute("SELECT * FROM inventory")
            rows = cursor.fetchall()
            print(rows)

            connection.commit()


database_creation()