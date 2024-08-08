import sqlite3

def get_db_connection():
    """データベース接続を取得する"""
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_fav(user_id, fav_id):
    """お気に入りを追加する"""
    conn = get_db_connection()
    conn.execute('INSERT INTO favs (user_id, fav_id) VALUES (?, ?)', (user_id, fav_id))
    conn.commit()
    conn.close()

def is_fav(user_id, fav_id):
    """お気に入りかどうかをチェックする"""
    conn = get_db_connection()
    fav = conn.execute('SELECT * FROM favs WHERE user_id = ? AND fav_id = ?', (user_id, fav_id)).fetchone()
    conn.close()
    return fav is not None

def remove_fav(user_id, fav_id):
    """お気に入りを削除する"""
    conn = get_db_connection()
    conn.execute('DELETE FROM favs WHERE user_id = ? AND fav_id = ?', (user_id, fav_id))
    conn.commit()
    conn.close()

def get_fav_list(user_id):
    """お気に入りリストを取得する"""
    conn = get_db_connection()
    favs = conn.execute('''
        SELECT users.id as user_id, users.username
        FROM favs 
        JOIN users ON favs.fav_id = users.id 
        WHERE favs.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return favs

def save_haiku(user_id, content):
    """俳句を保存する"""
    conn = get_db_connection()
    conn.execute('INSERT INTO haikus (user_id, content) VALUES (?, ?)', (user_id, content))
    conn.commit()
    conn.close()

def get_timelines(user_id):
    """タイムラインを取得する"""
    conn = get_db_connection()
    haikus = conn.execute('''
        SELECT haikus.*, users.username
        FROM haikus
        JOIN users ON haikus.user_id = users.id
        WHERE haikus.user_id = ? OR haikus.user_id IN (SELECT fav_id FROM favs WHERE user_id = ?)
        ORDER BY haikus.timestamp DESC
    ''', (user_id, user_id)).fetchall()
    conn.close()
    return haikus
