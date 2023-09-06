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
        with sqlite3.connect(database_name + '.db') as connection:
            cursor = connection.cursor()
            table_name = database_name.replace('.db', '') + '_inventory'
            generate_qr_codes_for_database(database_name, table_name)
            cursor.execute(f"create table {table_name}(SKU integer, DESCRIPTION text, PRICE integer, UNIQUE_CODE integer)")
            connection.commit()
    
    if os.path.isfile('product_information_database.db'):
        pass
    elif os.path.isfile('product_information_database.db') == False:
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

def generate_random_uuid():
    # This is used for identifying, product, totes and stockroom inventory.
    data = str(uuid.uuid4().int)
    return data[0:10]

def generate_qr_codes_for_database(database, table_name):
    # This needs to contain the table name and database file name
    img = qrcode.make(database + ' ' + table_name)
    img.save(database.replace('.db', '') + '.png')

def generate_qr_codes_for_sku(sku, table_name, database_file_name, unique_code):
    img = qrcode.make(str(sku) + ' ' + str(table_name) + ' ' + database_file_name + ' ' + str(unique_code))
    img.save(str(sku) + '.png')

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

def show_scan_results_for_item(table_name=None, database_file_name=None, sku=None, unique_code=None):
    # Show what's inside a database or get information about a product
    if database_file_name and table_name != None:
        with sqlite3.connect(database_file_name) as connection:
            try:
                print(f'Displaying all items within this database {database_file_name}')
                cursor = connection.cursor()
                all_data = cursor.execute(f"SELECT * from {table_name}")
                print(all_data.fetchall())
            except sqlite3.OperationalError:
                print('Nothing was found')
    
    elif sku != None:
        # Used for grabbing information on a product.
        with sqlite3.connect('product_information_database.db') as connection:
            cursor = connection.cursor()
            sku_data = cursor.execute(f"SELECT {sku}, DESCRIPTION, PRICE from product_info")
            return sku_data.fetchone()
    
    elif unique_code != None:
        # Look through all the databases within a directory for a specific item.
        for database in os.listdir():
            if database.endswith('.db'):
                with sqlite3.connect(database) as connection:
                    cursor = connection.cursor()
                    table_names = cursor.execute("""select name from sqlite_master where type='table';""")
                    results = table_names.fetchall()
                    for table in results:
                        table_name = table[0]
                        with sqlite3.connect(database) as connection:
                            cursor = connection.cursor()
                            data = cursor.execute(f"""select {unique_code}, sku from {table_name}""")
                            data = data.fetchone()
                            if data == None:
                                pass
                            elif data != None:
                                # This is now broken for our generate_qr_codes_for_sku() function....
                                return data[1], data[2], data[0], data[3], table_name, database

def copy_item_to_inventory_database(unique_code=None, sku=None, destination_filename=None, destination_table_name=None):
    # Copy item into a database
    sku_data = show_scan_results_for_item(unique_code=unique_code)
    # To-Fix: Creation of a NONE database when destination_filename equals None
    # To-do: Exception handling when a user enter's an item instead of a inventory location.
    
    if destination_filename == None:
        pass
    elif destination_filename != None:
        struct_data = [
            (sku_data[0], sku_data[1], sku_data[3], unique_code)
        ]
        try:
            with sqlite3.connect(str(destination_filename)) as connection:
                cursor = connection.cursor()
                cursor.executemany(f"INSERT INTO {destination_table_name} VALUES (?, ?, ?, ?)", struct_data)
                connection.commit()
        except sqlite3.OperationalError as e:
            print('Not an inventory database!!')


# item_to_scan = input("Scan the product qr code: ")
# database_to_scan = input('Scan the inventory qr tag: ')
# value = database_to_scan.find(' ')
# copy_item_to_inventory_database(unique_code=str(item_to_scan[51:]), sku=item_to_scan[0], destination_filename=database_to_scan[0:value] + '.db', destination_table_name=database_to_scan[value:].replace(' ', ''))

# Create database files
#database_creation('Testing_database')

data = show_scan_results_for_item(unique_code=3236630686)
print(data)
generate_qr_codes_for_sku(sku=data[3], table_name=data[1], database_file_name=data[2], unique_code=data[0])


#Code for running show_scan_results_for_item()
# data = input('enter qr code: ')
# list_1 = data.split(" ")
# print(list_1[0])
# try:
#     show_scan_results_for_item(list_1[0], list_1[1])
# except IndexError:
#     show_scan_results_for_item(database_file_name=list_1[0])


#print('Create a new table')
#create_new_item_group(database_file_name='sales_floor_database.db', table_name='testing')
