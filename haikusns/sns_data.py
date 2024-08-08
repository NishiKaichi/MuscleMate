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
def add_like(user_id, haiku_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO likes (user_id, haiku_id) VALUES (?, ?)', (user_id, haiku_id))
    conn.commit()
    conn.close()

#"""いいねを削除する"""
def remove_like(user_id, haiku_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM likes WHERE user_id = ? AND haiku_id = ?', (user_id, haiku_id))
    conn.commit()
    conn.close()

#"""特定の俳句へのいいねの数を取得する"""
def get_likes(haiku_id):
    conn = get_db_connection()
    likes = conn.execute('SELECT COUNT(*) AS like_count FROM likes WHERE haiku_id = ?', (haiku_id,)).fetchone()
    conn.close()
    return likes['like_count']

#"""ユーザーが特定の俳句を既にいいねしているかどうかをチェックする"""
def is_liked_by_user(user_id, haiku_id):
    conn = get_db_connection()
    like = conn.execute('SELECT 1 FROM likes WHERE user_id = ? AND haiku_id = ?', (user_id, haiku_id)).fetchone()
    conn.close()
    return like is not None

#"""俳句を保存する"""
def save_haiku(user_id, content):
    conn = get_db_connection()
    conn.execute('INSERT INTO haikus (user_id, content) VALUES (?, ?)', (user_id, content))
    conn.commit()
    conn.close()

#"""タイムラインを取得する"""
def get_timelines(user_id):
    conn = get_db_connection()
    haikus = conn.execute('''
        SELECT haikus.*, users.username, (SELECT COUNT(*) FROM likes WHERE likes.haiku_id = haikus.id) AS like_count
        FROM haikus
        JOIN users ON haikus.user_id = users.id
        WHERE haikus.user_id = ? OR haikus.user_id IN (SELECT fav_id FROM favs WHERE user_id = ?)
        ORDER BY haikus.timestamp DESC
    ''', (user_id, user_id)).fetchall()
    conn.close()
    return haikus
