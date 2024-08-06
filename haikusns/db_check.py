#-----このファイルはデータベースに格納されている値を確認するためのものです。-----
#-----register関数がきちんと動作してdbに格納されたか、？-----

import sqlite3

def print_table_data(table_name):
    """指定されたテーブルのデータをすべて表示する"""
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    
    print(f"\n--- {table_name} テーブルのデータ ---")
    for row in rows:
        print(dict(row))
    
    conn.close()

if __name__ == '__main__':
    # 表示したいテーブルのリスト
    tables = ['users', 'favs', 'haikus']
    
    for table in tables:
        print_table_data(table)