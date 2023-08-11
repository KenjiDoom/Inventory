import sqlite3

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

database_creation()