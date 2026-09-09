from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "change_this_to_something_secret"

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'avatar1.png'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            cover_image TEXT,
            uploaded_by INTEGER,
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            chapter_number INTEGER,
            title TEXT,
            content TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            chapter_id INTEGER NOT NULL,
            position TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (chapter_id) REFERENCES chapters (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chapter_id INTEGER NOT NULL,
            highlighted_text TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (chapter_id) REFERENCES chapters (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            rating INTEGER,
            comment TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        avatar = request.form.get('avatar', 'avatar1.png')

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password, avatar) VALUES (?, ?, ?, ?)',
                (username, email, password, avatar)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Username or email already exists!"
        conn.close()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['avatar'] = user['avatar']
            return redirect(url_for('home'))
        else:
            return "Invalid username or password!"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/books')
def books():
    conn = get_db_connection()
    all_books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('books.html', books=all_books)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    chapters = conn.execute('SELECT * FROM chapters WHERE book_id = ?', (book_id,)).fetchall()
    like_count = conn.execute('SELECT COUNT(*) FROM likes WHERE book_id = ?', (book_id,)).fetchone()[0]
    reviews = conn.execute('SELECT reviews.*, users.username FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = ?', (book_id,)).fetchall()

    user_liked = False
    if 'user_id' in session:
        liked = conn.execute('SELECT * FROM likes WHERE user_id = ? AND book_id = ?', (session['user_id'], book_id)).fetchone()
        user_liked = liked is not None

    conn.close()
    return render_template('book_detail.html', book=book, chapters=chapters, like_count=like_count, reviews=reviews, user_liked=user_liked)

@app.route('/read/<int:chapter_id>')
def read_chapter(chapter_id):
    conn = get_db_connection()
    chapter = conn.execute('SELECT * FROM chapters WHERE id = ?', (chapter_id,)).fetchone()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (chapter['book_id'],)).fetchone()
    all_chapters = conn.execute('SELECT * FROM chapters WHERE book_id = ? ORDER BY chapter_number', (chapter['book_id'],)).fetchall()

    is_bookmarked = False
    if 'user_id' in session:
        bookmark = conn.execute(
            'SELECT * FROM bookmarks WHERE user_id = ? AND chapter_id = ?',
            (session['user_id'], chapter_id)
        ).fetchone()
        is_bookmarked = bookmark is not None

    conn.close()
    return render_template('read_chapter.html', chapter=chapter, book=book, all_chapters=all_chapters, is_bookmarked=is_bookmarked)

@app.route('/like/<int:book_id>', methods=['POST'])
def like_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    existing = conn.execute(
        'SELECT * FROM likes WHERE user_id = ? AND book_id = ?',
        (session['user_id'], book_id)
    ).fetchone()

    if existing:
        conn.execute('DELETE FROM likes WHERE user_id = ? AND book_id = ?', (session['user_id'], book_id))
    else:
        conn.execute('INSERT INTO likes (user_id, book_id) VALUES (?, ?)', (session['user_id'], book_id))

    conn.commit()
    conn.close()
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/review/<int:book_id>', methods=['POST'])
def add_review(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    rating = request.form['rating']
    comment = request.form['comment']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (?, ?, ?, ?)',
        (session['user_id'], book_id, rating, comment)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/bookmark/<int:chapter_id>', methods=['POST'])
def add_bookmark(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    chapter = conn.execute('SELECT * FROM chapters WHERE id = ?', (chapter_id,)).fetchone()

    existing = conn.execute(
        'SELECT * FROM bookmarks WHERE user_id = ? AND chapter_id = ?',
        (session['user_id'], chapter_id)
    ).fetchone()

    if not existing:
        conn.execute(
            'INSERT INTO bookmarks (user_id, book_id, chapter_id, position) VALUES (?, ?, ?, ?)',
            (session['user_id'], chapter['book_id'], chapter_id, 'start')
        )
        conn.commit()

    conn.close()
    return redirect(url_for('read_chapter', chapter_id=chapter_id))

@app.route('/bookmarks')
def view_bookmarks():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    bookmarks = conn.execute('''
        SELECT bookmarks.*, chapters.title as chapter_title, books.title as book_title
        FROM bookmarks
        JOIN chapters ON bookmarks.chapter_id = chapters.id
        JOIN books ON bookmarks.book_id = books.id
        WHERE bookmarks.user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('bookmarks.html', bookmarks=bookmarks)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)