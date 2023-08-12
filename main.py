import sqlite3, os

def check_database_existence():
    if os.path.isfile('Inven-database.db'):
        with sqlite3.connect('Inven-database.db') as connection:
            print('Displaying database information')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM inventory')
            rows = cursor.fetchall()
            print(rows)
    else:
        database_creation()

def database_creation():
    print('Generating database...')
    with sqlite3.connect('Inven-database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("create table inventory(SKU integer, DESCRIPTION text, PRICE integer)")
        data = [
            (10034, 'Gaming key binds', 10)
        ]
        cursor.executemany('INSERT INTO inventory VALUES(?,?,?)', data)
        connection.commit()

        # Querying database
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        print(rows)
        
        connection.commit()

check_database_existence()