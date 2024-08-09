import sqlite3

#"""データベース接続を取得する"""
def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

#"""お気に入りを追加する"""
def add_fav(user_id, fav_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO favs (user_id, fav_id) VALUES (?, ?)', (user_id, fav_id))
    conn.commit()
    conn.close()

#"""お気に入りかどうかをチェックする"""
def is_fav(user_id, fav_id):
    conn = get_db_connection()
    fav = conn.execute('SELECT * FROM favs WHERE user_id = ? AND fav_id = ?', (user_id, fav_id)).fetchone()
    conn.close()
    return fav is not None

#"""お気に入りを削除する"""
def remove_fav(user_id, fav_id): 
    conn = get_db_connection()
    conn.execute('DELETE FROM favs WHERE user_id = ? AND fav_id = ?', (user_id, fav_id))
    conn.commit()
    conn.close()

#"""お気に入りリストを取得する"""
def get_fav_list(user_id):
    conn = get_db_connection()
    favs = conn.execute('''
        SELECT users.id as user_id, users.username
        FROM favs 
        JOIN users ON favs.fav_id = users.id 
        WHERE favs.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return favs

#"""いいねを追加する"""
def add_like(user_id, post_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO likes (user_id, post_id) VALUES (?, ?)', (user_id, post_id))
    conn.commit()
    conn.close()

#"""いいねを削除する"""
def remove_like(user_id, post_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id))
    conn.commit()
    conn.close()

#"""特定の俳句へのいいねの数を取得する"""
def get_likes(post_id):
    conn = get_db_connection()
    likes = conn.execute('SELECT COUNT(*) AS like_count FROM likes WHERE post_id = ?', (post_id,)).fetchone()
    conn.close()
    return likes['like_count']

#"""ユーザーが特定の俳句を既にいいねしているかどうかをチェックする"""
def is_liked_by_user(user_id, post_id):
    conn = get_db_connection()
    like = conn.execute('SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id)).fetchone()
    conn.close()
    return like is not None

#"""俳句を保存する"""

def save_post(user_id, content, category, image_path=None):
    conn = sqlite3.connect('data.db')
    try:
        if image_path:
            conn.execute('''
                INSERT INTO posts (user_id, content, category, timestamp, image_path) 
                VALUES (?, ?, ?, datetime("now"), ?)
            ''', (user_id, content, category, image_path))
        else:
            conn.execute('''
                INSERT INTO posts (user_id, content, category, timestamp) 
                VALUES (?, ?, ?, datetime("now"))
            ''', (user_id, content, category))
        conn.commit()
    finally:
        conn.close()


#"""タイムラインを取得する"""
def get_timelines():
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT posts.*, users.username, 
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.timestamp DESC
    ''').fetchall()
    conn.close()
    return posts

#カテゴリを得る
def get_category_by_post_id(post_id):
    conn = get_db_connection()
    category = conn.execute(
        'SELECT category FROM posts WHERE id = ?', (post_id,)
    ).fetchone()
    conn.close()
    return category['category'] if category else None