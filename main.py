import sqlite3, os, uuid, qrcode

def database_creation():
    # Note: We cane make these functions more dynamic by using an argument for the database_name instead of hard typing everything out.
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
    # This is used for identifying, product, totes and stockroom inventory.
    return uuid.uuid4().hex

def generate_qr_codes_for_database(table_name):
    img = qrcode.make(table_name)
    img.save(table_name.replace('.db', '') + '.png')

def create_new_item_group(database_file_name, table_name):
    # This function is used for creating a new item group. AKA: creating a new table within a database.
    # database representing what area of the store you're inserting this item group into. i.e., stockroom or sales floor.
    try:
        with sqlite3.connect(database_file_name) as connection:
            cursor = connection.cursor()
            # Table name is the new database name you want to create
            cursor.execute(f"create table {table_name}(SKU integer, DESCRIPTION text, PRICE integer)")
            connection.commit()
    except sqlite3.OperationalError:
        print(f'"{table_name}" already exist...')

def show_scan_results_for_item(table_name=None, database_file_name=None):
    # Show what's inside a database or get description information about a product
    if database_file_name != None:
        with sqlite3.connect(database_file_name) as connection:
            try:
                cursor = connection.cursor()
                all_data = cursor.execute(f"SELECT * from {table_name}")
                print(all_data.fetchall())
            except sqlite3.OperationalError:
                if table_name == None:
                    print('This file does not contain any databases')
                elif table_name != None:
                    print(f'{table_name} was not found...')

    else:   
        print('No database was sepcifeid')

data = input('enter qr code: ')
list_1 = data.split(" ")
print(list_1[0])
try:
    show_scan_results_for_item(list_1[0], list_1[1])
except IndexError:
    show_scan_results_for_item(database_file_name=list_1[0])


#print('Create a new table')
#create_new_item_group(database_file_name='sales_floor_database.db', table_name='testing')