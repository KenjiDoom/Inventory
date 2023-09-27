from flask import Flask, render_template, request, redirect
import sqlite3, socket
from main import *

app = Flask(__name__)

@app.route("/")
def website():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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
                    print('Login sucessful')

                    return render_template('inventory.html')
            else:
                return render_template('error_message.html')
        except sqlite3.OperationalError as e:
            if os.path.exists('user-data.db') == True:
                pass
            else:
                print('Table does not exist.')

    return render_template('login.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        sku_number = request.form['sku']
        sku_result = show_scan_results_for_item(SKU=str(sku_number))
 
        if sku_result == None:
            return render_template('search.html', error_message='Sku was not found...')
        else:
            results = [(sku_result[0], sku_result[1], sku_result[2])]
            return render_template('search.html', results=results)

    return render_template('search.html')

if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())
    app.run(host='192.168.1.81', port=4000)
