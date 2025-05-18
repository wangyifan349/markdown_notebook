# 📔 Markdown Notebook

基于 Flask 的在线 Markdown 笔记本，支持用户注册登录，创建、编辑、查看 Markdown 格式笔记，支持搜索其他用户笔记并以最长公共子序列算法排序匹配。界面采用 Bootstrap 5 美化，适配手机和电脑端。✨

---

<p align="center">
  <img src="https://user-images.githubusercontent.com/yourgithub/yourproject/banner.png" alt="Markdown Notebook Banner" width="600" />
</p>

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

`markdown_notebook` 是一个简单易用的在线 Markdown 笔记记录平台。用户可以注册并登录自己的账号，随时在线创建和编辑笔记，笔记内容支持 Markdown 格式，界面清爽且响应式，兼容手机及桌面设备。📱💻

此外，用户可通过模糊搜索功能查找其他用户的笔记——搜索基于最长公共子序列（LCS）算法进行匹配，能够智能排序，更容易找到想要的用户。查看他人笔记时仅支持只读，确保数据安全。🔒

---

## 功能特点 🌟

- 👤 用户注册、登录、登出，密码安全哈希存储
- ✍️ 创建、编辑、删除（可扩展）Markdown 格式笔记
- 📋 笔记列表管理，支持快速查看和编辑
- 📖 Markdown 实时渲染查看，支持代码高亮及常用扩展
- 🔍 支持模糊搜索其他用户，根据最长公共子序列排序
- 📱 响应式设计，支持手机和电脑浏览
- 🎨 使用 Bootstrap 5 美化界面，用户体验良好

---

## 安装及运行 🚀

### 1. 克隆项目

```bash
git clone https://github.com/wangyifan349/markdown_notebook.git
cd markdown_notebook
```

### 2. 创建并激活虚拟环境（推荐）

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

> 如果没有 `requirements.txt`，请手动安装依赖：
>
> ```bash
> pip install flask flask_sqlalchemy markdown werkzeug
> ```

### 4. 运行项目 🏃‍♂️

```bash
python app.py
```

默认启动以后，浏览器打开：

```
http://127.0.0.1:5000
```

即可访问并使用。🌐

---

## 使用说明 📖

- 访问首页即可登录，如无账号可先注册 🆕
- 登录后，可创建、编辑和浏览你的 Markdown 笔记 ✍️
- 通过顶部导航进入用户搜索页面，输入关键词搜索其他用户的笔记，点击后查看只读内容 🔎
- 登出按钮在右上角，确保账户安全 🔐

---

## 依赖 📦

- Python 3.7+
- Flask >= 2.3.0
- Flask-SQLAlchemy >= 3.0.0
- Markdown >= 3.4.0
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
└── templates/       # （可选）自定义 HTML 模板文件夹
```

---

## 许可协议 🛡️

本项目使用 [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause) 许可。

BSD 3-Clause 许可证是一种宽松的开源许可证，允许你自由使用、复制、修改和分发本项目，包括用于商业用途，只要你遵守以下条件：

- 必须保留原作者的版权声明和许可条款。
- 不能使用原作者、贡献者的名字为衍生产品背书或推广，除非得到许可。
- 不提供任何形式的明示或暗示保证，使用风险自负。

详细条款请参考官方许可证链接。

---

## 作者信息 🙋‍♂️

- 作者：Wang Yifan  
- GitHub：[https://github.com/wangyifan349](https://github.com/wangyifan349)  
- 邮箱 wangyifan1999@protonmail.com

欢迎提出 Issues 或 Pull Requests，共同完善项目！🤝

