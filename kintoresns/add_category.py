import sqlite3

def add_category_column():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    
    # categoryカラムを追加
    cur.execute('ALTER TABLE posts ADD COLUMN category TEXT')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_category_column()
