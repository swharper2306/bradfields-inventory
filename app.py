from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# DB init
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    barcode TEXT
                )''')

    try:
        c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
    except sqlite3.OperationalError:
        pass

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
    barcode = request.form['barcode']

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("INSERT INTO inventory (item_name, location, quantity, barcode) VALUES (?, ?, ?, ?)", 
              (name, location, quantity, barcode))
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
    
@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    if request.method == "POST":
        item_name = request.form["item_name"]
        location = request.form["location"]
        quantity = int(request.form["quantity"])
        barcode = request.form["barcode"]

        cursor.execute(
            "UPDATE inventory SET item_name = ?, location = ?, quantity = ?, barcode = ? WHERE id = ?",
            (item_name, location, quantity, barcode, item_id),
        )
        conn.commit()
        conn.close()
        return redirect("/")

    cursor.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return render_template("edit.html", item=item)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
