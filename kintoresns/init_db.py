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
        
        #コメントテーブル
        cur.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')        
        
        # 既存のテーブルにカラムが存在しない場合の処理
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        if 'profile_image' not in columns:
            cur.execute('ALTER TABLE users ADD COLUMN profile_image TEXT')

        # 既存のテーブルにカラムが存在しない場合の処理
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        if 'bio' not in columns:
            cur.execute('ALTER TABLE users ADD COLUMN bio TEXT')

    conn.commit()

if __name__ == '__main__':
    init_db()
