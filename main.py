import sqlite3, os, uuid, qrcode, json
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
    # STILL WORKING ON THIS
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

def generate_all_qr_codes_database(database, description):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=13,
    )

    qr.add_data(database +', ' + description)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    draw = ImageDraw.Draw(qr_img)
    text = str(database) + ', ' + description
    font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    img_width, img_height = qr_img.size
    text_x = (img_width - text_width) // 8
    text_y = img_height - text_height - 80
    font_size = 20
    font = ImageFont.truetype("static/fonts/DejaVuSans.ttf", size=font_size) 
    
    draw.text((text_x, text_y), text, fill="black", font=font)

    qr_img.save('datahub/qrcodes-generated/' + database.replace('.db', '') + description.replace(' ', '').replace(',', '') + '.png')

def generate_qr_codes_for_database(database, table_name, location_name, pog_number=None):
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=13,
    )
    qr.add_data(database + ' ' + table_name + ' ' + location_name)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    draw = ImageDraw.Draw(qr_img)
    
    if pog_number != None:
        text = str(pog_number) + ' ' + str(table_name) + ' ' + location_name
    else:
        text = str(table_name) + ' ' + location_name
        
    font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    img_width, img_height = qr_img.size
    text_x = (img_width - text_width) // 8
    text_y = img_height - text_height - 80
    
    # Changing image size, left off here. Also note I might change the json data removing 'shelfs' and keeping only sections
    font_size = 20
    font = ImageFont.truetype("static/fonts/DejaVuSans.ttf", size=font_size) 
    
    draw.text((text_x, text_y), text, fill="black", font=font)

    # Generate random or specific end of filename?
    char_remove = [' ', ',']
    for chars in char_remove:
        location_name = location_name.replace(chars, '_')
    
    #updated_description
    qr_img.save('datahub/qrcodes-generated/' + database.replace('.db', '') + '_' + table_name + '_' + location_name.replace(',', '_') + '.png')

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

def create_new_item_group(table_name, location_name):
    try:
        with sqlite3.connect('datahub/' + 'stockroom_floor.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"create table {table_name} (SKU integer, DESCRIPTION text, PRICE integer, UNIQUE_CODE integer, CAPACITY integer, LOCATION string)")
            connection.commit()
    except sqlite3.OperationalError:
        print(f'"{table_name}" already exist...')
    generate_qr_codes_for_database(database='stockroom_floor.db', table_name=str(table_name), location_name=location_name)

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

def copy_item_to_inventory_database(unique_code=None, destination_filename=None, destination_table_name=None, location_text=None):
    # Copy an item into a database
    # Needs "location" update
    sku_data = show_scan_results_for_item(unique_code=unique_code)
    try:
        if sku_data[0] != None:
            if destination_filename == None:
                pass
            elif destination_filename != None:
                if os.path.exists('datahub/' + str(destination_filename)) == True:
                    try:
                        struct_data = [
                            (sku_data[0], sku_data[1], sku_data[2], unique_code, sku_data[4], location_text), 
                            (sku_data[0], sku_data[1], sku_data[2], unique_code, sku_data[4], location_text, sku_data[7], sku_data[6]),
                        ]
                        with sqlite3.connect('datahub/' + str(destination_filename)) as connection:
                           cursor = connection.cursor()
                           sql_command = f"INSERT INTO {destination_table_name} VALUES (:col1, :col2, :col3, :col4, :col5, :col6)"
                           cursor.execute(sql_command, {'col1': struct_data[0][0], 'col2': struct_data[0][1], 'col3': struct_data[0][2], 'col4': struct_data[0][3], 'col5': struct_data[0][4], 'col6':struct_data[0][5]})
                           connection.commit()
                           delete_items_from_database(unique_code=unique_code, item_and_destination_data=struct_data[1])
                           return 'deleted'
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

def unique_code_modification_and_transfer(sku_number=None, destination_filename=None, destination_table_name=None, location_text=None):
    with sqlite3.connect('datahub/product_information_database.db') as connection:
        cursor = connection.cursor()
        cursor = cursor.execute(f"SELECT {sku_number}, DESCRIPTION, PRICE, CAPACITY, LOCATION from product_info WHERE sku={sku_number}")
        sku_data = cursor.fetchone()
        new_modified_data = [
            (sku_data[0], sku_data[1], sku_data[2], generate_random_uuid(), sku_data[3], location_text)
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

def search_for_sku_image_file(sku):
    with open('sku_image_locations.json', 'r') as f:
        data = json.loads(f.read())
        return data[sku]
###########################################################

def gen_all_qr_tags_or_specific(stockroom_floor=None, sales_floor=None, warehouse_specific=None, sales_specific=None, sec_number=None):
    # This function returns "location" descriptions
    with open('datahub/pog_data.json') as f:
        data = json.loads(f.read())
    
    pog_names = ['Lights', "Drilling", 'Screwdrivers']
    pog_description = []
    
    if stockroom_floor != None:
        for pog in pog_names:
            rack_value = data[str(pog)]['Stockroom_pog']['1']
            pog_number = data[str(pog)]['Pog_number']
            pog_description.append('POG #' + pog_number + ', ' + str(pog) + ', ' + rack_value) 
    
    if sales_floor != None:
        range_list = []
        for pog in pog_names:
            values = len(data[str(pog)]['Sales_pog'])
            range_list.append(values)
            
        for pog in pog_names:
            for number, num in enumerate(range_list):
                for i in range(1, num):
                    try:
                        asile_value = data[str(pog)]['Sales_pog'][str(i)]
                        pog_number = data[str(pog)]['Pog_number']
                        pog_description.append('POG #' + pog_number + ', ' + str(pog) + ', ' + asile_value)
                    except KeyError:
                        pass
    
    elif warehouse_specific != None:
        r_value = data[str(warehouse_specific)]['Stockroom_pog']['1']
        pog_num = data[str(warehouse_specific)]['Pog_number']
        pog_description.append('POG #' + pog_num + ', ' + str(warehouse_specific) + ', ' + r_value)
    
    elif sales_specific != None:
        try:
            a_value = data[str(sales_specific)]['Sales_pog']["%s" % str(sec_number)]
            pog_num = data[str(sales_specific)]['Pog_number']
            pog_description.append('POG #' + pog_num + ', ' + str(sales_specific) + ', '+ a_value)
        except KeyError:
            print('Section number not found.')
            sys.exit(1)
    
    return pog_description

def print_specific_qr_tag(tag_name, sales=None, stockroom=None):
    # KEYWORD "SPECIFIC"
    # This function will serach for a specific "location" description. When the assoicate wants to only print one tag
    value = None

    if stockroom != None:
        if tag_name.lower() in ("22", "lights"):
            print('Generating Lights stockroom qr-tag')
            value = gen_all_qr_tags_or_specific(warehouse_specific=str('Lights'))
        elif tag_name.lower() in ("27", "screwdrivers"):
            print('Generating screwdrivers stockroom qr-tag')
            value = gen_all_qr_tags_or_specific(warehouse_specific=str('Screwdrivers'))
        elif tag_name.lower() in ("drilling", "33"):
            print('Generating Drilling stockroom qr tag')
            value = gen_all_qr_tags_or_specific(warehouse_specific=str('Drilling'))
        else:
            return None
    elif sales != None:
        if tag_name.lower() in ("22", "lights"):
            print("Generating Lights sales qr tag")
            value = gen_all_qr_tags_or_specific(sales_specific=str('Lights'), sec_number=str(sales))
        elif tag_name.lower() in ("27", "screwdrivers"):
            value = gen_all_qr_tags_or_specific(sales_specific=str('Screwdrivers'), sec_number=str(sales))
        elif tag_name.lower() in ("33", "drilling"):
            value = gen_all_qr_tags_or_specific(sales_specific=str('Drilling'), sec_number=str(sales))
        else:
            return None

    return value