from main import *
from replen import *

def menu():
    print('1. Information on a product')
    print('2. Create a new product')
    print('3. Move an item ')
    print('4. Delete an item')
    print('5. Create a new item-group / totes')
    print('6. Generate ALL sales/stockroom POG QR tags.')
    print('7. Generate specific POG QR tags.')
    print('8. Generate all SKU QR tags')
    print('9. Generate a specifc sku qr tag')
    print('10. Generate Replen Report ')
    
    try:
        user_option = input('Select an option: ')
    
        if user_option == '1':
            sku_number = input('Scan/Enter a SKU: ')
            sku_information = show_scan_results_for_item(SKU=sku_number)
            print(sku_information)
        
        elif user_option == '2':
            sku = input('Scan/Enter a SKU: ')
            destination_location = input('Scan inventory tag: ')
            f_comma = destination_location.find(',') + 2
            s_comma = destination_location[f_comma:].find(',')

            t_comma = f_comma + s_comma

            table_comma = destination_location[t_comma + 2:].find(',')

            table = destination_location[t_comma + 2:]
            third_comma = destination_location[t_comma + 2:].find(',')

            table_name = table[:third_comma]
            
            #unique_code_modification_and_transfer(sku_number=sku[0:5], destination_filename=, destination_table_name=str(table_name))
        
        elif user_option == '3':
            try:
                item = input('Scan item tag: ')
                database_location = input('Scan inventory tag: ')
                value = database_location.find(' ')
                copy_item_to_inventory_database(unique_code=item[6:16], destination_filename=database_location[0:value], destination_table_name=database_location[value:].replace(' ', ''))
            except IndexError as e:
                return 'Error no item was scanned...' + str(e)
        
        elif user_option == '4':
            item = input('Enter code/scan item tag: ')
            if len(item) < int(11):
                print('This should be running')
                delete_items_from_database(unique_code=item)
            elif len(item) > int(10):
                print('Is this running mate?')
                delete_items_from_database(unique_code=item[6:16])
        
        elif user_option == '5':
            # To-do: Keep track of all totes created, and location their being saved to. Save this list into a json file.
            tote_name = input('Enter tote/item group name: ')
            pog_location = input('Scan or enter POG #: ')
            location_data = print_specific_qr_tag(tag_name=str(pog_location), stockroom='Yes')
            if pog_location == None:
                print('Missing POG number...')
            elif pog_location != None:
                for location in location_data:
                    create_new_item_group(table_name=str(tote_name), location_name=str(location))
                    generate_qr_codes_for_database(database='stockroom_floor.db', table_name=str(tote_name), location_name=location)
        
        elif user_option == '6':
            # Printing all pog tags
            stock_option = input('Enter Sales or stockroom: ')
            if stock_option.lower() == 'sales':
                qr_tags_data = gen_all_qr_tags_or_specific(stockroom_floor=None, sales_floor='Yes', warehouse_specific=None)
                for data in qr_tags_data:
                    generate_all_qr_codes_database(database='sales_floor.db', description=str(data))
            elif stock_option.lower() == 'stockroom':
                qr_tags_data = gen_all_qr_tags_or_specific(stockroom_floor='Yes', sales_floor=None, warehouse_specific=None)
                for i in qr_tags_data:
                    generate_all_qr_codes_database(database='stockroom_floor.db', description=str(i))

        elif user_option == '7':
            print('Printing specific pog tag')
            stock_option = input('Enter sales/stockroom: ')
            if stock_option.lower() == 'sales':
                pog_name = input('Enter pog number/name: ')
                section_number = input('Enter section number: ')
                value = print_specific_qr_tag(tag_name=str(pog_name), sales=str(section_number), stockroom=None)
                for data in value:
                    pog_number = data[:7]
                    tablename = data[9:]
                    value = tablename.find(',')
                    table = tablename[:value]
                    description = tablename[value + 2:]
                    generate_qr_codes_for_database(database='sales_floor.db', table_name=str(table), location_name=str(description), pog_number=str(pog_number))
            elif stock_option.lower() == 'stockroom':
                # LEFT OF HERE SOMETHING IS WRONG WITH DESCRIPTION
                pog_name = input('Enter pog number/name: ')
                value = print_specific_qr_tag(tag_name=str(pog_name), stockroom='yes', sales=None)
                for data in value:
                    pog_number = data[:7]
                    tablename = data[9:]
                    com_value = tablename.find(',')
                    table = tablename[:com_value]
                    description = tablename[com_value:]
                    generate_qr_codes_for_database(database='stockroom_floor.db', table_name=str(table), location_name=str(description), pog_number=str(pog_number))
            
        elif user_option == '8':
            update_all_qr_tags()
        
        elif user_option == '9':
            item = input('Enter/Scan items ID code: ')
            if len(item) < int(11):
                data = show_scan_results_for_item(unique_code=item)
                generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[4], database_file_name=data[5])
            elif len(item) > int(10):
                data = show_scan_results_for_item(unique_code=item[6:16])
                generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[4], database_file_name=data[5])
        elif user_option == '10':
            print('Generating report....')
            replen_pull_report()

    except KeyboardInterrupt:
        print('\nExiting...')

menu()
