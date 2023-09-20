from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def website():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.method == 'POST':
            try:
                connection = sqlite3.connect('user-data.db')
                cursor = connection.cursor()

                store_number = request.form['storeNumber']
                username = request.form['username']
                password = request.form['password']

                print(store_number, username, password)

                cursor.execute(f"SELECT storeID, username, password FROM users WHERE username={username} and password={password}")
                
                print('--------')
                results = cursor.fetchall()
                print(results)

                if len(results) == 0:
                    print('Sorry incorrect creds. Try again...')
                else:
                    return render_template('inventory.html')
            except sqlite3.OperationalError as e:
                print(e)
                print(username + 'not found...')


    return render_template('login.html')

        
if __name__ == "__main__":
    app.run(host="192.168.1.81", port=4000)
