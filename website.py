from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def website():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':        
        store_number = request.form['storeNumber']
        username = request.form['username']
        password = request.form['password']

        print(store_number, username, password)

    return render_template('login.html')

        
if __name__ == "__main__":
    app.run(host="192.168.1.81", port=4000)
