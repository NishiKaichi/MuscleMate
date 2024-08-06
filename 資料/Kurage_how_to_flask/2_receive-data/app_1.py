#初期化
import flask
app_1 = flask.Flask(__name__)

#入力を促すページの定義
#index関数が返却する文字列は、HTML文になっています。 内容はとてもシンプルで、入力を受け取るためのformが一つと、その中に入力欄と送信ボタンが一つずつあるだけのものです。
@app_1.route('/')
def index():
    return '''
    <form action="/receive">
        <input name="value">
        <input type="submit">
    </form>
    '''

#入力を受け取るページの定義
@app_1.route('/receive')
def receive():
    return '入力されたデータは"' + flask.request.args.get('value') + '"です'


#Webサーバの実行
if __name__ == '__main__':   #必須の記述
    app_1.run()                #引き金