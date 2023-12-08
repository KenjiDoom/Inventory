from main import *
from replen import *
from read_pog_data import *

# All QR tags will eventually be physically printed.

def menu():
    print('1. Information on a product')
    print('2. Create a new product')
    print('3. Move an item ')
    print('4. Delete an item')
    print('5. Create a new item-group / totes')
    print('6. Generate sales or stockroom POG QR tags.')
    print('7. Generate specific POG QR tags.')
    print('8. Generate all SKU QR tags')
    print('9. Update or generate a specifc sku qr tag')
    print('10. Generate Report ')
    
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
            # Keep track of all totes created, and location their being saved to. Save this list into a json file.
            tote_name = input('Enter tote/item group name: ')
            pog_location = input('Scan or enter POG #: ')
            location_data = print_specific_qr_tag(tag_name=str(pog_location), stockroom='Yes')
            if pog_location == None:
                print('Missing POG number...')
            elif pog_location != None:
                create_new_item_group(table_name=str(tote_name), location_name=str(location_data))
                generate_qr_codes_for_database(database='stockroom_floor.db', table_name=str(tote_name), location_name=location_data)
        
        elif user_option == '6':
            # Printing all pog tags
            stock_option = input('Enter Sales or stockroom: ')
            if stock_option.lower() == 'sales':
                print_pog_qr_tags(sales_floor='Yes', stockroom=None)
            elif stock_option.lower() == 'stockroom':
                print('Generating stockroom pog')
                print_pog_qr_tags(sales_floor=None, stockroom='Yes')
        
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
                pog_name = input('Enter pog number/name: ')
                print_specific_qr_tag(tag_name=str(pog_name), stockroom='yes', sales=None)
            
        elif user_option == '8':
           # This will be messed up due to new location_name added
            # You need to also remove database printing. 
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
