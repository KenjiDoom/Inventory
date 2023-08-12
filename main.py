import sqlite3, os

def database_creation():
    # Checking for stockroom database file [ This represents the stockroom ]
    if os.path.isfile('stockroom-database.db'):
        with sqlite3.connect("stockroom-database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM inventory")
            rows = cursor.fetchall()
            print('Pre-existing file found...')
            print(rows)
    else:
        with sqlite3.connect('stockroom-database.db') as connection:
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
    
    # Checking for the sales floor database file. [ This represents the sales floor ]
    if os.path.isfile('sales_floor_database.db'):
        with sqlite3.connect('sales_floor_database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM sales_inventory')
            rows = cursor.fetchall()
            print('File exist...')
            print(rows)
    else:
        # Should make an empty database
        with sqlite3.connect('stockroom-database.db') as connection:
            cursor = connection.cursor()
            cursor.execute("create table sales_inventory(SKU integer, DESCRIPTION text, PRICE integer)")
            connection.commit()
            
            cursor.execute("SELECT * FROM sales_inventory")
            rows = cursor.fetchall()
            
            print(rows)
            connection.commit()

database_creation()