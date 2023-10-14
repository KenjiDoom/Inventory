from flask import Flask, render_template, request, redirect
import sqlite3, socket
from main import *

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        def user_database_validation():
            if os.path.exists('user-data.db') == True:
                return True
            else:
                return 'Back-end database not found...'
        
        try:
            if os.path.exists('user-data.db'):
                with sqlite3.connect('user-data.db') as connection:
                    cursor = connection.cursor()

                    store_number = request.form['storeNumber']
                    username = request.form['username']
                    password = request.form['password']

                    query = "SELECT storeID, username, password FROM users WHERE storeID=? and username=? AND password=?"
                    data = cursor.execute(query, (store_number, username, password))
                    result = data.fetchone()

                if result == None:
                    return render_template('login.html', error_message='Sorry incorrect creds. Try again...')
                else:
                    return render_template('inventory.html')
            else:
                db_status = user_database_validation()
                return render_template('error_message.html', error_message=str(db_status))
        
        except sqlite3.OperationalError as e:
            if user_database_validation() == True:
                pass
            else:
                print('Missing the user database')

    return render_template('login.html')

# Sku Search function
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        try:
            sku_number = request.form['sku']
            if len(sku_number) == 5:
                sku_result = show_scan_results_for_item(SKU=str(sku_number))
            elif len(sku_number) > 5:
                sku_result = show_scan_results_for_item(unique_code=str(sku_number[6:16]))

            if sku_result == None:
                return render_template('search.html', error_message='Sku was not found...')
            else:
                results = [(sku_result[0], sku_result[1], sku_result[2])]
                return render_template('search.html', results=results)
        
        except UnboundLocalError:
            return render_template('search.html', error_message='Sku was not found...')

    return render_template('search.html')

@app.route('/label', methods=['GET', 'POST'])
def labelpro():
    # Note label printing is mainly used for Price tags... but these functions can be used for items and databases
    # 1. Update all qr tags in a database or all databases. (Also known as print all the items within a database)
    # 2. Update or generate a specific qr tag for a specific item (using unique_code or sku). 
    # 3. Show avaiable QR tag options
    # Idea: Scan SKU or inventory name for generating all the qr tags within that (tote, isle, inventory) (barcode)
    if request.method == 'POST':
        try:
            if request.form.get('item_button') == 'item':
                # Item press
                    ID_code = request.form['item_name']
                    data = show_scan_results_for_item(unique_code=ID_code)
                    generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[4], database_file_name=data[5])
                    total_amount_of_skus = total_amount_sku(sku_number=data[0])
                    results = [(data[0], data[1], str(total_amount_of_skus), data[3])]
                    tr_names = [('Sku', 'Description', 'Total OH', 'ID Code')]

                    return render_template('label.html', results=results, tr_names=tr_names)
            
            elif request.form.get('inventory_button') == 'inventory':
                # Inventory press
                result = []
                inventory_name = request.form['item_name']
                if inventory_name == []:
                    pass
                elif inventory_name != []:    
                    if ".db" in inventory_name:
                        # Looks for table name and database file name
                        remove_db = inventory_name.find('.db') + 4
                        table = validate_table_name(table_name=str(inventory_name[remove_db:]), database_file_name=inventory_name[:remove_db - 1])
                        inventory_data = show_scan_results_for_item(table_name=str(table[0]), database_file_name=str(inventory_name[:remove_db - 1]))
                        generate_qr_codes_for_database(database=str(inventory_name[:remove_db - 1]), table_name=str(table[0]))
                    
                        for sku in inventory_data:
                            for i in range(len(inventory_data[0])):
                                numbers = sku[i][0]
                                amount = total_amount_sku(sku=numbers, database_file_name=str(inventory_name[:remove_db - 1]), table_name=str(table[0]))
                                result.append((sku[i][0], sku[i][1], amount, sku[i][3]))
                        
                        tr_names = [('Sku', 'Description', 'Quantity', 'ID Code')]
                        
                        return render_template('label.html', results=result, tr_names=tr_names)
                    else:
                        # Looks only for table name
                        table = validate_table_name(table_name=str(inventory_name))
                        inventory_data = show_scan_results_for_item(table_name=str(table[1]), database_file_name=str(table[0]))
                        generate_qr_codes_for_database(database=str(table[0]), table_name=str(table[1]))
                        
                        for sku in inventory_data:
                            for i in range(len(inventory_data[0])):
                                numbers = sku[i][0]
                                amount = total_amount_sku(sku=numbers, database_file_name=str(table[0]), table_name=str(table[1]))
                                result.append((sku[i][0], sku[i][1], amount, sku[i][3]))
                        
                        tr_names = [('Sku', 'Description', 'Quantity', 'ID Code')]

                        return render_template('label.html', results=result, tr_names=tr_names)
        
        except TypeError as e:
            print(e)
            return render_template('label.html', error_message='Something went wrong...')
        except IndexError as e:
            print(e)
            return render_template('label.html', error_message='Something went wrong...')

    return render_template('label.html')

@app.route('/moving_item', methods=['GET', 'POST'])
def moving_item():
    if request.method == 'POST':
        sku_number = request.form['sku']
        inventory = request.form['inventory_location']
        value = inventory.find(' ')
        data = copy_item_to_inventory_database(unique_code=sku_number[6:16], destination_filename=inventory[0:value], destination_table_name=inventory[value:].replace(' ', ''))
        if data == 'deleted':
            return render_template('moving_item.html', result='item was moved successfully...')
        else:
            return render_template('moving_item.html', error_message='Item not found...')

    return render_template('moving_item.html')

    return render_template('moving_item.html')

if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())
    app.run(host='192.168.1.82', port=4000)
