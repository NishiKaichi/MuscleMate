#初期化
import flask
app_3 = flask.Flask(__name__)
#Cookieを使う前準備
app_3.config['SECRET_KEY'] = 'this is secret password'#'this is secret password'の部分はユーザーの安全を守るためのパスワードですので、ランダムな値にして、決して人に教えないようにしてください。

#ユーザー名とパスワードを受け取る
@app_3.route('/')
def index():
    return '''
    <form action="/login">
        ユーザー名: <input name="name"><br>
        パスワード: <input name="password" type="password"><br>
        <input type="submit" value="ログイン"><br>
    </form>
    '''

#ログインする
@app_3.route('/login')
def login():
    flask.session['name'] = flask.request.args.get('name')#Flaskで値をCookieに保存する時は、flask.sessionというものの中に入れます

    return 'ようこそ ' + flask.session['name'] + 'さん<br><a href="/mypage">マイページへ</a>'

#マイページ#
#-----ログイン済みかどうかのチェック-----#
@app_3.route('/mypage')
def mypage():
    if 'name' in flask.session: #nameという名前のデータがflask.sessionに保存されているかどうかチェック
        return flask.session['name'] + 'さんのページ<br><br><a href="/logout">ログアウト</a> <a href="/">トップページ</a>'
    else:
        return 'ログインしてください<br><br><a href="/">トップページ</a>'

#ログアウトする
@app_3.route('/logout')
def logout():
    del flask.session['name']

    return 'ログアウトしました<br><a href="/">トップページへ戻る</a>'

#Webサーバの実行
if __name__ == '__main__':
    app_3.run()