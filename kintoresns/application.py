from flask import Flask, redirect, render_template, request, flash, session, url_for
from markupsafe import Markup
import os, time
import init_db
from datetime import datetime
import sns_user as user, sns_data as data   
from werkzeug.utils import secure_filename

# Flaskインスタンスと暗号化キーの指定
app = Flask(__name__)
app.secret_key = 'TIIDe5TUMtPUHpyu'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# dbの初期化
init_db.init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- URLのルーティング ---
@app.route('/')
@user.login_required
def index():
    me = user.get_id()
    return render_template('index.html', id=me,
            username=user.get_username(me),
            users=user.get_allusers(),
            fav_users=data.get_fav_list(me),
            timelines=data.get_timelines(current_user_id=me), user_id=me)

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

# ログアウト処理
@app.route('/logout')
def logout():
    user.try_logout()
    return redirect('/login')

# ユーザー登録処理
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

# お気に入り追加処理
@app.route('/add_fav/<int:fav_id>', methods=['POST'])
@user.login_required
def add_fav(fav_id):
    user_id = user.get_id()
    data.add_fav(user_id, fav_id)
    return redirect(f'/users/{fav_id}')

# お気に入り削除処理
@app.route('/remove_fav/<int:fav_id>', methods=['POST'])
@user.login_required
def remove_fav(fav_id):
    user_id = user.get_id()
    data.remove_fav(user_id, fav_id)
    return redirect(f'/users/{fav_id}')

# いいねの追加と削除を1つのルートで処理する
@app.route('/toggle_like/<int:post_id>', methods=['POST'])
@user.login_required
def toggle_like(post_id):
    user_id = user.get_id()
    if data.is_liked_by_user(user_id, post_id):
        data.remove_like(user_id, post_id)
    else:
        data.add_like(user_id, post_id)
    return redirect(request.referrer)

# post投稿処理
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
    categories = request.form.getlist("category")
    file = request.files.get('image')
    filename = None
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    if text:
        data.save_post(user_id, text, categories, filename)
    
    return redirect('/')

# post削除処理
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@user.login_required
def delete_post(post_id):
    user_id = user.get_id()
    data.delete_post(post_id, user_id)
    return redirect(request.referrer)

# ユーザーIDをすべてのテンプレートで自動的に利用できるようにする
@app.context_processor
def inject_user_id():
    user_id = user.get_id() if user.is_login() else None
    return dict(user_id=user_id)

@app.route('/users/<int:user_id>')
@user.login_required
def user_profile(user_id):
    current_user_id = user.get_id()  # 現在のログインユーザーのIDを取得
    conn = data.get_db_connection()
    
    # ユーザー情報を取得
    user_info = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user_info is None:
        return render_template('404.html'), 404  # ユーザーが存在しない場合は404エラーページを表示
    
    # お気に入り登録されているかどうかを確認
    is_fav = data.is_fav(current_user_id, user_id)
    
    # 投稿を取得
    posts = user.get_posts_by_user(user_id, current_user_id)
    
    for post in posts:
        post["comments"] = data.get_post_comments(post["id"])
        
    conn.close()
    
    # ユーザープロフィールページを表示
    return render_template(
        'users.html', user_info=user_info, posts=posts, is_fav=is_fav, user_id=user.get_id(), current_user_id=current_user_id,
    )

#ユーザーページに自己紹介文を追加
@app.route('/edit_bio', methods=['POST'])
@user.login_required
def edit_bio():
    user_id = user.get_id()
    bio = request.form.get('bio', '')

    conn = data.get_db_connection()
    conn.execute('UPDATE users SET bio = ? WHERE id = ?', (bio, user_id))
    conn.commit()
    conn.close()

    return redirect(f'/users/{user_id}')

#プロフィール画像のアップロード
@app.route('/upload_profile_image', methods=['POST'])
@user.login_required
def upload_profile_image():
    user_id = user.get_id()
    file = request.files['profile_image']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn = data.get_db_connection()
        conn.execute('UPDATE users SET profile_image = ? WHERE id = ?', (filename, user_id))
        conn.commit()
        conn.close()
    
    return redirect(f'/users/{user_id}')

# コメント投稿処理
@app.route('/add_comment/<int:post_id>', methods=['POST'])
@user.login_required
def add_comment(post_id):
    user_id = user.get_id()
    content = request.form.get('content')
    
    if content:
        conn = data.get_db_connection()
        conn.execute('INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)', (post_id, user_id, content))
        conn.commit()
        conn.close()

        # 通知を追加
        post_user_id = data.get_post_user_id(post_id)
        if post_user_id != user_id:
            message = f"{data.get_user_by_id(user_id)['username']}さんがあなたの投稿にコメントしました"
            data.add_notification(post_user_id, message)
    
    return redirect(request.referrer or '/')  # コメント投稿した元のページへリダイレクト

# カテゴリによる投稿フィルタリング
@app.route('/category/<category_name>')
@user.login_required
def category_posts(category_name):
    me = user.get_id()
    
    # "all"カテゴリが選択された場合はすべての投稿を表示
    if category_name == "all":
        posts = data.get_all_posts()
    else:
        user_id = user.get_id()
        posts = data.get_posts_by_category(category_name)
    
    return render_template('category.html', id=me,
                            username=user.get_username(me),
                            users=user.get_allusers(),
                            category_name=category_name,
                            posts=posts)

# 通知ページの表示
@app.route('/notifications')
@user.login_required
def notifications():
    user_id = user.get_id()
    notifications = data.get_notifications(user_id)
    return render_template('notifications.html', notifications=notifications)

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
    dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    return time.strftime('%Y年%m月%d日 %H:%M:%S')

# 改行を有効にするフィルタの追加
def linebreaks_filter(s):
    return Markup(s.replace('\n', '<br>'))

app.jinja_env.filters['datestr'] = datestr_filter
app.jinja_env.filters['linebreaks'] = linebreaks_filter

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0')
