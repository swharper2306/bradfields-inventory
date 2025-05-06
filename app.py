from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os

app = Flask(__name__)

# DB init
def init_db():
    if not os.path.exists('inventory.db'):
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT NOT NULL,
                        location TEXT NOT NULL,
                        quantity INTEGER NOT NULL DEFAULT 0
                    )''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['item_name']
    location = request.form['location']
    quantity = int(request.form['quantity'])

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("INSERT INTO inventory (item_name, location, quantity) VALUES (?, ?, ?)", (name, location, quantity))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
