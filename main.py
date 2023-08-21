import sqlite3, os, uuid, qrcode

def database_creation(database_name):
    if os.path.isfile(database_name):
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {database_name.replace('.db', '') + '_inventory'}")
            rows = cursor.fetchall()
            print('File found...')
            print(rows)
    else:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            generate_qr_codes_for_database(database_name)
            
            table_name = database_name.replace('.db', '') + '_inventory'
            
            cursor.execute(f"create table {table_name}(SKU integer, DESCRIPTION text, PRICE integer)")
            connection.commit()
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            print(rows)
            connection.commit()
    
    # This database does need to be hard coded.
    if os.path.isfile('product_information_database.db'):
        pass
    elif os.path.isfile('product_information_database.db') == False:
        with sqlite3.connect('product_information_database.db') as connection:
            cursor = connection.cursor()
            generate_qr_codes_for_database('product_information_database.db')
            cursor.execute("create table product_info(SKU integer, DESCRIPTION text, PRICE integer)")
            data = [
                (10034, 'Gaming key binds', 10),
                (40456, 'Mousepad', 5),
                (68896, 'Headset', 15),
            ]
            cursor.executemany('INSERT INTO product_info VALUES(?,?,?)', data)
            connection.commit()

            cursor.execute("SELECT * FROM product_info")
            rows = cursor.fetchall()

            print(rows)
            connection.commit()

def generate_random_uuid():
    # This is used for identifying, product, totes and stockroom inventory.
    return uuid.uuid4().hex

def generate_qr_codes_for_database(databasename):
    img = qrcode.make(databasename)
    img.save(databasename.replace('.db', '') + '.png')

def generate_qr_codes_for_sku(sku, unique_name):
    print()

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

def show_scan_results_for_item(table_name=None, database_file_name=None, sku=None):
    # Show what's inside a database or get information about a product
    # I foresee this code having some bugs that we'll need to debug...
    if database_file_name != None:
        # This gets all items within a database
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
    elif sku != None:
        # This gets product information
        # !!!! Once you print out QR tags for skus, then implement this code... !!!!
        with sqlite3.connect('product_information_database.db') as connection:
            try:
                cursor = connection.cursor()
                # How can I also print out the description of this sku (product)
                sku_data = cursor.execute(f"SELECT {sku}, DESCRIPTION, PRICE from product_info")
                return sku_data.fetchone()
            except sqlite3.OperationalError:
                print('Oops something went wrong')

sku_tag_data = show_scan_results_for_item(sku=40456)
generate_qr_codes_for_sku(sku=sku_tag_data[0], descritpion=sku_tag_data[1], price=sku_tag_data[2])


# Creating a whole new database and hard coding the data
#database_creation('testing_database.db')

# Code for running show_scan_results_for_item()
# data = input('enter qr code: ')
# list_1 = data.split(" ")
# print(list_1[0])
# try:
#     show_scan_results_for_item(list_1[0], list_1[1])
# except IndexError:
#     show_scan_results_for_item(database_file_name=list_1[0])


#print('Create a new table')
#create_new_item_group(database_file_name='sales_floor_database.db', table_name='testing')