from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response 
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'


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
            print("Make request!")
            resp = make_response(redirect('/'))
            resp.set_cookie("username", username, max_age=60*60*24*365*2)
            resp.set_cookie("progress", str([0,0,0,0]), max_age=60*60*24*365*2)
            # return redirect(url_for('index'))
            return resp
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
    progress = request.cookies.get("progress")
    print(progress)
    progress = progress[1:]
    progress = progress[:-1]
    progress = progress.split(",")
    return render_template("lesson.html", lesson_name=f"Урок: {number}", course_name=f"Курс: {coursename}", youtube_video_id="n0xtO0x81cg?si=2_9a4LL6pmk7DAtj", name=coursename)

@app.route("/redirect/<name>")
def test(name):
    dict_ = {"python": 0,
            'c++': 1,
            "go": 2,
            "rust": 3}
    progress = request.cookies.get("progress")
    progress = progress[1:]
    progress = progress[:-1]
    progress = progress.split(",")
    
    temp = name
    name = name.lower()
    progress[int(dict_[name])] = int(progress[int(dict_[name])]) + 1
    print(progress)
    resp = make_response(redirect(f"/lesson/{progress[dict_[name]]}/{temp}"))
    resp.set_cookie("progress", "0",max_age=0)
    resp.set_cookie("progress", str(progress), max_age=60*60*24*365*2)
    return resp


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
