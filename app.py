from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ========================
# Setup SQLite DB
# ========================
conn = sqlite3.connect('vuln.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin','admin')")
c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('user','1234')")
c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, author TEXT)''')
conn.commit()
conn.close()

# ========================
# Login Route (SQLi vulnerable)
# ========================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('vuln.db')
        c = conn.cursor()
        # SQL Injection Vulnerable Query
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        c.execute(query)
        result = c.fetchone()
        conn.close()
        if result:
            session['username'] = username
            return redirect('/feed')
        else:
            return "Invalid credentials"
    return render_template('login.html')

# ========================
# Register Route
# ========================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('vuln.db')
        c = conn.cursor()
        try:
            c.execute(f"INSERT INTO users (username,password) VALUES ('{username}','{password}')") # SQLi vulnerable
            conn.commit()
        except:
            conn.close()
            return "User exists!"
        conn.close()
        return redirect('/login')
    return render_template('register.html')

# ========================
# Feed Route (XSS vulnerable)
# ========================
@app.route('/feed', methods=['GET','POST'])
def feed():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        content = request.form['content']
        conn = sqlite3.connect('vuln.db')
        c = conn.cursor()
        c.execute(f"INSERT INTO posts (content, author) VALUES ('{content}','{session['username']}')")  # XSS vulnerable
        conn.commit()
        conn.close()
    conn = sqlite3.connect('vuln.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()
    return render_template('feed.html', username=session['username'], posts=posts)

# ========================
# Comment Route (CSRF vulnerable)
# ========================
comments_db = {}
@app.route('/comment/<int:post_id>', methods=['GET','POST'])
def comment(post_id):
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        comment_text = request.form['comment']
        comments_db.setdefault(post_id, []).append({'username': session['username'], 'content': comment_text})
    return render_template('comment.html', post={'id': post_id}, comments=comments_db.get(post_id, []))

# ========================
# Profile Route
# ========================
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')
    return render_template('profile.html', username=session['username'], email=f"{session['username']}@example.com")

# ========================
# Logout
# ========================
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
