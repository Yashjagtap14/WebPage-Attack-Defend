import sqlite3

conn = sqlite3.connect('social.db')
c = conn.cursor()

# Drop tables for a fresh start (dev only)
c.execute("DROP TABLE IF EXISTS users")
c.execute("DROP TABLE IF EXISTS posts")

# Users table
c.execute('''CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)''')

# Posts table
c.execute('''CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')

# Add sample users
c.execute("INSERT INTO users (username,password) VALUES ('alice','password'),('bob','1234')")

# Add sample posts
c.execute("INSERT INTO posts (user_id,content) VALUES (1,'Hello from Alice!'),(2,'Bob here <script>alert(`XSS`)</script>')")

conn.commit()
conn.close()
print("Database initialized.")
