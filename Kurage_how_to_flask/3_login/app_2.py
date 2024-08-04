#初期化
import flask
app_2 = flask.Flask(__name__)
#-----Cookieを使う前準備-----#
app_2.config['SECRET_KEY'] = 'this is secret password'#'this is secret password'の部分はユーザーの安全を守るためのパスワードですので、ランダムな値にして、決して人に教えないようにしてください。

#ユーザー名とパスワードを受け取る
@app_2.route('/')
def index():
    return '''
    <form action="/login">
        ユーザー名: <input name="name"><br>
        パスワード: <input name="password" type="password"><br>
        <input type="submit" value="ログイン"><br>
    </form>
    '''

#-----ログインする-----#
@app_2.route('/login')
def login():
    flask.session['name'] = flask.request.args.get('name')#Flaskで値をCookieに保存する時は、flask.sessionというものの中に入れます

    return 'ようこそ ' + flask.session['name'] + 'さん<br><a href="/mypage">マイページへ</a>'

#-----マイページ-----#
@app_2.route('/mypage')
def mypage():
    return flask.session['name'] + 'さんのページ'

#Webサーバの実行
if __name__ == '__main__':
    app_2.run()