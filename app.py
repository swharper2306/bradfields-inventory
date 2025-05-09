from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from contextlib import contextmanager

app = Flask(__name__)

DATABASE = 'inventory.db'

@contextmanager
def get_db_cursor(commit=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db_cursor(commit=True) as c:
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

@app.route('/')
def index():
    with get_db_cursor() as c:
        c.execute("SELECT * FROM inventory")
        items = c.fetchall()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['item_name']
    location = request.form['location']
    quantity = int(request.form['quantity'])
    barcode = request.form['barcode']

    with get_db_cursor(commit=True) as c:
        c.execute("INSERT INTO inventory (item_name, location, quantity, barcode) VALUES (?, ?, ?, ?)",
                  (name, location, quantity, barcode))
    return redirect('/')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    with get_db_cursor(commit=True) as c:
        c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    return redirect('/')

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if request.method == "POST":
        item_name = request.form["item_name"]
        location = request.form["location"]
        quantity = int(request.form["quantity"])
        barcode = request.form["barcode"]

        with get_db_cursor(commit=True) as c:
            c.execute(
                "UPDATE inventory SET item_name = ?, location = ?, quantity = ?, barcode = ? WHERE id = ?",
                (item_name, location, quantity, barcode, item_id),
            )
        return redirect("/")

    with get_db_cursor() as c:
        c.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        item = c.fetchone()
    return render_template("edit.html", item=item)

@app.route('/scan_update', methods=['POST'])
def scan_update():
    barcode = request.form['barcode'].strip()  # <-- Normalize input
    action = request.form['action']

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT quantity FROM inventory WHERE barcode = ?", (barcode,))
    result = c.fetchone()

    if result:
        current_qty = result['quantity']
        new_qty = current_qty + 1 if action == 'add' else max(current_qty - 1, 0)
        c.execute("UPDATE inventory SET quantity = ? WHERE barcode = ?", (new_qty, barcode))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'quantity': new_qty})
    else:
        conn.close()
        return jsonify({'status': 'error', 'message': f'Barcode not found: {barcode}'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)