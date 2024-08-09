import sqlite3

def init_db():
    with sqlite3.connect('data.db') as conn:
        cur = conn.cursor()
        
        # usersテーブルの作成
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        # postsテーブルの作成
        cur.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                category TEXT, 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # その他のテーブル作成
        cur.execute('''
            CREATE TABLE IF NOT EXISTS favs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fav_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (fav_id) REFERENCES users (id)
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (post_id) REFERENCES haikus(id)
            )
        ''')

    conn.commit()

if __name__ == '__main__':
    init_db()
