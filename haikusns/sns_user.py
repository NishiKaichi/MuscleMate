from flask import session, redirect
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

def get_db_connection():
    """データベース接続を取得する"""
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_user(username, password):
    """ユーザーを作成する"""
    password_hash = generate_password_hash(password)
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def is_login():
    """ログイン状態をチェックする"""
    return 'login' in session

def try_login(form):
    """ログインを試みる"""
    username = form.get('username', '')
    password = form.get('password', '')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user is None or not check_password_hash(user['password'], password):
        return False

    session['login'] = user['id']
    return True

def get_id():
    """ログイン中のユーザーIDを取得する"""
    return session['login'] if is_login() else None

def get_username(user_id):
    """ユーザーIDからユーザー名を取得する"""
    conn = get_db_connection()
    user = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user['username'] if user else None

def get_allusers():
    """全ユーザーを取得する"""
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def try_logout():
    """ログアウト処理"""
    session.pop('login', None)

# ログイン必須を処理するデコレーターを定義 --- (*7)
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_login():
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper
