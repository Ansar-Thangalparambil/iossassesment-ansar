from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create table if not exists
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
        return redirect('/')
    
    # Fetch all names
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    conn.close()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
