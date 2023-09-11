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
        try:
            with sqlite3.connect(database_name + '.db') as connection:
                cursor = connection.cursor()
                table_name = database_name.replace('.db', '') + '_inventory'
                generate_qr_codes_for_database(database_name + '.db', table_name)
                cursor.execute(f"create table {table_name}(SKU integer, DESCRIPTION text, PRICE integer, UNIQUE_CODE integer)")
                connection.commit()
        except sqlite3.OperationalError:
            print('That file already exist...')
    
    # This code below will eventually need its own file.
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

def update_all_qr_tags():
    print('Updating all qr tags with update-to-date locations and information')
    for database in os.listdir():
        if database.endswith('.db'):
            with sqlite3.connect(database) as connection:
                cursor = connection.cursor()
                table_names = cursor.execute("""select name from sqlite_master where type='table';""")
                results = table_names.fetchall()
                for tables in results:
                    generate_qr_codes_for_database(str(database), str(tables[0]))
                    items = cursor.execute(f""" SELECT * from {tables[0]}""")
                    sku_data = items.fetchall()
                    for sku in sku_data:
                        print(str(sku[0]) + ' ' + str(sku[3]) + ' ' + str(tables[0]) + ' ' + str(database))
                        generate_qr_codes_for_sku(sku[0], sku[3], str(tables[0]), str(database))

def generate_random_uuid():
    # This is used for identifying, product, totes and stockroom inventory.
    data = str(uuid.uuid4().int)
    return data[0:10]

def generate_qr_codes_for_database(database, table_name):
    # This needs to contain the table name and database file name
    img = qrcode.make(database + ' ' + table_name)
    img.save(database.replace('.db', '') + '_' + table_name + '.png')

def generate_qr_codes_for_sku(sku, unique_code, table_name, database_file_name):
    img = qrcode.make(str(sku) + ' ' + str(table_name) + ' ' + database_file_name + ' ' + str(unique_code))
    img.save(str(sku) + '_' + str(unique_code) + '.png')

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
    # Show's all the items within a database. (Inventory database)
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
        # Provides detailed information about a sku number (item/product)
        with sqlite3.connect('product_information_database.db') as connection:
            cursor = connection.cursor()
            sku_data = cursor.execute(f"SELECT {sku}, DESCRIPTION, PRICE from product_info")
            return sku_data.fetchone()
    
    elif unique_code != None:
        # Locate an item through all database files
        try:
            database = os.listdir() 
            database.remove('product_information_database.db')
            for database_name in database:
                if database_name.endswith('.db'):
                    with sqlite3.connect(database_name) as connection:
                        cursor = connection.cursor()
                        table_names = cursor.execute("""select name from sqlite_master where type='table';""")
                        results = table_names.fetchall()
                        for table in results:
                            table_name = table[0]
                            with sqlite3.connect(database_name) as connection:
                                cursor = connection.cursor()
                                data = cursor.execute(f"""select {unique_code}, sku, description, price from {table_name} WHERE UNIQUE_CODE={unique_code}""")
                                data = data.fetchone()
                                if data == None:
                                    pass
                                elif data != None:
                                    return data[1], data[2], data[3], data[0], table_name, database_name
        except sqlite3.OperationalError:
            print('!! Error must have scanned an inventory qr tag instead of a item. !!')

def copy_item_to_inventory_database(unique_code=None, sku=None, destination_filename=None, destination_table_name=None):
    # Copy an item into a database
    sku_data = show_scan_results_for_item(unique_code=unique_code)
    try:
        if sku_data[0] != None:
            if destination_filename == None:
                pass
            elif destination_filename != None:
                if os.path.exists(destination_filename) == True:
                    try:
                        struct_data = [
                            (sku_data[0], sku_data[1], sku_data[2], unique_code)
                        ]
                        with sqlite3.connect(str(destination_filename)) as connection:
                            cursor = connection.cursor()
                            cursor.executemany(f"INSERT INTO {destination_table_name} VALUES (?, ?, ?, ?)", struct_data)
                            connection.commit()
                            # Delete data once it's been copied into the new database.
                            delete_items_from_database(unique_code=unique_code, new_destination_filename=str(destination_filename), new_destination_table_name=str(destination_table_name))
                    except sqlite3.OperationalError as e:
                        print('Error scanned an item into an item.')
                        print(e)
                    except IndexError:
                        print('!! Error nothing was scanned. !!')
                else:
                    print(destination_filename + ' not found...')
        else:
            pass
    except TypeError:
        print('Item not found...')

def delete_items_from_database(unique_code=None, new_destination_filename=None, new_destination_table_name=None):
    # Deletes items from a database
    try:
        item_location_information = show_scan_results_for_item(unique_code=unique_code)  
        
        file_data = [
            item_location_information[5], item_location_information[4], new_destination_filename, new_destination_table_name
        ]
        print(file_data[0])
        with sqlite3.connect(str(file_data[0])) as connection:
            cursor = connection.cursor()
            cursor.execute(f"""DELETE from {file_data[1]} where unique_code={unique_code}""")
            print('Deleted.....')
            connection.commit()
    
    except NameError:
        print('The item is already deleted.')
    except TypeError:
        print('The item is already deleted.')

def unique_code_modification_and_transfer(sku_number=None, destination_filename=None, destination_table_name=None):
    # Used for moving orginal data into new inventory locations, with new unique codes. Creating new items and moving them into new inventory locatiins.
    # Also useful for when all items for a specific sku have been deleted.
    with sqlite3.connect('product_information_database.db') as connection:
        cursor = connection.cursor()
        cursor = cursor.execute(f"SELECT {sku_number}, DESCRIPTION, PRICE from product_info")
        sku_data = cursor.fetchone()
        new_modified_data = [
            (sku_data[0], sku_data[1], sku_data[2], generate_random_uuid())
        ]
        with sqlite3.connect(str(destination_filename)) as connection:
            cursor = connection.cursor()
            cursor.executemany(f'INSERT INTO {destination_table_name} VALUES (?, ?, ?, ?)', new_modified_data)
            connection.commit()
        print('Done..')

update_all_qr_tags()

# Create new items incase all have been deleted.
# sku = input('Scan or enter sku number: ')
# database_location = input('Scan the inventory qr tag: ')
# value = database_location.find(' ')
# unique_code_modification_and_transfer(sku_number=sku[0:5], destination_filename=database_location[0:value], destination_table_name=database_location[value:])

# Deleting an item - to be used for register by people.
# item_to_scan = input("Scan the product qr code you want to delete: ")
# delete_items_from_database(unique_code=str(item_to_scan[51:]), sku=item_to_scan[0])

# Code for copying items into a database
# try:
#     item_to_scan = input("Scan the product qr code: ")
#     database_to_scan = input('Scan the inventory qr tag: ')
#     value = database_to_scan.find(' ')
#     copy_item_to_inventory_database(unique_code=str(item_to_scan[51:]), sku=item_to_scan[0:5], destination_filename=database_to_scan[0:value], destination_table_name=database_to_scan[value:].replace(' ', ''))
# except IndexError:
#     print('!! Error nothing was scanned. !!')

# Code for creating database files
#database_creation('BRANDNEWDATABASE')

# Code for creating qr codes for items
#data = show_scan_results_for_item(unique_code=5609943232)
#generate_qr_codes_for_sku(sku=data[0], table_name=data[4], database_file_name=data[5], unique_code=data[3])

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
