from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Загружаем курсы и вопросы из JSON
with open('courses.json', 'r', encoding='utf-8') as f:
    courses_data = json.load(f)

# Создание базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            progress TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    username = request.cookies.get('username')
    return render_template('index.html', courses=courses_data["courses"], username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Неверный логин или пароль"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, progress) VALUES (?, ?, ?)', (username, password, '{}'))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/lesson/<number>/<coursename>")
def lesson(number,coursename):
    return render_template("lesson.html", lesson_name=f"Урок: {number}", course_name=f"Курс: {coursename}", youtube_video_id="n0xtO0x81cg?si=2_9a4LL6pmk7DAtj")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
