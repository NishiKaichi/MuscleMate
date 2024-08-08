from flask import Flask, redirect, render_template, request, flash, session
from markupsafe import Markup
import os, time
import sqlite3
from datetime import datetime
import sns_user as user, sns_data as data   

# Flaskインスタンスと暗号化キーの指定
app = Flask(__name__)
app.secret_key = 'TIIDe5TUMtPUHpyu'


# --- URLのルーティング ---
@app.route('/')
@user.login_required
def index():
    me = user.get_id()
    return render_template('index.html', id=me,
            username = user.get_username(me),
            users=user.get_allusers(),
            fav_users=data.get_fav_list(me),
            timelines=data.get_timelines(me),user_id=me)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if user.try_login(request.form):
            return redirect('/')
        flash("ログインに失敗しました")
    return render_template('login_form.html')

@app.route('/login/try', methods=['POST'])
def login_try():
    if user.try_login(request.form):
        return redirect('/')
    flash("ログインに失敗しました")
    return redirect('/login')

#ログアウト処理
@app.route('/logout')
def logout():
    user.try_logout()
    return redirect('/login')

#ユーザー登録処理
@app.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録処理"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['re_password']

        if password != confirm_password:
            error_message = 'パスワードが一致しません。もう一度入力してください。'
            return render_template('register.html', error_message=error_message, username=username)

        if not user.create_user(username, password):
            error_message = 'このユーザー名は既に使用されています。'
            return render_template('register.html', error_message=error_message, username='')

        flash('ユーザー登録が完了しました。')
        return redirect('/login')

    return render_template('register.html')

#お気に入り追加処理
@app.route('/add_fav/<int:fav_id>', methods=['POST'])
@user.login_required
def add_fav(fav_id):
    user_id = user.get_id()
    data.add_fav(user_id, fav_id)
    return redirect('/')

#お気に入り削除処理
@app.route('/remove_fav/<int:fav_id>', methods=['POST'])
@user.login_required
def remove_fav(fav_id):
    user_id = user.get_id()
    data.remove_fav(user_id, fav_id)
    return redirect('/')

#俳句投稿処理
@app.route('/write', methods=['GET'])
@user.login_required
def write():
    return render_template("write_form.html",id=user.get_id())

@app.route("/write/try",methods=["POST"])
@user.login_required
def try_write():
    user_id = user.get_id()
    print(request.form)
    content = request.form.get("text","")
    if content:
        data.save_haiku(user_id, content)
    else:
        print("no text provided")
    return redirect('/')

@app.route('/users/<int:user_id>')
@user.login_required
def user_profile(user_id):
    conn = data.get_db_connection()
    user_info = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    haikus = conn.execute('SELECT * FROM haikus WHERE user_id = ?', (user_id,)).fetchall()
    is_fav = data.is_fav(user.get_id(), user_id)
    conn.close()

    return render_template('users.html', user_info=user_info, haikus=haikus, is_fav=is_fav)

# --- テンプレートのフィルタなど拡張機能の指定 ---
@app.context_processor
def add_staticfile():
    return dict(staticfile=staticfile_cp)

def staticfile_cp(fname):
    path = os.path.join(app.root_path, 'static', fname)
    mtime = str(int(os.stat(path).st_mtime))
    return '/static/' + fname + '?v=' + str(mtime)

# 改行を有効にするフィルタを追加
@app.template_filter('linebreak')
def linebreak_filter(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;') \
         .replace('>', '&gt;').replace('\n', '<br>')
    return Markup(s)

# 日付をフォーマットするフィルタを追加
@app.template_filter('datestr')
def datestr_filter(s):
    dt=datetime.strptime(s,'%Y-%m-%d %H:%M:%S')
    return time.strftime('%Y年%m月%d日 %H:%M:%S')

def linebreaks_filter(s):
    return Markup(s.replace('\n', '<br>'))

app.jinja_env.filters['datestr'] = datestr_filter
app.jinja_env.filters['linebreaks'] = linebreaks_filter

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
