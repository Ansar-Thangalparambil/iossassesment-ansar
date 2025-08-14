from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3
import string
import random
import os

app = Flask(__name__)

# ---------- Database Setup ----------
DB_FILE = "urls.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        short_code TEXT UNIQUE,
                        long_url TEXT
                      )''')
    conn.commit()
    conn.close()

# ---------- Helper Functions ----------
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def save_url_mapping(short_code, long_url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
    conn.commit()
    conn.close()

def get_long_url(short_code):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ---------- Routes ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url'].strip()
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'http://' + long_url  # Auto-fix missing scheme

        short_code = generate_short_code()
        save_url_mapping(short_code, long_url)
        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    else:
        return render_template('404.html'), 404

# ---------- Start App ----------
if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True)
