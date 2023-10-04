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
    # 1. Update all qr tags in a database or all databases. (Also known as print all the items within a database)
    # 2. Update or generate a specific qr tag for a specific item (using unique_code or sku). 
    # 3. Show avaiable QR tag options
    # Idea: Scan SKU or inventory name for generating all the qr tags within that (tote, isle, inventory) (barcode)
    if request.method == 'POST':
        if request.form.get('item_button') == 'item':
            try:
                ID_code = request.form['item_name']
                # To-do: Detect if string is longer then 5 characters for a scan
                data = show_scan_results_for_item(unique_code=ID_code)
                generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[4], database_file_name=data[5])
                print('Done')
            except TypeError:
                return render_template('label.html', error_message='Nothing was entered...')
        elif request.form.get('inventory_button') == 'inventory':
            inventory_name = request.form['item_name']
            print(inventory_name)

    return render_template('label.html')

if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())
    app.run(host='192.168.1.81', port=4000)
