import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "dev_secret_key"

DATABASE = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            category TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_name TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO users (email, password) VALUES (?, ?)',
            (email, password)
        )
        conn.commit()
        conn.close()

        flash('Registration Successful!')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Email or Password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html')


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']

        conn.execute(
            'INSERT INTO tasks (user_id, title, category) VALUES (?, ?, ?)',
            (session['user_id'], title, category)
        )
        conn.commit()

    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template('tasks.html', tasks=tasks)


@app.route('/complete_task/<int:id>')
def complete_task(id):
    conn = get_db_connection()

    conn.execute(
        'UPDATE tasks SET completed = 1 WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('tasks'))


@app.route('/delete_task/<int:id>')
def delete_task(id):
    conn = get_db_connection()

    conn.execute(
        'DELETE FROM tasks WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('tasks'))


@app.route('/blogs', methods=['GET', 'POST'])
def blogs():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        conn.execute(
            'INSERT INTO blogs (user_id, title, content) VALUES (?, ?, ?)',
            (session['user_id'], title, content)
        )

        conn.commit()

    blogs = conn.execute(
        'SELECT * FROM blogs WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template('blogs.html', blogs=blogs)


@app.route('/delete_blog/<int:id>')
def delete_blog(id):
    conn = get_db_connection()

    conn.execute(
        'DELETE FROM blogs WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('blogs'))


@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        image_name = request.form['image_name']

        conn.execute(
            'INSERT INTO notes (user_id, image_name) VALUES (?, ?)',
            (session['user_id'], image_name)
        )

        conn.commit()

    notes = conn.execute(
        'SELECT * FROM notes WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template('notes.html', notes=notes)


@app.route('/delete_note/<int:id>')
def delete_note(id):
    conn = get_db_connection()

    conn.execute(
        'DELETE FROM notes WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('notes'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)