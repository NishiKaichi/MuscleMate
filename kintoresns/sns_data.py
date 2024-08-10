import sqlite3
import pytz
from datetime import datetime

# 日本時間に変換する関数
def convert_to_jst(utc_dt):
    jst = pytz.timezone('Asia/Tokyo')
    utc_dt = datetime.strptime(utc_dt, '%Y-%m-%d %H:%M:%S')
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(jst)

# データベース接続を取得する
def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

# 通知を追加する
def add_notification(user_id, message):
    conn = get_db_connection()
    conn.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)', (user_id, message))
    conn.commit()
    conn.close()

# お気に入りを追加する
def add_fav(user_id, fav_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO favs (user_id, fav_id) VALUES (?, ?)', (user_id, fav_id))
    conn.commit()
    conn.close()

    # 通知を追加
    message = f"{get_user_by_id(user_id)['username']}さんがお気に入りに追加しました"
    add_notification(fav_id, message)

# お気に入りかどうかをチェックする
def is_fav(user_id, fav_id):
    conn = get_db_connection()
    fav = conn.execute('SELECT * FROM favs WHERE user_id = ? AND fav_id = ?', (user_id, fav_id)).fetchone()
    conn.close()
    return fav is not None

# お気に入りを削除する
def remove_fav(user_id, fav_id): 
    conn = get_db_connection()
    conn.execute('DELETE FROM favs WHERE user_id = ? AND fav_id = ?', (user_id, fav_id))
    conn.commit()
    conn.close()

# お気に入りリストを取得する
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

# いいねを追加する
def add_like(user_id, post_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO likes (user_id, post_id) VALUES (?, ?)', (user_id, post_id))
    conn.commit()
    conn.close()

    # 通知を追加
    post_user_id = get_post_user_id(post_id)
    if post_user_id != user_id:
        message = f"{get_user_by_id(user_id)['username']}さんがあなたの投稿にいいねしました"
        add_notification(post_user_id, message)

# いいねを削除する
def remove_like(user_id, post_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id))
    conn.commit()
    conn.close()

# 特定のpostへのいいねの数を取得する
def get_likes(post_id):
    conn = get_db_connection()
    likes = conn.execute('SELECT COUNT(*) AS like_count FROM likes WHERE post_id = ?', (post_id,)).fetchone()
    conn.close()
    return likes['like_count']

# ユーザーが特定のpostを既にいいねしているかどうかをチェックする
def is_liked_by_user(user_id, post_id):
    conn = get_db_connection()
    like = conn.execute('SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?', (user_id, post_id)).fetchone()
    conn.close()
    return like is not None

# postを保存する
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

# postを削除する
def delete_post(post_id, user_id):
    conn = get_db_connection()
    # 投稿がログイン中のユーザーによって作成されたか確認する
    post = conn.execute('SELECT * FROM posts WHERE id = ? AND user_id = ?', (post_id, user_id)).fetchone()
    if post:
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
    conn.close()

# タイムラインを取得する
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

# カテゴリを得る
def get_category_by_post_id(post_id):
    conn = get_db_connection()
    category = conn.execute(
        'SELECT category FROM posts WHERE id = ?', (post_id,)
    ).fetchone()
    conn.close()
    return category['category'] if category else None

# 全投稿を取得する
def get_all_posts():
    conn = get_db_connection()
    result = conn.execute(
        '''
        SELECT posts.*, users.username, 
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.timestamp DESC
        '''
    ).fetchall()

    for post in result:
        post_id=post[0]
        conn.execute('''
            SELECT comments.content, comments.timestamp, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = ?
            ORDER BY comments.timestamp ASC
        ''', (post_id,))
        comments=conn.fetchall()
        result.append({
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
    return result

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
    
    result = []
    
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
        
        result.append({
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
    return result


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

# ユーザーIDからユーザー情報を取得する関数を追加
def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

# post IDからユーザーIDを取得する関数を追加
def get_post_user_id(post_id):
    conn = get_db_connection()
    post_user_id = conn.execute('SELECT user_id FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return post_user_id['user_id'] if post_user_id else None

# ユーザーの通知を取得する関数を追加
def get_notifications(user_id):
    conn = get_db_connection()
    notifications = conn.execute('''
        SELECT id, message, created_at, read 
        FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    # 日本時間に変換
    jst_notifications = []
    for notification in notifications:
        notification_dict = dict(notification)
        notification_dict['created_at'] = convert_to_jst(notification['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        jst_notifications.append(notification_dict)
    
    conn.close()
    return jst_notifications