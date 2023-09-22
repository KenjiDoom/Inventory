from flask import Flask, render_template, request
import sqlite3, socket

app = Flask(__name__)

@app.route("/")
def website():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with sqlite3.connect('user-data.db') as connection:
            cursor = connection.cursor()
        
            store_number = request.form['storeNumber']
            username = request.form['username']
            password = request.form['password']

            query = "SELECT storeID, username, password FROM users WHERE storeID=? and username=? AND password=?"
            data = cursor.execute(query, (store_number, username, password))
            result = data.fetchone()
        
        if len(result) == 0:
            print('Sorry incorrect creds. Try again...')
        else:
            print('Login sucessful')
            return render_template('inventory.html')


    return render_template('login.html')

        
if __name__ == "__main__":
    IP = socket.gethostbyname(socket.gethostname())
    app.run(host=str(IP), port=4000)
