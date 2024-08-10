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
    cur = conn.cursor()
    cur.execute('''
        SELECT posts.id, posts.content, posts.category, posts.timestamp, posts.image_path,
               users.username, posts.user_id,
               (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.timestamp DESC
    ''')
    
    posts = cur.fetchall()
    
    # タイムラインの各投稿に対応するコメントを取得
    timelines = []
    for post in posts:
        post_id = post[0]  # posts.id
        cur.execute('''
            SELECT comments.content, comments.timestamp, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = ?
            ORDER BY comments.timestamp ASC
        ''', (post_id,))
        comments = cur.fetchall()
        
        timelines.append({
            'id': post[0],
            'content': post[1],
            'category': post[2],
            'timestamp': post[3],
            'image_path': post[4],
            'username': post[5],
            'user_id': post[6],
            'like_count': post[7],
            'comments': comments
        })
    
    conn.close()
    return timelines


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

    for post in posts:
        post_id=post[0]
        conn.execute('''
            SELECT comments.content, comments.timestamp, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = ?
            ORDER BY comments.timestamp ASC
        ''', (post_id,))
        comments=conn.fetchall()
        posts.append({
            'id': post[0],
            'content': post[1],
            'category': post[2],
            'timestamp': post[3],
            'image_path': post[4],
            'username': post[5],
            'user_id': post[6],
            'like_count': post[7],
            'comments': comments
        })

    conn.close()
    return posts

#カテゴリに基づいて投稿を取得する
def get_posts_by_category(category_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT posts.id, posts.content, posts.category, posts.timestamp, posts.image_path,
               users.username, posts.user_id,
               (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.category LIKE ?
        ORDER BY posts.timestamp DESC
    ''', (f'%{category_name}%',))
    
    posts = []
    
    # 各投稿に対応するコメントを取得
    for post in cur.fetchall():
        post_id = post[0]  # posts.id
        cur.execute('''
            SELECT comments.content, comments.timestamp, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = ?
            ORDER BY comments.timestamp ASC
        ''', (post_id,))
        comments = cur.fetchall()
        
        posts.append({
            'id': post[0],
            'content': post[1],
            'category': post[2],
            'timestamp': post[3],
            'image_path': post[4],
            'username': post[5],
            'user_id': post[6],
            'like_count': post[7],
            'comments': comments
        })
    
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