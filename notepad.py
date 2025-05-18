from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import markdown
from markupsafe import Markup

app = Flask(__name__)
app.secret_key = 'replace_with_a_long_random_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------------------------
# 数据模型定义
# ----------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    notes = db.relationship('Note', backref='user', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)

# ----------------------------------
# 工具函数
# ----------------------------------
def lcs_length(s1, s2):
    """计算s1和s2的最长公共子序列长度，忽略大小写"""
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m):
        for j in range(n):
            if s1[i].lower() == s2[j].lower():
                dp[i+1][j+1] = dp[i][j] + 1
            else:
                dp[i+1][j+1] = max(dp[i+1][j], dp[i][j+1])
    return dp[m][n]

def login_required(f):
    """装饰器：检查登录，未登录重定向"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("请先登录")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------
# 路由定义
# ----------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('notes'))
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        if not username or not password or not password2:
            flash('请完整填写表单')
            return redirect(url_for('register'))
        if password != password2:
            flash('两次密码输入不匹配')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('用户名已被注册')
            return redirect(url_for('register'))
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    return render_template_string(REGISTER_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'{user.username}，欢迎回来！')
            return redirect(url_for('notes'))
        else:
            flash('用户名或密码错误')
            return redirect(url_for('login'))
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    flash('已登出')
    return redirect(url_for('login'))

@app.route('/notes')
@login_required
def notes():
    user = User.query.get(session['user_id'])
    notes = user.notes
    return render_template_string(NOTES_HTML, user=user, notes=notes)

@app.route('/notes/new', methods=['GET', 'POST'])
@login_required
def new_note():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_public = ('is_public' in request.form)
        if not title:
            flash('标题不能为空')
            return redirect(url_for('new_note'))
        note = Note(title=title, content=content, user_id=session['user_id'], is_public=is_public)
        db.session.add(note)
        db.session.commit()
        flash('笔记创建成功')
        return redirect(url_for('notes'))
    return render_template_string(EDIT_NOTE_HTML, note=None, action_url=url_for('new_note'), page_title='新建笔记')

@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != session['user_id']:
        flash('无权编辑该笔记')
        return redirect(url_for('notes'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_public = ('is_public' in request.form)
        if not title:
            flash('标题不能为空')
            return redirect(url_for('edit_note', note_id=note_id))
        note.title = title
        note.content = content
        note.is_public = is_public
        db.session.commit()
        flash('笔记保存成功')
        return redirect(url_for('notes'))
    return render_template_string(EDIT_NOTE_HTML, note=note, action_url=url_for('edit_note', note_id=note.id), page_title='编辑笔记')

@app.route('/notes/<int:note_id>')
@login_required
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    is_owner = (note.user_id == session['user_id'])
    html_content = Markup(markdown.markdown(note.content, extensions=['extra', 'codehilite']))
    if not is_owner:
        if not note.is_public:
            flash('该笔记为私密，仅作者可见')
            return redirect(url_for('notes'))
        flash('您正在查看他人笔记，只读模式')
    return render_template_string(VIEW_NOTE_HTML, note=note, html_content=html_content, is_owner=is_owner)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = ''
    results = []
    if request.method == 'POST':
        query = request.form.get('username', '').strip()
        if not query:
            flash('请输入要搜索的用户名')
            return redirect(url_for('search'))
        users = User.query.filter(User.username != session['username']).all()

        scored_users = []
        for user in users:
            public_notes = [n for n in user.notes if n.is_public]
            if not public_notes:
                continue
            score = lcs_length(query, user.username)
            if score > 0:
                scored_users.append((score, user))
        scored_users.sort(key=lambda x: x[0], reverse=True)

        results = [item[1] for item in scored_users]

        if len(results) == 0:
            flash('无匹配用户')
    return render_template_string(SEARCH_HTML, query=query, results=results)

@app.route('/users/<int:user_id>/notes/<int:note_id>')
@login_required
def view_others_note(user_id, note_id):
    if user_id == session['user_id']:
        return redirect(url_for('view_note', note_id=note_id))
    user = User.query.get_or_404(user_id)
    note = Note.query.get_or_404(note_id)
    if note.user_id != user.id:
        flash('笔记不属于该用户')
        return redirect(url_for('search'))
    if not note.is_public:
        flash('该笔记为私密，仅作者可见')
        return redirect(url_for('search'))
    html_content = Markup(markdown.markdown(note.content, extensions=['extra', 'codehilite']))
    flash(f'您正在查看 {user.username} 的笔记，只读模式')
    return render_template_string(VIEW_NOTE_HTML, note=note, html_content=html_content, is_owner=False)

# ----------------------------------
# 模板字符串（Bootstrap 5  + MathJax + 代码高亮 + 公开复选）
# ----------------------------------
NAVBAR_HTML = '''
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="{{ url_for('notes') }}">Markdown笔记本</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" 
            data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" 
            aria-expanded="false" aria-label="切换导航">
      <span class="navbar-toggler-icon"></span>
    </button>
    {% if session.get('username') %}
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item"><a class="nav-link" href="{{ url_for('notes') }}">我的笔记</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('new_note') }}">新建笔记</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('search') }}">搜索用户</a></li>
      </ul>
      <span class="navbar-text me-3">登录用户：{{ session['username'] }}</span>
      <a class="btn btn-outline-light btn-sm" href="{{ url_for('logout') }}">登出</a>
    </div>
    {% endif %}
  </div>
</nav>
'''

LOGIN_HTML = '''
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>登录 - Markdown笔记本</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body>
    ''' + NAVBAR_HTML + '''
    <div class="container" style="max-width:400px;">
      <h2 class="mb-4">登录</h2>
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-warning">
            {% for msg in messages %}
              <div>{{ msg }}</div>
            {% endfor %}
          </div>
        {% endif %}
      {% endwith %}
      <form method="post" novalidate>
        <div class="mb-3">
          <label for="username" class="form-label">用户名</label>
          <input type="text" name="username" id="username" class="form-control" autocomplete="username" required autofocus>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">密码</label>
          <input type="password" name="password" id="password" class="form-control" autocomplete="current-password" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">登录</button>
      </form>
      <p class="text-center mt-3">没有账号？<a href="{{ url_for('register') }}">注册</a></p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

REGISTER_HTML = '''
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>注册 - Markdown笔记本</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body>
    ''' + NAVBAR_HTML + '''
    <div class="container" style="max-width:400px;">
      <h2 class="mb-4">注册</h2>
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-warning">
            {% for msg in messages %}
              <div>{{ msg }}</div>
            {% endfor %}
          </div>
        {% endif %}
      {% endwith %}
      <form method="post" novalidate>
        <div class="mb-3">
          <label for="username" class="form-label">用户名</label>
          <input type="text" name="username" id="username" class="form-control" autocomplete="username" required autofocus>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">密码</label>
          <input type="password" name="password" id="password" class="form-control" autocomplete="new-password" required>
        </div>
        <div class="mb-3">
          <label for="password2" class="form-label">确认密码</label>
          <input type="password" name="password2" id="password2" class="form-control" autocomplete="new-password" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">注册</button>
      </form>
      <p class="text-center mt-3">已有账号？<a href="{{ url_for('login') }}">去登录</a></p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

NOTES_HTML = '''
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>我的笔记 - Markdown笔记本</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body>
    ''' + NAVBAR_HTML + '''
    <div class="container mt-2">
      <h2>{{ user.username }} 的笔记列表</h2>
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-info" role="alert">
            {% for msg in messages %}
              <div>{{ msg }}</div>
            {% endfor %}
          </div>
        {% endif %}
      {% endwith %}

      {% if notes|length == 0 %}
        <div class="alert alert-secondary my-3">暂无笔记，<a href="{{ url_for('new_note') }}">点击新建</a>吧！</div>
      {% else %}
        <div class="list-group mb-3">
          {% for note in notes %}
            <a href="{{ url_for('view_note', note_id=note.id) }}" 
               class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
              {{ note.title }}
              <span>
                {% if note.is_public %}
                  <span class="badge bg-success me-2">公开</span>
                {% else %}
                  <span class="badge bg-secondary me-2">私密</span>
                {% endif %}
                <a href="{{ url_for('edit_note', note_id=note.id) }}" class="btn btn-outline-secondary btn-sm">编辑</a>
              </span>
            </a>
          {% endfor %}
        </div>
      {% endif %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

EDIT_NOTE_HTML = '''
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ page_title }} - Markdown笔记本</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script"></script>
  </head>
  <body>
    ''' + NAVBAR_HTML + '''
    <div class="container mt-2" style="max-width: 800px;">
      <h2>{{ page_title }}</h2>
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-danger" role="alert">
            {% for msg in messages %}
              <div>{{ msg }}</div>
            {% endfor %}
          </div>
        {% endif %}
      {% endwith %}
      <form method="post" novalidate>
        <div class="mb-3">
          <label for="title" class="form-label">标题</label>
          <input name="title" id="title" class="form-control" required value="{{ note.title if note else '' }}">
        </div>
        <div class="mb-3">
          <label for="content" class="form-label">内容（Markdown）</label>
          <textarea name="content" id="content" rows="15" class="form-control">{{ note.content if note else '' }}</textarea>
        </div>
        <div class="form-check mb-3">
          <input class="form-check-input" type="checkbox" value="true" id="is_public" name="is_public" {% if note and note.is_public %}checked{% endif %}>
          <label class="form-check-label" for="is_public">
            公开此笔记（允许其他用户搜索并查看）
          </label>
        </div>
        <button type="submit" class="btn btn-primary">{{ '保存' if note else '创建' }}</button>
        <a href="{{ url_for('notes') }}" class="btn btn-secondary ms-2">返回</a>
      </form>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

VIEW_NOTE_HTML = '''
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ note.title }} - Markdown笔记本</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      pre code {
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 4px;
        white-space: pre-wrap;
        display: block;
      }
    </style>
    <!-- MathJax 支持数学公式 -->
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script"></script>
  </head>
  <body>
    ''' + NAVBAR_HTML + '''
    <div class="container mt-2" style="max-width: 900px;">
      <h2>{{ note.title }}</h2>
      <p><small>用户：{{ note.user.username }}</small></p>
      {% if note.is_public %}
        <span class="badge bg-success mb-2">公开</span>
      {% else %}
        <span class="badge bg-secondary mb-2">私密</span>
      {% endif %}
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-info" role="alert">
            {% for msg in messages %}
              <div>{{ msg }}</div>
            {% endfor %}
          </div>
        {% endif %}
      {% endwith %}
      <hr>
      <div class="markdown-content mb-3">{{ html_content|safe }}</div>
      <a href="{{ url_for('notes') }}" class="btn btn-secondary">返回</a>
      {% if is_owner %}
        <a href="{{ url_for('edit_note', note_id=note.id) }}" class="btn btn-primary ms-2">编辑</a>
      {% endif %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

SEARCH_HTML = '''
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>搜索用户 - Markdown笔记本</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body>
    ''' + NAVBAR_HTML + '''
    <div class="container mt-2" style="max-width: 800px;">
      <h2>搜索其他用户的笔记</h2>
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-warning" role="alert">
            {% for msg in messages %}
              <div>{{ msg }}</div>
            {% endfor %}
          </div>
        {% endif %}
      {% endwith %}
      <form method="post" class="row g-3 mb-4" novalidate>
        <div class="col-9 col-sm-10">
          <input type="text" name="username" class="form-control" placeholder="输入用户名" value="{{ query }}">
        </div>
        <div class="col-3 col-sm-2">
          <button type="submit" class="btn btn-primary w-100">搜索</button>
        </div>
      </form>
      {% if results %}
        <h4>搜索结果（按最长公共子序列降序）：</h4>
        <ul class="list-group">
          {% for user in results %}
            <li class="list-group-item">
              <strong>{{ user.username }}</strong>
              {% set public_notes = [] %}
              {% for note in user.notes %}
                {% if note.is_public %}
                  {% do public_notes.append(note) %}
                {% endif %}
              {% endfor %}
              {% if public_notes|length == 0 %}
                （无公开笔记）
              {% else %}
                <ul class="mt-2">
                  {% for note in public_notes %}
                    <li>
                      <a href="{{ url_for('view_others_note', user_id=user.id, note_id=note.id) }}">
                        {{ note.title }}
                      </a>
                    </li>
                  {% endfor %}
                </ul>
              {% endif %}
            </li>
          {% endfor %}
        </ul>
      {% endif %}
      <p class="mt-4"><a href="{{ url_for('notes') }}">返回我的笔记</a></p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
'''

# ----------------------------------
# 启动服务
# ----------------------------------
if __name__ == '__main__':
    db.create_all()
    app.run(debug=False)
