import sqlite3

def init_db():
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS favs (
                user_id INTEGER,
                fav_id INTEGER,
                PRIMARY KEY (user_id, fav_id)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS haikus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

if __name__ == '__main__':
    init_db()

