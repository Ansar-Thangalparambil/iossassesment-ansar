from flask import Flask, render_template, request, redirect
import sqlite3
import string
import random
import os
import re

app = Flask(__name__)

# ---------- Database Setup ----------
DB_FILE = "urls.db"

def init_db():
    """Initialize the database and create table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            long_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---------- Helper Functions ----------
def generate_short_code(length=6):
    """Generate a random alphanumeric short code."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def save_url_mapping(short_code, long_url):
    """Save the mapping of short code to long URL in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (short_code, long_url) VALUES (?, ?)",
        (short_code, long_url)
    )
    conn.commit()
    conn.close()

def get_long_url(short_code):
    """Retrieve the original URL from the short code."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def is_valid_url(url):
    """Validate the URL using regex."""
    pattern = re.compile(
        r'^(https?:\/\/)?'                  # http:// or https:// (optional)
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domain
        r'(:\d+)?'                          # optional port
        r'(\/[^\s]*)?$'                     # optional path
    )
    return re.match(pattern, url)

# ---------- Routes ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    error_message = None
    input_value = ""

    if request.method == 'POST':
        long_url = request.form['long_url'].strip()
        input_value = long_url

        # Auto-add http:// if missing
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'http://' + long_url

        # Validate URL
        if not is_valid_url(long_url):
            error_message = "Invalid URL! Please enter a correct URL."
        else:
            short_code = generate_short_code()
            save_url_mapping(short_code, long_url)
            short_url = request.host_url + short_code

    return render_template('index.html', short_url=short_url, error_message=error_message, input_value=input_value)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect short code to original URL or show an error message."""
    long_url = get_long_url(short_code)
    if long_url:
        return redirect(long_url)
    else:
        return render_template('index.html', error_message="Invalid short code! Please check the URL.", input_value=short_code, short_url=None)

# ---------- Start App ----------
if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True)
