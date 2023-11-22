import sqlite3, os, uuid, qrcode
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def database_creation(database_name):
    if os.path.isfile('datahub/' + database_name):
        with sqlite3.connect('datahub/' + database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {database_name.replace('.db', '') + '_inventory'}")
            rows = cursor.fetchall()
            print('File found...')
            print(rows)
    else:
        try:
            with sqlite3.connect('datahub/' + database_name + '.db') as connection:
                cursor = connection.cursor()
                table_name = database_name.replace('.db', '') + '_inventory'
                generate_qr_codes_for_database(database_name + '.db', table_name)
                cursor.execute(f"create table {table_name}(SKU integer, DESCRIPTION text, PRICE integer, UNIQUE_CODE integer, CAPACITY integer, LOCATION string)")
                connection.commit()
        except sqlite3.OperationalError:
            print('That file already exist...')

def update_all_qr_tags():
    print('Updating all qr tags with update-to-date locations and information')
    try:
        exclude_db_names = ['user-data.db', 'product_information_database.db']
        database_name = os.listdir('datahub')

        for ex_db in exclude_db_names:
            try:
                database_name.remove(ex_db)
            except ValueError:
                pass
        
        for database in database_name:
            if database.endswith('.db'):
                with sqlite3.connect('datahub/' + str(database)) as connection:
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
    font = ImageFont.truetype("static/fonts/DejaVuSans.ttf", size=font_size) 
    
    draw.text((text_x, text_y), text, fill="black", font=font)

    qr_img.save('datahub/qrcodes-generated/' + database.replace('.db', '') + '_' + table_name + '.png')

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
    font = ImageFont.truetype("static/fonts/DejaVuSans.ttf", size=30)
    
    img_width, img_height = qr_img.size
    text_x = (img_width - 90) // 2
    text_y = img_height - 40

    draw.text((text_x, text_y), text, fill="black", font=font)

    qr_img.save('datahub/qrcodes-generated/' + str(sku) + '_' + str(unique_code) + '.png', 'PNG')

def create_new_item_group(database_file_name, table_name):
    # This function is used for creating a new item group. AKA: creating a new table within a database.
    # database representing what area of the store you're inserting this item group into. i.e., stockroom or sales floor.
    # Might contain fixed values. Sales.db or backend.db
    try:
        with sqlite3.connect('datahub/' + database_file_name) as connection:
            cursor = connection.cursor()
            # Table name is the new database name you want to create
            cursor.execute(f"create table {table_name} (SKU integer, DESCRIPTION text, PRICE integer, UNIQUE_CODE integer, CAPACITY integer, LOCATION string)")
            connection.commit()
    except sqlite3.OperationalError:
        print(f'"{table_name}" already exist...')

def show_scan_results_for_item(table_name=None, database_file_name=None, SKU=None, unique_code=None):
    # Show's all the items within a database. (Inventory database)
    items = []
    if database_file_name and table_name != None:
        with sqlite3.connect('datahub/' + database_file_name) as connection:
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
            with sqlite3.connect('datahub/product_information_database.db') as connection:
                cursor = connection.cursor()
                sku_data = cursor.execute(f"SELECT {SKU}, DESCRIPTION, PRICE, LOCATION from product_info where sku={SKU}")
                return sku_data.fetchone()
        except sqlite3.OperationalError:
            return SKU + ' not found'
    
    elif unique_code != None:
        # Locate an item through all database files
        try:
            exclude_db_names = ['user-data.db']
            database = os.listdir('datahub')
            for ex_db in exclude_db_names:
                try:
                    database.remove(ex_db)
                except ValueError:
                    pass                
            for database_name in database:
                if database_name.endswith('.db'):
                    with sqlite3.connect('datahub/' + database_name) as connection:
                        cursor = connection.cursor()
                        table_names = cursor.execute("""select name from sqlite_master where type='table';""")
                        results = table_names.fetchall()
                        for table in results:
                            table_name = table[0]
                            with sqlite3.connect('datahub/' + database_name) as connection:
                                cursor = connection.cursor()
                                data = cursor.execute(f"""select {unique_code}, SKU, DESCRIPTION, PRICE, CAPACITY, LOCATION from {table_name} WHERE UNIQUE_CODE={unique_code}""")
                                data = data.fetchall()
                                value = len(data)
                                if data == None or len(data) == 0:
                                    pass
                                elif data != None:
                                    for i in range(value):
                                        #print(data[i][1], data[i][2], data[i][3], data[i][0], data[i][4], data[i][5], table_name, database_name)
                                        return data[i][1], data[i][2], data[i][3], data[i][0], data[i][4], data[i][5], table_name, database_name
        
        except sqlite3.OperationalError as e:
            print(e)
            print('!! Error must have scanned an inventory qr tag instead of a item. !!')

def copy_item_to_inventory_database(unique_code=None, destination_filename=None, destination_table_name=None):
    # Copy an item into a database
    # Needs datahub update
    sku_data = show_scan_results_for_item(unique_code=unique_code)
    try:
        if sku_data[0] != None:
            if destination_filename == None:
                pass
            elif destination_filename != None:
                if os.path.exists('datahub/' + destination_filename) == True:
                    try:
                        struct_data = [
                            (sku_data[0], sku_data[1], sku_data[2], unique_code, sku_data[4], sku_data[5]), 
                            (sku_data[0], sku_data[1], sku_data[2], unique_code, sku_data[4], sku_data[5], sku_data[7], sku_data[6]),
                        ]
                        print(destination_filename, destination_table_name)
                        with sqlite3.connect('datahub/' + str(destination_filename)) as connection:
                            cursor = connection.cursor()
                            sql_command = f"INSERT INTO {destination_table_name} VALUES (:col1, :col2, :col3, :col4, :col5, :col6)"
                            cursor.execute(sql_command, {'col1': struct_data[0][0], 'col2': struct_data[0][1], 'col3': struct_data[0][2], 'col4': struct_data[0][3], 'col5': struct_data[0][4], 'col6':struct_data[0][5]})
                            connection.commit()
                            delete_items_from_database(unique_code=unique_code, item_and_destination_data=struct_data[1])
                            return 'deleted'
                        # Hmmmm..... So it scans the item into the database BUT doesn't delet it. It claims
                    # except sqlite3.OperationalError as e:
                    #     print('Error scanned an item into an item.')
                    #     print(e)
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
    if item_and_destination_data != None: # Needs datahub update
        with sqlite3.connect('datahub/' + str(item_and_destination_data[6])) as connection:
            cursor = connection.cursor()
            cursor.execute(f"""DELETE from {str(item_and_destination_data[7])} where unique_code={str(unique_code)}""")
            print('Deleted.....')
            connection.commit()
    elif item_and_destination_data == None:
        item_data = show_scan_results_for_item(unique_code=unique_code)
        try:
            with sqlite3.connect('datahub/' + str(item_data[7])) as connection:
                cursor = connection.cursor()
                cursor.execute(f"""DELETE from {str(item_data[6])} where unique_code={str(unique_code)}""")
                print('Deleted.....')
                connection.commit()
        except TypeError as e:
            print('Item not found ' + str(e))

def unique_code_modification_and_transfer(sku_number=None, destination_filename=None, destination_table_name=None):
    with sqlite3.connect('datahub/product_information_database.db') as connection:
        cursor = connection.cursor()
        cursor = cursor.execute(f"SELECT {sku_number}, DESCRIPTION, PRICE, CAPACITY, LOCATION from product_info WHERE sku={sku_number}")
        sku_data = cursor.fetchone()
        print(sku_data)
        new_modified_data = [
            (sku_data[0], sku_data[1], sku_data[2], generate_random_uuid(), sku_data[3], sku_data[4])
        ]
        with sqlite3.connect('datahub/' + str(destination_filename)) as connection:
            cursor = connection.cursor()
            cursor.executemany(f'INSERT INTO {destination_table_name} VALUES (?, ?, ?, ?, ?, ?)', new_modified_data)
            connection.commit()
        print('Done..')

def total_amount_sku(sku_number=None, database_file_name=None, table_name=None, sku=None):
    # Used in website.py
    if sku_number != None:
        total_amount = []
        database = os.listdir('datahub/')
        database.remove('product_information_database.db')
        for database_name in database:
            if database_name.endswith('.db'):
                with sqlite3.connect('datahub/' + database_name) as connection:
                    cursor = connection.cursor()
                    table_names = cursor.execute(""" select name from sqlite_master where type='table';""")
                    results = table_names.fetchall()
                    for table in results:
                        table_name = table[0]
                        with sqlite3.connect('datahub/' + database_name) as connection:
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
        with sqlite3.connect('datahub/' + database_file_name) as connection:
            cursor = connection.cursor()
            all_data = cursor.execute(f"SELECT {sku} from {table_name} where sku={sku}")
        return len(all_data.fetchall())

def validate_table_name(table_name=None, database_file_name=None):
    # This should provide a table name and database name
    valid_database_name = []
    if table_name != []:
        if database_file_name != None:
            print(database_file_name)
            with sqlite3.connect('datahub/' + database_file_name) as connection:
                cursor = connection.cursor()
                table = cursor.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';""")
                valid_database_name.append(table.fetchone())
        if database_file_name == None:
            database = os.listdir()
            for database_name in database:
                if database_name.endswith('.db'):
                    with sqlite3.connect('datahub/' + database_name) as connection:
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

def search_skus_and_unique_ids(sku_number):
    # We all grepping all database files for 
    exclude_db_names = ['user-data.db', 'product_information_database.db']
    database = os.listdir('datahub')
    for ex_db in exclude_db_names:
        try:
            database.remove(ex_db)
        except ValueError:
            pass
    
    for database_name in database:
        if database_name.endswith('.db'):
            with sqlite3.connect('datahub/' + database_name) as connection:
                cursor = connection.cursor()
                table_names = cursor.execute(""" SELECT name from sqlite_master where type='table'; """)
                results = table_names.fetchall()
                for table in results:
                    table_name = table[0]
                    unique_id_query = cursor.execute(f""" SELECT SKU, UNIQUE_CODE, LOCATION from {table[0]} where SKU={sku_number} """)
                    unique_ids = unique_id_query.fetchall()
                    return unique_ids  

def sku_search(sku_number):
    location_list = []
    description_list = []
    with sqlite3.connect('datahub/product_information_database.db') as connection:
        cursor = connection.cursor()
        information_data = cursor.execute(f"""SELECT SKU, DESCRIPTION, LOCATION from product_info where sku={sku_number}""")
        information_data = information_data.fetchall()
   
    return information_data

def sku_total_amount(sku_number):
    # Remake of total_amount_sku, because I don't want to break things for now but this should be considered duplicate code.
    database = os.listdir('datahub/')
    sku_list = []
    try:
        database.remove('product_information_database.db')
        database.remove('user-data.db')
    except ValueError:
        pass
    for database_name in database:
        if database_name.endswith('.db'):
            with sqlite3.connect('datahub/' + str(database_name)) as connection:
                cursor = connection.cursor()
                table_name = cursor.execute(""" select name from sqlite_master where type='table';""")
                results = table_name.fetchall()
                for table in results:
                    data = cursor.execute(f""" select SKU from {table[0]} where SKU={sku_number}""")
                    data = data.fetchall()
                    for sku in data:
                        sku_list.append(sku)
    return len(sku_list)