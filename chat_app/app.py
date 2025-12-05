from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from models import db, User, Message, init_db
# 导入socketio实例
from socketio_events import socketio

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(config['development'])

# 初始化数据库
db.init_app(app)
init_db(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 设置登录页面的路由
login_manager.login_message = '请先登录'

# 初始化SocketIO
socketio.init_app(app)

# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    """根据用户ID加载用户"""
    return User.query.get(int(user_id))

# 路由定义

@app.route('/')
def index():
    """首页，重定向到登录页面"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 查询用户
        user = User.query.filter_by(username=username).first()
        
        if user and user.verify_password(password):
            # 登录成功
            login_user(user)
            user.update_login_status(is_online=True)
            flash('登录成功', 'success')
            return redirect(url_for('chat'))
        else:
            # 登录失败
            flash('用户名或密码错误', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # 表单验证
        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('register'))
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))
        
        # 创建新用户
        new_user = User(username=username)
        new_user.password = password
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'注册失败：{str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """退出登录"""
    current_user.update_login_status(is_online=False)
    logout_user()
    flash('已退出登录', 'success')
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    """聊天页面"""
    # 获取所有在线用户
    online_users_list = User.query.filter_by(is_online=True).all()
    
    # 获取消息历史记录
    messages = Message.query.order_by(Message.created_at).all()
    
    return render_template('chat.html', online_users=online_users_list, messages=messages)



# 主函数
if __name__ == '__main__':
    # 运行应用
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
