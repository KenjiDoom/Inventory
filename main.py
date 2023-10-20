import sqlite3, os, uuid, qrcode
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

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
    try:
        exclude_db_names = ['user-data.db']
        database_name = os.listdir() 
        for ex_db in exclude_db_names:
            try:
                database_name.remove(ex_db)
            except ValueError:
                pass
        for database in database_name:
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
    except sqlite3.OperationalError:
        pass

def generate_random_uuid():
    # This is used for identifying, product, totes and stockroom inventory.
    data = str(uuid.uuid4().int)
    return data[0:10]

def generate_qr_codes_for_database(database, table_name):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=10,
    )
    qr.add_data(database + ' ' + table_name)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    draw = ImageDraw.Draw(qr_img)
    
    text = str(table_name)
    font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    img_width, img_height = qr_img.size
    text_x = (img_width - text_width) // 2
    text_y = img_height - text_height - 10 
    
    font_size = 15
    font = ImageFont.truetype("DejaVuSans.ttf", size=font_size) 
    
    draw.text((text_x, text_y), text, fill="black", font=font)

    qr_img.save(database.replace('.db', '') + '_' + table_name + '.png')

def generate_qr_codes_for_sku(sku, unique_code, table_name, database_file_name):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=10,
    )
    qr.add_data(str(sku) + ' ' + str(unique_code) + ' ' + str(table_name) + ' ' + database_file_name)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    draw = ImageDraw.Draw(qr_img)
    
    text = str(sku)
    font = ImageFont.truetype("DejaVuSans.ttf", size=30)
    
    img_width, img_height = qr_img.size
    text_x = (img_width - 90) // 2
    text_y = img_height - 40

    draw.text((text_x, text_y), text, fill="black", font=font)

    qr_img.save(str(sku) + '_' + str(unique_code) + '.png')

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
    items = []
    if database_file_name and table_name != None:
        with sqlite3.connect(database_file_name) as connection:
            try:
                print(f'Displaying all items within this database {database_file_name}')
                cursor = connection.cursor()
                all_data = cursor.execute(f"SELECT * from {table_name}")
                items.append(all_data.fetchall())
            except sqlite3.OperationalError:
                print('Nothing was found')

        return items
    
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
            exclude_db_names = ['product_information_database.db', 'user-data.db']
            database = os.listdir() 
            for ex_db in exclude_db_names:
                try:
                    database.remove(ex_db)
                except ValueError:
                    pass                
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
                                data = cursor.execute(f"""select {unique_code}, SKU, DESCRIPTION, PRICE from {table_name} WHERE UNIQUE_CODE={unique_code}""")
                                data = data.fetchall()
                                value = len(data)
                                if data == None or len(data) == 0:
                                    pass
                                elif data != None:
                                    for i in range(value):
                                        return data[i][1], data[i][2], data[i][3], data[i][0], table_name, database_name
        except sqlite3.OperationalError as e:
            print(e)
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
                            return 'deleted'
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

def total_amount_sku(sku_number=None, database_file_name=None, table_name=None, sku=None):
    if sku_number != None:
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
        print(total_amount)
        print('Total of ' + str(len(total_amount)))
        return len(total_amount)
    elif database_file_name and table_name != None:
        with sqlite3.connect(database_file_name) as connection:
            cursor = connection.cursor()
            all_data = cursor.execute(f"SELECT {sku} from {table_name} where sku={sku}")
        return len(all_data.fetchall())

def total_amount_warehouse():
    # This will count all the total items within a warehouse
    # 1. Get current data to label report 
    # 2. Get the total amount of items in the entire warehouse        #SKU    #LEFT
    # 3. Get the total amount per sku, and put them into a dictionary {10045: 20} 
    # 4. Save the results to a database or json? 
    # 5. Compare last report data to <-> resent report data
    #                   yesterday - today = present amount required 
    current_date = datetime.now()
    print("Repot gen date : " + str(current_date))
    total_amount_per_database = []
    big_sku_list = []
    
    database = os.listdir()
    database.remove('product_information_database.db')
    database.remove('user-data.db')
    
    for database_name in database:
        if database_name.endswith('.db'):
            with sqlite3.connect('product_information_database.db') as connection:
                    cursor = connection.cursor()
                    skus = cursor.execute(""" SELECT SKU FROM product_info """)
                    skus = skus.fetchall()

            with sqlite3.connect(database_name) as connection:
                cursor = connection.cursor()
                table_name = cursor.execute(""" select name from sqlite_master where type='table';""")
                results = table_name.fetchall()
                for table in results:
                    with sqlite3.connect(database_name) as connection:
                            cursor = connection.cursor()
                            data = cursor.execute(f"""SELECT SKU FROM {table[0]}""")
                            data = data.fetchall()
                            total_amount_per_database.append(len(data))
                            for sku in data:
                                big_sku_list.append(str(sku[0]))

    warehouse_total_amount = sum(total_amount_per_database)
    print(warehouse_total_amount)
    
    sku_total_dict = {sku:big_sku_list.count(sku) for sku in big_sku_list}
    print(sku_total_dict)

def validate_table_name(table_name=None, database_file_name=None):
    # This should provide a table name and database name
    valid_database_name = []
    if table_name != []:
        if database_file_name != None:
            print(database_file_name)
            with sqlite3.connect(database_file_name) as connection:
                cursor = connection.cursor()
                table = cursor.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';""")
                print(table.fetchone())
        if database_file_name == None:
            database = os.listdir()
            for database_name in database:
                if database_name.endswith('.db'):
                    with sqlite3.connect(database_name) as connection:
                        cursor = connection.cursor()
                        table_names = cursor.execute(""" select name from sqlite_master where type='table';""")
                        for table in table_names.fetchall():
                            if table[0] == table_name:
                                valid_database_name.append(database_name)
                                valid_database_name.append(table_name)
                                print('if table_name is being ran')
                            else:
                                pass
    return valid_database_name


total_amount_warehouse()
