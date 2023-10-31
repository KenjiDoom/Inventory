import sqlite3, os, uuid, qrcode
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
from deepdiff import DeepDiff

def total_amount_warehouse():
    total_amount_per_database = []
    big_sku_list = []
    
    database = os.listdir()
    database.remove('product_information_database.db')
    
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
    print('Total amount of items on home: ', str(warehouse_total_amount))
    
    # Total amount of items per sku in the entire warehouse
    sku_total_dict = {sku:big_sku_list.count(sku) for sku in big_sku_list}
    return sku_total_dict

def replen_pull_report():
    sku_list = []
    cap_list = []
    location_list = []
    database = os.listdir()
    
    # Exclude back-end database file
    database.remove('back-end-store.db')
    database.remove('product_information_database.db')

    for database_name in database:
        if database_name.endswith('.db'):
            with sqlite3.connect(database_name) as connection:
                cursor = connection.cursor()
                table_name = cursor.execute(""" SELECT name from sqlite_master where type='table';""")
                results = table_name.fetchall()
                for table in results:
                    with sqlite3.connect(database_name) as connection:
                        data = cursor.execute(f"""SELECT SKU, Capacity, Location from {str(table[0])}""")
                        data = data.fetchall()
                        for sku in data:
                            sku_list.append(sku[0])
                            cap_list.append(sku[1])
                            location_list.append(sku[2])

    # Orginal data before...
    cap_dict = {i:[sku_list.count(i), b] for (i, b) in zip(sku_list, cap_list)}
    total_amount_skus_present_day = {i:sku_list.count(i) for i in sku_list}
    
    # Orginal Day
    print('------ Day 1 report -------')
    day_1 =  {10034: 5, 40456: 7, 68896: 3}
    print(day_1)
    print('------ Present day report ----')
    print(total_amount_skus_present_day)
    print('-------------------------------')
    # Calculates how much was substracted, from yesterday's report to today's.
    amount_subtracted_warehouse = {key: day_1[key] - total_amount_skus_present_day.get(key, 0)
                           for key in day_1.keys()}

    # This is adding the capacity next to the current total amount. Total amount of skus and the capactiy amount.
    my_dict2 = {i:[sku_list.count(i), b] for (i, b) in zip(sku_list, cap_list)}
    current_peg_amount = {i:[sku_list.count(i), location_list.count(b)] for (i, b) in zip(sku_list, location_list)}

    diff = set(amount_subtracted_warehouse) - set(my_dict2)
    zeroed_out_skus = list(diff)
    if zeroed_out_skus != None:
        for sku in zeroed_out_skus:
            with sqlite3.connect('product_information_database.db') as connection:
                cur = connection.cursor()
                fix_missing = cur.execute(f""" SELECT SKU, CAPACITY from product_info where SKU={sku}""")
                number_data = fix_missing.fetchone()
                my_dict2.update({number_data[0]:[0, number_data[1]]})
                cap_dict.update({number_data[0]:[0, number_data[1]]})
                total_amount_skus_present_day.update({number_data[0]:0})
                current_peg_amount.update({number_data[0]:[0, number_data[1]]})
    else:
        pass

    # Adding percentage total of capacity amount
    print(my_dict2)
    for key in my_dict2:
        percentage = (40 / 100.0) * my_dict2[key][1]
        my_dict2[key][1] = round(percentage)
    
    
    print('--- How many items where sold / subtracted from the warehouse / meaning how many where removed from based on yesterdays report ----')
    print(amount_subtracted_warehouse)
    print('------------------------------')
    print('Original Capacity amount')
    print(cap_dict)
    print('------------------------------')
    print('Percentage capacity amount')
    print(my_dict2)
    print('------------------------------')
    print('Current amount of items in a location')
    print(current_peg_amount)
    print('------------------------------')
    
    all_amount = total_amount_warehouse()
    for a, b, c, d, e in zip(amount_subtracted_warehouse, my_dict2, cap_dict, current_peg_amount, all_amount):
        # Is the amount subtracted from the warehouse greter then the percentage quanity amount..

        # One thing it's not getting is the zero value
        if amount_subtracted_warehouse[a] > my_dict2[b][1]:
            print('                                             ')
            print('SO is ' + str(amount_subtracted_warehouse[a]) + ' greater then ' + str(my_dict2[b][1]))
            print('Yes ' + str(amount_subtracted_warehouse[a]) + ' is greater then ' + 'Percentage Capactiy: ' + str(my_dict2[b][1]) + ' : Orginal Capacity: ' + str(cap_dict[c][1]))
            print('The current amount in that peg is ' + str(current_peg_amount[d][1]))
            pull_amount = cap_dict[c][1] - current_peg_amount[d][1]
            print('Total OH:', all_amount[e], 'You need to pull:', str(pull_amount), 'from ' + str(b))
            print('------')
        else:
            print('NOT BEING REPLENISHED BECAUSE')
            print(str(amount_subtracted_warehouse[a]) + ' is not greater then ' + str(my_dict2[b][1]))
            print('----------------------------')
    
    # Whenever there is an inocrrect number of items in one dict, this whole program won't work.
    for x, h, g in zip(current_peg_amount, my_dict2, cap_dict):
        if current_peg_amount[x][0] == 0:
            print(str(current_peg_amount[x][0]) + ' is less than ' + str(my_dict2[h][1]))
            print('You need to pull',cap_dict[g][1] - current_peg_amount[x][0], 'from', str(h))

def save_results(data):
    current_date = date.today()
    day = str(current_date)
    print("Repot gen date : ", str(current_date))
    
    present_data = {'Date': day}
    present_data.update(data)
    file_object = json.dumps(present_data, indent=4)
    
    with open(str(day) +'.json', 'w') as file:
        file.write(file_object)

# Saving present data to file.
OH_amount = total_amount_warehouse()
save_results(OH_amount)

#total_amount_warehouse()
#replen_pull_report()
