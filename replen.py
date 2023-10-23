import sqlite3, os, uuid, qrcode
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def total_amount_warehouse():
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

    # Total amount of items in the entire warehouse
    warehouse_total_amount = sum(total_amount_per_database)
    print(warehouse_total_amount)
    
    # Total amount of items per sku in the entire warehouse
    sku_total_dict = {sku:big_sku_list.count(sku) for sku in big_sku_list}
    print(sku_total_dict)

def replen_pull_report():
    sku_list = []
    cap_list = []
    database = os.listdir()
    database.remove('product_information_database.db')
    database.remove('user-data.db')
    
    for database_name in database:
        if database_name.endswith('.db'):
            with sqlite3.connect(database_name) as connection:
                cursor = connection.cursor()
                table_name = cursor.execute(""" SELECT name from sqlite_master where type='table';""")
                results = table_name.fetchall()
                for table in results:
                    with sqlite3.connect(database_name) as connection:
                        data = cursor.execute(f"""SELECT SKU, Capacity from {str(table[0])}""")
                        data = data.fetchall()
                        for sku in data:
                            sku_list.append(sku[0])
                            cap_list.append(sku[1])
    
    # Orginal data before...
    cap_dict = {i:[sku_list.count(i), b] for (i, b) in zip(sku_list, cap_list)}
    total_amount_skus_present_day = {i:sku_list.count(i) for i in sku_list}

    # Orginal Day
    day_1 =  {10034: 5, 40456: 15, 68896: 15}
    print(day_1)
    print(total_amount_skus_present_day)

    # Calculates how much was substracted, from yesterday's report to today's.
    amount_subtracted_warehouse = {key: day_1[key] - total_amount_skus_present_day.get(key, 0)
                           for key in day_1.keys()}
    print(amount_subtracted_warehouse)

    # This is adding the capacity next to the current total amount. Total amount of skus and the capactiy amount.
    my_dict2 = {i:[sku_list.count(i), b] for (i, b) in zip(sku_list, cap_list)}
    
    # Adding percentage total of capacity amount
    for key in my_dict2:
        percentage = (40 / 100.0) * my_dict2[key][1]
        my_dict2[key][1] = round(percentage)

    print(cap_dict)
    print(my_dict2)

    for a, b, c in zip(amount_subtracted_warehouse, my_dict2, cap_dict):
        if amount_subtracted_warehouse[a] > my_dict2[b][1]:
            print('SO is ' + str(amount_subtracted_warehouse[a]) + ' greater then ' + str(my_dict2[b][1]))
            amount_to_pull = cap_dict[c][1] - my_dict2[b][0]
            print(cap_dict[c][1])
            # LEFT OFF HERE
            print('Sku: ' + str(b) + ' Restock QTY: ' + str(amount_to_pull))
        else:
            pass

#total_amount_warehouse()
replen_pull_report()

