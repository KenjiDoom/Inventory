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
    # unique codes need to come after sku numbers to have a fixed index number.
    # WORKING ON THIS RIGHT NOW
    img = qrcode.make(str(sku) + ' ' + str(unique_code) + ' ' + str(table_name) + ' ' + database_file_name)
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

def show_scan_results_for_item(table_name=None, database_file_name=None, SKU=None, unique_code=None):
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
    
    elif SKU != None:
        try:
            # Provides detailed information about a sku number (item/product)
            with sqlite3.connect('product_information_database.db') as connection:
                cursor = connection.cursor()
                sku_data = cursor.execute(f"SELECT {SKU}, DESCRIPTION, PRICE from product_info where sku={SKU}")
                return sku_data.fetchone()
        except sqlite3.OperationalError:
            return SKU + ' not found'
    
    elif unique_code != None:
        # Locate an item through all database files
        try:
            database = os.listdir() 
            database.remove('product_information_database.db')
            for database_name in database:
                if database_name.endswith('.db'):
                    # Why is this code returning a NONE? 
                    with sqlite3.connect(database_name) as connection:
                        cursor = connection.cursor()
                        table_names = cursor.execute("""select name from sqlite_master where type='table';""")
                        results = table_names.fetchall()
                        for table in results:
                            table_name = table[0]
                            with sqlite3.connect(database_name) as connection:
                                cursor = connection.cursor()
                                data = cursor.execute(f"""select {unique_code}, sku, description, price from {table_name} WHERE UNIQUE_CODE={unique_code}""")
                                data = data.fetchall()
                                value = len(data)
                                if data == None or len(data) == 0:
                                    pass
                                elif data != None:
                                    for i in range(value):
                                        return data[i][1], data[i][2], data[i][3], data[i][0], table_name, database_name
        except sqlite3.OperationalError:
            print('!! Error must have scanned an inventory qr tag instead of a item. !!')

def copy_item_to_inventory_database(unique_code=None, destination_filename=None, destination_table_name=None):
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
                            (sku_data[0], sku_data[1], sku_data[2], unique_code),
                            (sku_data[0], sku_data[1], sku_data[2], unique_code, sku_data[4], sku_data[5], destination_filename, destination_table_name),
                        ]
                        with sqlite3.connect(str(destination_filename)) as connection:
                            cursor = connection.cursor()
                            sql_command = f"INSERT INTO {destination_table_name} VALUES (:col1, :col2, :col3, :col4)"
                            cursor.execute(sql_command, {'col1': struct_data[0][0], 'col2': struct_data[0][1], 'col3': struct_data[0][2], 'col4': struct_data[0][3]})
                            connection.commit()
                            delete_items_from_database(unique_code=unique_code, item_and_destination_data=struct_data[1])
                    except sqlite3.OperationalError as e:
                        print('Error scanned an item into an item.')
                        print(e)
                    except IndexError as e:
                        print('!! Error nothing was scanned. !!')
                        print(e)
                else:
                    print(destination_filename + ' not found...')
        else:
            pass
    except TypeError as e:
        print('Error item not found...' + str(e))

def delete_items_from_database(unique_code=None, item_and_destination_data=None):
    if item_and_destination_data != None:
        print(item_and_destination_data)
        with sqlite3.connect(str(item_and_destination_data[5])) as connection:
            cursor = connection.cursor()
            cursor.execute(f"""DELETE from {str(item_and_destination_data[4])} where unique_code={str(unique_code)}""")
            print('Deleted.....')
            connection.commit()
    
    elif item_and_destination_data == None:
        item_data = show_scan_results_for_item(unique_code=unique_code)
        try:
            with sqlite3.connect(str(item_data[5])) as connection:
                cursor = connection.cursor()
                cursor.execute(f"""DELETE from {str(item_data[4])} where unique_code={str(unique_code)}""")
                print('Deleted.....')
                connection.commit()
        except TypeError as e:
            print('Item not found ' + str(e))

def unique_code_modification_and_transfer(sku_number=None, destination_filename=None, destination_table_name=None):
    # Used for moving orginal data into new inventory locations, with new unique codes. Creating new items and moving them into new inventory locatiins.
    # Also useful for when all items for a specific sku have been deleted.
    with sqlite3.connect('product_information_database.db') as connection:
        cursor = connection.cursor()
        cursor = cursor.execute(f"SELECT {sku_number}, DESCRIPTION, PRICE from product_info WHERE sku={sku_number}")
        sku_data = cursor.fetchone()
        new_modified_data = [
            (sku_data[0], sku_data[1], sku_data[2], generate_random_uuid())
        ]
        with sqlite3.connect(str(destination_filename)) as connection:
            cursor = connection.cursor()
            cursor.executemany(f'INSERT INTO {destination_table_name} VALUES (?, ?, ?, ?)', new_modified_data)
            connection.commit()
        print('Done..')

def total_amount_sku(sku_number=None):
    total_amount = []
    database = os.listdir()
    database.remove('product_information_database.db')
    for database_name in database:
        if database_name.endswith('.db'):
            with sqlite3.connect(database_name) as connection:
                cursor = connection.cursor()
                table_names = cursor.execute(""" select name from sqlite_master where type='table';""")
                results = table_names.fetchall()
                for table in results:
                    table_name = table[0]
                    with sqlite3.connect(database_name) as connection:
                        cursor = connection.cursor()
                        data = cursor.execute(f"""select {sku_number} from {table_name}""")
                        data = data.fetchall()
                        if data == None or len(data) == 0:
                            pass
                        else:
                            total_amount.append(data)
    print('We have a total of ' + str(len(total_amount)))