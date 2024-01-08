from flask import Flask, render_template, request, redirect
import sqlite3, socket
from replen import *
from main import *

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        def user_database_validation():
            if os.path.exists('datahub/user-data.db') == True:
                return True
            else:
                return 'Back-end database not found...'
        
        try:
            if os.path.exists('datahub/user-data.db'):
                with sqlite3.connect('datahub/user-data.db') as connection:
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
            elif len(sku_number) == 10:
                sku_result = show_scan_results_for_item(unique_code=str(sku_number))
            elif len(sku_number) == 39:
                sku_result = show_scan_results_for_item(unique_code=str(sku_number[6:16]))

            if sku_result == None:  
                return render_template('search_error.html', error_message='Sku was not found...')
            else:
                totoal_OH = sku_total_amount(sku_number=str(sku_result[0]))
                description = sku_search(sku_number=sku_result[0])    
                image = search_for_sku_image_file(sku=str(sku_result[0]))
                try:
                    results = [(sku_result[0], sku_result[1], sku_result[2], totoal_OH, sku_result[5])]
                except IndexError:
                    results = [(sku_result[0], sku_result[1], sku_result[2], totoal_OH, description[0][2])]
                return render_template('search.html', results=results, image_file_name=str(image))
        except UnboundLocalError:
            return render_template('search.html', error_message='Sku was not found...')

    return render_template('search.html')

@app.route('/label', methods=['GET', 'POST'])
def labelpro():
    if request.method == 'POST':
        try:
            if request.form.get('item_button') == 'item':
                dialog_box = request.form['item_name']
                comma_value = dialog_box.find(',')
                if dialog_box.find(',') < 0:
                    try:
                        # Generate specific qr tag
                        print('Item tag now scanned!')
                        item = dialog_box[6:16]
                        data = show_scan_results_for_item(unique_code=item)
                        generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[6], database_file_name=data[7])
                        return render_template('label.html', successful_message='Successfully generated ' + str(data[0]))
                    except TypeError:
                        item = int(dialog_box)
                        if isinstance(item, int) == True:
                            item = str(dialog_box)
                            if len(item) == 10:
                                data = show_scan_results_for_item(unique_code=item)
                                generate_qr_codes_for_sku(sku=data[0], unique_code=data[3], table_name=data[6], database_file_name=data[7])
                                return render_template('label.html', successful_message='Successfully generated ' + str(data[3]))

                elif str(dialog_box[:comma_value]) == 'sales_floor.db':
                    # Generate sales based on pog name.
                    after_sales_value = dialog_box[comma_value + 2:]
                    pog_name_value = after_sales_value.find(',') + 2
                    pog = after_sales_value[pog_name_value:]
                    pog_last_comma_value = after_sales_value[pog_name_value:].find(',')
                    pog_name = pog[:pog_last_comma_value]
                    data = generate_specfic_pog_tag(pog_data=str(pog_name), sales_floor='True')
                    for i in data:
                        generate_all_qr_codes_database(database='sales_floor.db', description=str(i))
                    return render_template('label.html', successful_message='Successfully generated ' + str(pog_name))
                elif str(dialog_box[:comma_value]) == 'stockroom_floor.db':
                    # Generate stockroom based on pog name.
                    after_stockroom_value = dialog_box[comma_value + 2:]
                    pog_name_value = after_stockroom_value.find(',') + 2
                    pog = after_stockroom_value[pog_name_value:]
                    pog_last_comma_value = after_stockroom_value[pog_name_value:].find(',')
                    pog_name = pog[:pog_last_comma_value]
                    data = generate_specfic_pog_tag(pog_data=str(pog_name), stockroom_floor='True')
                    for i in data:
                        generate_all_qr_codes_database(database='stockroom_floor.db', description=str(i))
                    return render_template('label.html', successful_message='Successfully generated ' + str(pog_name))
                
        except TypeError as e:
            print(e)
            return render_template('label.html', error_message='Something went wrong...')
        except IndexError as e:
            print(e)
            return render_template('label.html', error_message='Something went wrong...')
        except NameError as e:
            print(e)
            return render_template('label.html', error_message='Something went wrong...')
        except ValueError as e:
            print(e)
            return render_template('label.html', error_message='Something went wrong...')

    return render_template('label.html')

@app.route('/moving_item', methods=['GET', 'POST'])
def moving_item():
    if request.method == 'POST':
        item = request.form['item_tag']
        print(item[6:16])

        destination_location = request.form['inventory_location']
        
        f_comma = destination_location.find(',') + 2
        s_comma = destination_location[f_comma:].find(',')
        t_comma = f_comma + s_comma
        table_comma = destination_location[t_comma + 2:].find(',')
        table = destination_location[t_comma + 2:]
        
        third_comma = destination_location[t_comma + 2:].find(',')
        table_name = table[:third_comma]
        
        f_value = f_comma - 2
        des_file = destination_location[:f_value]
        
        third_comma = third_comma + 2
        location = table[third_comma:]
        
        data = copy_item_to_inventory_database(unique_code=item[6:16], destination_filename=str(des_file), destination_table_name=str(table_name), location_text=str(location))
        if data == 'deleted':
            return render_template('moving_item.html', result='item was moved successfully...')
        else:
            return render_template('moving_item.html', error_message='Item not found...')
    
    return render_template('moving_item.html')

@app.route('/report_summary', methods=['GET', 'POST'])
def report_summary():
    # This function should be used for other areas of our program. It's well written...
    results = []
    replen_data = replen_pull_report()
    for key, value in replen_data.items(): 
        oh_number = sku_total_amount(sku_number=key)
        sku_search_results = sku_search(sku_number=key)
        
        sku_summary = {
            'SKU': key,
            'Description': sku_search_results[0][1],
            'Location': sku_search_results[0][2],
            'OH': oh_number,
            'Restock QTY': value
        }
        
        # Append the dictionary to the results list
        results.append(sku_summary)

    return render_template('report_summary.html', data=results)


@app.route('/IDSearch/<sku>')
def id_search(sku):
    unique_ids_data = search_skus_and_unique_ids(sku)
    return render_template('id_locations.html', unique_numbers=unique_ids_data, sku_number=sku)

@app.route('/save_replen', methods=['POST'])
def save_replen():
    # This functions runs when save replen button is clicked.
    # Clicking save on this function should also save to qty...
    all_amount = total_amount_warehouse(data_removed_name='backend_warehouse.db')
    re_data = replen_pull_report()
    save_results(data=all_amount, replen_data=re_data)
    save_qty()

    return render_template('report_summary_saved_results.html', popup_message='Results have been saved!')

@app.route('/work_report', methods=['GET', 'POST'])
def work_report(value_number):
    sku_list = ['10034', '68896', '40456']
    print(value_number)
    try:
        sku = sku_list[value_number]
        data = sku_search(sku_number=str(sku))
        OH = sku_total_amount(sku_number=str(sku))
        image_link = search_for_sku_image_file(sku=sku)
        sku_restock_qty = reading_qty_content(sku_number=str(sku))
        results = [(sku, data[0][3], OH, str(sku_restock_qty), image_link)]
    except IndexError as e:
        print(e)
    except TypeError as e:
        print(e)
    
    return render_template('work-template.html', data=results)

@app.route('/save_qty_restock', methods=['POST'])
def save_qty():
    re_data = replen_pull_report()
    save_restock_qty_for_report_page(restock_qty_data=re_data)
    return work_report(value_number=0)

class counter:
    def __init__(self):       
        self.value = 0
        self.sku_count = 2

    def increment(self, incremnet_number):
        if self.value >= self.sku_count:
            pass
        else:
            self.value += 1
        
        return self.value
    
    def decrement(self, decremnet_number):
        if self.value <= 0:
            self.value = 0
        else:
            self.value -= 1
        
        return self.value

counter_count = counter()

@app.route('/working_replen_button_clicks', methods=['POST'])
def button_click():
    # Keep track of skus not found...
    variable_value = request.form.get('variable_name')
    if variable_value == 'Increase_rightArrow':
        value = counter_count.increment(1)
    elif variable_value == 'Decrease_lefttarrow':
        value = counter_count.decrement(1)
    elif variable_value == 'Item_Not_Found':
        print('Item not found!')
    elif variable_value == 'Item_found':
        print('Item found!')

    return work_report(value_number=value)

if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())
    app.run(host='192.168.1.82', port=4000)
