import sqlite3

def check_posts_table():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    
    # postsテーブルのカラム情報を取得
    cur.execute("PRAGMA table_info(posts);")
    columns = cur.fetchall()
    print("Columns in posts table:", columns)
    
    conn.close()

if __name__ == "__main__":
    check_posts_table()