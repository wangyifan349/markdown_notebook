import os
import random
import string
from flask import (Flask, render_template, request, redirect, url_for, session,
                   flash, send_from_directory, abort)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 实际部署请换更安全的随机密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'  # 设置数据库URI，使用sqlite数据库文件
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭轨迹修改，提升性能
app.config['UPLOAD_FOLDER'] = 'uploads'  # 视频上传目录
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 最大上传限制500MB

db = SQLAlchemy(app)  # 创建数据库实例

# 用户模型，包含用户名和密码哈希，及与视频的一对多关联
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # 唯一用户名
    password_hash = db.Column(db.String(128), nullable=False)  # 密码哈希存储
    videos = db.relationship('Video', backref='owner', lazy=True)  # 关联用户的视频列表

    def set_password(self, password):
        # 生成密码哈希，PBKDF2+SHA256算法，salt长度16
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password):
        # 验证密码，比较输入密码与存储哈希是否匹配
        return check_password_hash(self.password_hash, password)

# 视频模型，存储文件名、标题、是否公开、及所属用户ID
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键ID
    filename = db.Column(db.String(256), nullable=False)  # 文件名存储
    title = db.Column(db.String(256), nullable=False)  # 视频标题
    visible = db.Column(db.Boolean, default=True)  # 是否公开可见
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 所属用户外键

# 判断是否为允许的视频文件扩展
def allowed_file(filename):
    allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm'}  # 允许的视频格式集合
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# 计算两个字符串的最长公共子序列长度
def lcs_length(a, b):
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]  # 初始化dp表
    for i in range(m):
        for j in range(n):
            # 字符忽略大小写比较
            if a[i].lower() == b[j].lower():
                dp[i+1][j+1] = dp[i][j]+1
            else:
                dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])
    return dp[m][n]

from functools import wraps

# 装饰器，必须登录才能访问某些路由
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'danger')  # 提示用户先登录
            return redirect(url_for('login'))  # 重定向登录页
        return f(*args, **kwargs)
    return decorated

# 获取当前登录用户对象
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# 确保用户上传目录存在，返回路径
def user_folder(username):
    folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    os.makedirs(folder, exist_ok=True)  # 不存在则创建目录
    return folder

# 生成随机5位验证码（大写字母和数字）
def generate_captcha():
    choices = string.ascii_uppercase + string.digits
    return ''.join(random.choices(choices, k=5))

# 供验证码页面访问，生成验证码并存session，简单纯文本返回
@app.route('/captcha')
def captcha():
    code = generate_captcha()
    session['captcha'] = code.lower()  # 存小写方便比较，大小写不敏感
    # 返回html显示验证码，样式绿底白字加粗加间距
    return f"<div class='p-3 mb-3 bg-light text-success text-center' style='font-size:24px;letter-spacing:8px;font-weight:bold'>{code}</div>"

# 主页，若登录跳到管理页，否则登录页
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('manage'))
    return redirect(url_for('login'))

# 注册路由，支持GET显示页面，POST处理注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 取表单参数并去除空白
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        captcha_input = request.form.get('captcha', '').strip().lower()

        # 基础校验，用户名和密码不能为空
        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return redirect(url_for('register'))
        # 验证验证码是否正确（忽略大小写）
        if 'captcha' not in session or captcha_input != session['captcha']:
            flash('验证码错误', 'danger')
            return redirect(url_for('register'))
        # 用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))

        # 新建用户，设置密码哈希后写入数据库
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功，请登录', 'success')

        # 使用完验证码删除session中的验证码，防止重用
        session.pop('captcha', None)
        return redirect(url_for('login'))
    # GET请求直接渲染注册模板
    return render_template('register.html')

# 登录路由，支持GET显示页面，POST处理登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取用户名密码验证码表单数据
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        captcha_input = request.form.get('captcha', '').strip().lower()

        user = User.query.filter_by(username=username).first()
        # 校验验证码，验证码必须存在且匹配
        if 'captcha' not in session or captcha_input != session['captcha']:
            flash('验证码错误', 'danger')
            return redirect(url_for('login'))
        # 验证用户名密码，密码采用check_password_hash
        if not user or not user.check_password(password):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('login'))

        # 登录成功，保存user_id到session用于验证身份
        session['user_id'] = user.id
        flash(f'欢迎，{user.username}', 'success')
        session.pop('captcha', None)  # 使用完验证码即删除，防止重用

        return redirect(url_for('manage'))
    # GET请求渲染登录页面
    return render_template('login.html')

# 登出路由，清除session并跳转到登录页
@app.route('/logout')
def logout():
    session.clear()  # 清除所有session数据，注销登录
    flash('已登出', 'info')
    return redirect(url_for('login'))

# 用户管理页面，支持上传视频和管理自己视频（重命名、删除、隐藏切换）
@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    user = get_current_user()  # 获取当前登录用户

    # 处理上传请求
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('请选择上传文件', 'warning')
            return redirect(url_for('manage'))

        file = request.files['video']  # 获取上传文件
        title = request.form.get('title', '').strip()  # 视频标题，可选

        if file.filename == '':
            flash('请选择上传文件', 'warning')
            return redirect(url_for('manage'))
        if not allowed_file(file.filename):
            flash('仅支持mp4/avi/mov/mkv/webm等视频格式', 'warning')
            return redirect(url_for('manage'))

        # 标题未填时用文件名作为标题
        if not title:
            title = secure_filename(file.filename)

        # 目录对应用户文件夹，自动创建
        filename = secure_filename(file.filename)
        folder = user_folder(user.username)
        save_path = os.path.join(folder, filename)

        # 防止文件重名，追加编号
        basename, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{basename}_{counter}{ext}"
            save_path = os.path.join(folder, filename)
            counter += 1

        # 保存文件到磁盘
        file.save(save_path)

        # 记录数据库
        new_video = Video(filename=filename, title=title, visible=True, owner=user)
        db.session.add(new_video)
        db.session.commit()
        flash('上传成功', 'success')
        return redirect(url_for('manage'))

    # 查询用户所有视频用于渲染页面
    videos = Video.query.filter_by(user_id=user.id).all()
    return render_template('manage.html', videos=videos, username=user.username)

# 删除视频请求处理，必须是视频所有者操作
@app.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id):
    user = get_current_user()
    video = Video.query.get_or_404(video_id)  # 查询视频，找不到404

    # 权限验证，只能删除自己视频
    if video.user_id != user.id:
        abort(403)  # 禁止访问

    try:
        # 删除硬盘文件
        path = os.path.join(user_folder(user.username), video.filename)
        if os.path.exists(path):
            os.remove(path)
        # 删除数据库记录
        db.session.delete(video)
        db.session.commit()
        flash('视频已删除', 'success')
    except Exception as e:
        # 如果失败显示错误信息
        flash(f'删除失败：{e}', 'danger')
    return redirect(url_for('manage'))

# 视频重命名，仅更新数据库标题
@app.route('/video/<int:video_id>/rename', methods=['POST'])
@login_required
def rename_video(video_id):
    user = get_current_user()
    video = Video.query.get_or_404(video_id)

    if video.user_id != user.id:
        abort(403)

    new_title = request.form.get('title', '').strip()
    if new_title:
        video.title = new_title
        db.session.commit()
        flash('标题已更新', 'success')
    else:
        flash('标题不能为空', 'warning')
    return redirect(url_for('manage'))

# 切换视频显示状态，公开/隐藏切换
@app.route('/video/<int:video_id>/toggle_visibility', methods=['POST'])
@login_required
def toggle_visibility(video_id):
    user = get_current_user()
    video = Video.query.get_or_404(video_id)

    if video.user_id != user.id:
        abort(403)

    video.visible = not video.visible  # 取反切换状态
    db.session.commit()
    flash(f'视频状态已切换为{"公开" if video.visible else "隐藏"}', 'info')
    return redirect(url_for('manage'))

# 查看指定用户公开视频列表
@app.route('/user/<username>')
def view_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # 只显示公开视频
    videos = Video.query.filter_by(user_id=user.id, visible=True).all()
    return render_template('view_user.html', user=user, videos=videos)

# 播放指定用户指定视频页面
@app.route('/user/<username>/video/<int:video_id>')
def play_video(username, video_id):
    user = User.query.filter_by(username=username).first_or_404()
    video = Video.query.get_or_404(video_id)

    # 视频必须属于该用户，并且是公开的
    if video.user_id != user.id or not video.visible:
        abort(404)

    folder = user_folder(user.username)
    return render_template('play_video.html', video=video, username=username)

# 静态发送视频文件接口，验证视频存在且公开才允许访问，防止访问隐藏视频
@app.route('/user/<username>/video_file/<filename>')
def serve_video(username, filename):
    folder = user_folder(username)
    user = User.query.filter_by(username=username).first_or_404()
    video = Video.query.filter_by(user_id=user.id, filename=filename, visible=True).first()
    if not video:
        abort(404)
    return send_from_directory(folder, filename)

# 用户搜索，依据输入关键字与用户名最长公共子序列长度降序排列
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            all_users = User.query.all()

            users_with_score = []
            for u in all_users:
                # 计算LCS，忽略大小写
                score = lcs_length(query, u.username)
                users_with_score.append((score, u))
            # 按score降序排序
            users_with_score.sort(key=lambda x: x[0], reverse=True)
            results = [u for score, u in users_with_score if score > 0]
            if not results:
                flash('没有匹配结果', 'warning')
    return render_template('search.html', results=results, query=query)

# 在请求第一次调用前创建数据库和上传目录
@app.before_first_request
def init_db():
    db.create_all()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

# 启动flask应用，debug模式启用
if __name__ == '__main__':
    app.run(debug=False)
