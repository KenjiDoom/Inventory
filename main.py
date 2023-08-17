import sqlite3, os, uuid, qrcode

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
            generate_qr_codes_for_database('stockroom-database.db')
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
            # Generate qr codes for 
            generate_qr_codes_for_database('sales_floor_database.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM sales_inventory')
            rows = cursor.fetchall()
            print('File exist...')
            print(rows)
    else:
        # Should make an empty database
        with sqlite3.connect('sales_floor_database.db') as connection:
            generate_qr_codes_for_database('sales_floor_database.db')
            cursor = connection.cursor()
            try:
                cursor.execute("create table sales_inventory(SKU integer, DESCRIPTION text, PRICE integer)")
                connection.commit()
            
                cursor.execute("SELECT * FROM sales_inventory")
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                pass
            print(rows)
            connection.commit()

def generate_random_uuid():
    # This is used for idetenifying, product, totes and stockroom inventory.
    return uuid.uuid4().hex

def generate_qr_codes_for_database(table_name):
    img = qrcode.make(table_name)
    img.save(table_name.replace('.db', '') + '.png')

def create_new_table(database_name):
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("create table tote(SKU integer, DESCRIPTION text, PRICE integer)")
            connection.commit()
    except sqlite3.OperationalError:
        print('tote already exist...')

def create_qr_items():
    with sqlite3.connect('stockroom-database.db') as connection:    
        cursor = connection.cursor()
        data = cursor.execute("SELECT name FROM sqlite_schema")
        for table_name in cursor:
            database_retriveal = cursor.execute("PRAGMA database_list;")
            database_name = database_retriveal.fetchall()
            print(str(table_name[0]))
            img = qrcode.make(table_name[0] + ' ' +  database_name[0][2])
            img.save(str(table_name[0]) + '.png')

move_data_to_new_table('stockroom-database.db')
