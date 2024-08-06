#初期化
import flask                 #Flaskのインポート
app = flask.Flask(__name__)  #flaskモジュールに含まれるFlaskクラスのインスタンスを生成する
                             #ここで宣言されているappという変数を通してFlaskにアクセスすることになる

#ページの定義
@app.route('/')              #次に定義する動作（関数）にアクセスするためのアドレスを示している。 今回は'/'なので、http://localhost:5000/ でアクセスすることが出来る。 もしもこれが'/hello'となっていれば、http://localhost:5000/hello でアクセスすることが出来るようになる。
def hello_world():           #hello_worldという名前の関数を定義
    return 'Hello World!'    #Hello World!'という文をクライアントに返す
                             # Flaskを使用する場合（関数の頭に@app.routeを付ける場合）は文字列しか返せないが、@app.routeを付けずに作った関数であれば数字やその他の物を返すことも出来る。

#Webサーバの実行
if __name__ == '__main__':   #必須の記述
    app.run()                #引き金