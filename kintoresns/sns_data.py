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

#"""特定のpostへのいいねの数を取得する"""
def get_likes(post_id):
    conn = get_db_connection()
    likes = conn.execute('SELECT COUNT(*) AS like_count FROM likes WHERE post_id = ?', (post_id,)).fetchone()
    conn.close()
    return likes['like_count']

#"""ユーザーが特定のpostを既にいいねしているかどうかをチェックする"""
def is_liked_by_user(user_id, post_id):
    conn = get_db_connection()
    like = conn.execute('SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id)).fetchone()
    conn.close()
    return like is not None

#"""postを保存する"""

def save_post(user_id, content, categories, image_path=None):
    conn = get_db_connection()
    try:
        # リストのカテゴリをカンマで結合して文字列にする
        categories_str = ','.join(categories)  
        if image_path:
            conn.execute('''
                INSERT INTO posts (user_id, content, category, timestamp, image_path) 
                VALUES (?, ?, ?, datetime("now"), ?)
            ''', (user_id, content, categories_str, image_path))
        else:
            conn.execute('''
                INSERT INTO posts (user_id, content, category, timestamp) 
                VALUES (?, ?, ?, datetime("now"))
            ''', (user_id, content, categories_str))
        conn.commit()
    finally:
        conn.close()

#postを削除する
def delete_post(post_id, user_id):
    conn = get_db_connection()
    # 投稿がログイン中のユーザーによって作成されたか確認する
    post = conn.execute('SELECT * FROM posts WHERE id = ? AND user_id = ?', (post_id, user_id)).fetchone()
    if post:
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
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

#全投稿を取得
def get_all_posts():
    conn = get_db_connection()
    posts = conn.execute(
        '''
        SELECT posts.*, users.username, 
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.timestamp DESC
        '''
    ).fetchall()

    # `sqlite3.Row` オブジェクトを辞書に変換してから操作
    result = []
    for post in posts:
        post_dict = dict(post)  # 辞書に変換
        post_dict['category'] = post_dict['category'].split(',')  # カテゴリをリストに変換
        result.append(post_dict)

    conn.close()
    return posts

#カテゴリに基づいて投稿を取得する
def get_posts_by_category(category_name, user_id):
    conn = get_db_connection()
    posts = conn.execute(
        '''
        SELECT posts.*, users.username, 
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count,
        (SELECT 1 FROM likes WHERE likes.user_id = ? AND likes.post_id = posts.id) AS liked_by_me
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.category LIKE ?
        ORDER BY posts.timestamp DESC
        ''', (user_id, f'%{category_name}%')
    ).fetchall()
    
    # `sqlite3.Row` オブジェクトを辞書に変換してから操作
    result = []
    for post in posts:
        post_dict = dict(post)  # 辞書に変換
        post_dict['category'] = post_dict['category'].split(',')  # カテゴリをリストに変換
        result.append(post_dict)
    
    conn.close()
    return posts

#コメント取得のための関数
def get_post_comments(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT comments.content, comments.timestamp, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = ?
        ORDER BY comments.timestamp ASC
    ''', (post_id,))
    comments = cur.fetchall()
    conn.close()
    return comments