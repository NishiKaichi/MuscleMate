from flask import Flask, redirect, render_template, request, flash, session,url_for
from markupsafe import Markup
import os, time
import sqlite3
from datetime import datetime
import sns_user as user, sns_data as data   
from werkzeug.utils import secure_filename

# Flaskインスタンスと暗号化キーの指定
app = Flask(__name__)
app.secret_key = 'TIIDe5TUMtPUHpyu'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
    return redirect(f'/users/{fav_id}')

#お気に入り削除処理
@app.route('/remove_fav/<int:fav_id>', methods=['POST'])
@user.login_required
def remove_fav(fav_id):
    user_id = user.get_id()
    data.remove_fav(user_id, fav_id)
    return redirect(f'/users/{fav_id}')

# いいねの追加と削除を1つのルートで処理する
@app.route('/toggle_like/<int:haiku_id>', methods=['POST'])
@user.login_required
def toggle_like(haiku_id):
    user_id = user.get_id()
    if data.is_liked_by_user(user_id, haiku_id):
        data.remove_like(user_id, haiku_id)
    else:
        data.add_like(user_id, haiku_id)
    return redirect(request.referrer)

#俳句投稿処理
@app.route('/write', methods=['GET'])
@user.login_required
def write():
    user_id = user.get_id()
    return render_template("write_form.html", user_id=user_id)

@app.route('/write/try', methods=['POST'])
@user.login_required
def try_write():
    user_id = user.get_id()
    text = request.form.get("text", "")
    file = request.files.get('image')
    filename = None
    if file:
        print(f"File received: {file.filename}")  # デバッグ用出力
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"Image saved as: {filename}")  # デバッグ用出力
        else:
            print("Invalid file type")  # デバッグ用出力
    else:
        print("No file received")  # デバッグ用出力
    if text:
        data.save_haiku(user_id, text, filename)
        print(f"Haiku saved with image: {filename}")  # デバッグ用出力
    else:
        print("No text provided")  # デバッグ用出力
    return redirect('/')


@app.route('/users/<int:user_id>')
@user.login_required
def user_profile(user_id):
    conn = data.get_db_connection()
    user_info = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user_info is None:
        return render_template('404.html'), 404  # 404エラーページを表示
    is_fav = data.is_fav(user.get_id(), user_id)
    conn.close()
    
    current_user_id = user.get_id()
    haikus = user.get_haikus_by_user(user_id, current_user_id)

    return render_template('users.html', user_info=user_info, haikus=haikus, is_fav=is_fav, user_id=user.get_id(),current_user_id=current_user_id) 

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
#改行を有効にするフィルタの追加
def linebreaks_filter(s):
    return Markup(s.replace('\n', '<br>'))

app.jinja_env.filters['datestr'] = datestr_filter
app.jinja_env.filters['linebreaks'] = linebreaks_filter

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0')