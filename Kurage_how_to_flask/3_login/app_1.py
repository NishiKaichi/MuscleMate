#初期化
import flask
app_1 = flask.Flask(__name__)

#ユーザー名とパスワードを受け取る
@app_1.route('/')
def index():
    return '''
    <form action="/login">
        ユーザー名: <input name="name"><br>
        パスワード: <input name="password" type="password"><br>
        <input type="submit" value="ログイン"><br>
    </form>
    '''

#ログインする
@app_1.route('/login')
def login():
    name = flask.request.args.get('name')

    return 'ようこそ ' + name + 'さん'

#Webサーバの実行
if __name__ == '__main__':
    app_1.run()