from main import *

def menu():
    print('1. Information on a product')
    print('2. Create a new product')
    print('3. Move an item ')
    print('4. Delete an item')
    print('5. Create a new location (New database file)')
    print('6. Create a new sub-location / totes (New database table)')
    print('7. Update all qr tags')
    print('8. Update or generate a specifc sku qr tag')
    try:
        user_option = input('Select an option: ')
    
        if user_option == '1':
            sku_number = input('Scan/Enter a SKU: ')
            sku_information = show_scan_results_for_item(SKU=sku_number)
            print(sku_information)
        
        elif user_option == '2':
            sku = input('Scan/Enter a SKU: ')
            database_location = input('Scan inventory tag: ')
            value = database_location.find(' ')
            unique_code_modification_and_transfer(sku_number=sku[0:5], destination_filename=database_location[0:value], destination_table_name=database_location[value:])
        
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
            database_name = input('Enter inventory name: ')
            database_creation(database_name)
        
        elif user_option == '6':
            database_name = input('Enter inventory name: ')
            tote_name = input('Enter tote/item group name: ')
            create_new_item_group(database_file_name, tote_name)
        
        elif user_option == '7':
            update_all_qr_tags()
        
        elif user_option == '8':
            item = input('Enter/Scan items ID code: ')
            if len(item) < int(11):
                data = show_scan_results_for_item(unique_code=item)
                generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[4], database_file_name=data[5])
            elif len(item) > int(10):
                data = show_scan_results_for_item(unique_code=item[6:16])
                generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[4], database_file_name=data[5])
    except KeyboardInterrupt:
        print('\nExiting...')

menu()