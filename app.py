from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Bộ nhớ tạm để demo (nên thay bằng database trong dự án thực tế)
users = {}
posts = [
    {'id': 1, 'title': 'Bài viết mẫu 1'},
    {'id': 2, 'title': 'Bài viết mẫu 2'},
    # Thêm nhiều bài viết để kiểm tra phân trang
]

@app.route('/')
def home():
    return render_template('home.html', posts=posts)

# Release Version 2: Đăng nhập và đăng ký
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
        if user and user.get('password') == password:
            if user.get('blocked'):
                flash("Tài khoản của bạn đã bị khóa", 'error')
                return redirect(url_for('login'))
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Sai thông tin đăng nhập", 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            flash("Người dùng đã tồn tại", 'error')
        else:
            users[username] = {'password': password, 'blocked': False}
            flash("Đăng ký thành công, mời đăng nhập", 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Release Version 3: Trang admin quản lý user
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        if action == 'block' and username in users:
            users[username]['blocked'] = True
            flash(f"Đã khóa tài khoản của {username}", 'success')
        elif action == 'reset' and username in users:
            users[username]['password'] = 'defaultpassword'
            flash(f"Đã reset mật khẩu cho {username}", 'success')
    return render_template('admin.html', users=users)

# Release Version 4: Quản lý bài viết với xóa hàng loạt
@app.route('/posts', methods=['GET', 'POST'])
def manage_posts():
    global posts
    if request.method == 'POST':
        selected_posts = request.form.getlist('post_ids')
        posts = [post for post in posts if str(post['id']) not in selected_posts]
        flash("Đã xóa các bài viết được chọn", 'success')
    return render_template('posts.html', posts=posts)

# Release Version 5: Phân trang (pagination)
@app.route('/page/<int:page_num>')
def paginate(page_num):
    per_page = 10
    start = (page_num - 1) * per_page
    end = start + per_page
    paginated_posts = posts[start:end]
    return render_template('home.html', posts=paginated_posts, page=page_num)

if __name__ == '__main__':
    app.run(debug=True)
