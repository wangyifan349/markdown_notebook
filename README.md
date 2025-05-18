# 📔 Markdown Notebook

基于 Flask 的在线 Markdown 笔记本，支持用户注册登录，创建、编辑、查看 Markdown 格式笔记，支持笔记公开权限设置。搜索其他用户笔记使用匹配相似度的算法模糊匹配排序。

界面采用 Bootstrap 5 美化，适配手机和电脑端，支持代码高亮及数学公式渲染。✨

---

## 目录 📚

- [项目简介](#项目简介)  
- [功能特点](#功能特点)  
- [安装及运行](#安装及运行)  
- [使用说明](#使用说明)  
- [依赖](#依赖)  
- [项目结构](#项目结构)  
- [许可协议](#许可协议)  
- [作者信息](#作者信息)  

---

## 项目简介 📝

`markdown_notebook` 是一个简单易用的在线 Markdown 笔记平台。用户可以注册登录，随时在线创建和编辑笔记，支持 Markdown 格式，且界面清爽响应，兼容手机及桌面设备。📱💻

用户可为每篇笔记设置“公开”权限。公开的笔记允许被其他用户搜索并查看，私密笔记仅本人访问，确保隐私安全。🔒

搜索功能支持根据用户名进行模糊匹配，基于最长公共子序列（LCS）算法排序，为你智能找人。查看他人公开笔记时，仅允许只读模式。📖

笔记内容支持代码语法高亮及数学公式（LaTeX）渲染，满足丰富书写需求。🎉

---

## 功能特点 🌟

- 👤 用户注册、登录、登出，密码哈希安全存储
- ✍️ 创建、编辑 Markdown 格式笔记，支持设置是否公开
- 🗃️ 笔记列表管理，清晰区分公开与私密
- 📖 Markdown 实时渲染查看，支持代码高亮和 MathJax 数学公式
- 🔍 用户名模糊搜索，基于最长公共子序列算法智能排序
- 🔐 只允许访问公开笔记或本人笔记，保护隐私安全
- 📱 响应式设计，支持手机和桌面浏览
- 🎨 Bootstrap 5 美观界面与交互体验

---

## 安装及运行 🚀

### 1. 克隆项目

```bash
git clone https://github.com/wangyifan349/markdown_notebook.git
cd markdown_notebook
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> 若无 `requirements.txt`，可手动安装：

```bash
pip install flask flask_sqlalchemy markdown pygments
```

### 3. 运行项目

```bash
python app.py
```

默认启动后，打开浏览器访问：

```
http://127.0.0.1:5000
```

即可开始使用。🌐

---

## 使用说明 📖

- 注册账号后登录，进入 “我的笔记” 页面管理笔记
- 创建新笔记时，可以填写标题、内容（支持 Markdown）及是否公开
- 编辑笔记界面同样支持修改公开状态
- 公开笔记其他用户可通过搜索用户名结果中查看（只读）
- 私密笔记仅本人可见，不会出现在搜索结果中
- 搜索页面输入用户名关键字，可智能推荐匹配用户及其公开笔记
- 退出登录保证账户安全

---

## 依赖 📦

- Python 3.7+
- Flask >= 2.3.0
- Flask-SQLAlchemy >= 3.0.0
- Markdown >= 3.4.0
- Pygments >= 2.15.1
- Werkzeug >= 2.3.0
- MarkupSafe >= 2.1.0
- Jinja2 >= 3.1.0
- itsdangerous >= 2.1.0
- click >= 8.0.0

---

## 项目结构（示例）📁

```
markdown_notebook/
├── app.py           # Flask 应用主文件
├── requirements.txt # 依赖列表
├── README.md        # 项目说明（本文件）
├── notes_auth.db    # SQLite 数据库文件（首次运行自动生成）
└── templates/       # （可选）HTML 模板文件夹，如非模板字符串方式
```

---

## 许可协议 🛡️

本项目遵循 [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause)。

该许可允许你自由使用、修改和分发本项目（包含商业用途），条件是：

- 保留版权声明和许可条款
- 不得用原作者名义为衍生产品背书或推广，除非得到授权
- 无任何形式保证，风险自负

详情请阅读许可证文本。

---

## 作者信息 🙋‍♂️

- 作者：Wang Yifan  
- GitHub：[https://github.com/wangyifan349](https://github.com/wangyifan349)  
- 邮箱：wangyifan1999@protonmail.com

欢迎提交 Issue 和 Pull Request，一起完善项目！🤝
