#-----このファイルはデータベースに格納されている値を確認するためのものです。-----
#-----register関数がきちんと動作してdbに格納されたか、？-----

import sqlite3

def check_saved_posts():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    
    # 保存された投稿を確認
    cur.execute("SELECT content, category FROM posts")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    
    conn.close()

if __name__ == "__main__":
    check_saved_posts()