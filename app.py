from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'secret-key-random'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='user', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=10)
    posts = pagination.items
    return render_template('index.html', user=current_user(), posts=posts, pagination=pagination)


# Cập nhật route post_detail: Nếu chưa đăng nhập, flash thông báo và chuyển hướng sang trang login
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    if not current_user():
        flash("Bạn hãy đăng nhập để xem chi tiết bài viết.")
        return redirect(url_for('login'))
    post = Post.query.get_or_404(post_id)
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('post_detail.html', post=post, posts=posts, user=current_user())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Mật khẩu và xác nhận mật khẩu không khớp!")
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại!")
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công, hãy đăng nhập.")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.is_blocked:
                flash('Tài khoản của bạn đã bị khóa!')
                return redirect(url_for('login'))
            session['user_id'] = user.id
            flash('Đăng nhập thành công!')
            return redirect(url_for('home'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Bạn đã đăng xuất.')
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('home'))
    if user.is_blocked:
        flash('Tài khoản của bạn đã bị khóa!')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin.html', user=user, users=users)

@app.route('/admin/block_user/<int:user_id>')
def block_user(user_id):
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('home'))
    target_user = User.query.get_or_404(user_id)
    target_user.is_blocked = True
    db.session.commit()
    flash(f'Đã khóa user {target_user.username}.')
    return redirect(url_for('admin'))

@app.route('/admin/unblock_user/<int:user_id>')
def unblock_user(user_id):
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('home'))
    target_user = User.query.get_or_404(user_id)
    target_user.is_blocked = False
    db.session.commit()
    flash(f'Đã mở khóa user {target_user.username}.')
    return redirect(url_for('admin'))

@app.route('/admin/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = current_user()
    if not user or not user.is_admin:
        flash('Bạn không có quyền.')
        return redirect(url_for('home'))
    if user.is_blocked:
        return redirect(url_for('home'))
    target_user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_password = request.form['new_password']
        target_user.password = generate_password_hash(new_password)
        db.session.commit()
        flash(f'Đã đổi mật khẩu cho {target_user.username}.')
        return redirect(url_for('admin'))
    return render_template('reset_password.html', target_user=target_user)

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập để xem nội dung này.')
        return redirect(url_for('login'))
    if not user.is_admin:
        flash('Bạn không có quyền truy cập trang này.')
        return redirect(url_for('home'))
    if user.is_blocked:
        return redirect(url_for('home'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form.get('image_url', '')
        new_post = Post(title=title, content=content, image_url=image_url, user_id=user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Tạo bài viết thành công.')
        return redirect(url_for('posts'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(user_id=user.id).paginate(page=page, per_page=10)
    user_posts = pagination.items
    return render_template('posts.html', user=user, posts=user_posts, pagination=pagination)

@app.route('/delete_posts', methods=['POST'])
def delete_posts():
    user = current_user()
    if not user:
        flash('Bạn cần đăng nhập.')
        return redirect(url_for('login'))
    post_ids = request.form.getlist('post_ids')
    for pid in post_ids:
        post = Post.query.get(pid)
        if post and post.user_id == user.id:
            db.session.delete(post)
    db.session.commit()
    flash('Đã xóa các bài viết được chọn.')
    return redirect(url_for('posts'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='ben2xx4').first():
            admin_user = User(
                username='ben2xx4',
                password=generate_password_hash('ben2xx4'),
                is_admin=True,
                is_blocked=False
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
