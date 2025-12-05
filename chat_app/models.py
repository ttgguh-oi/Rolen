from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# 初始化数据库
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户数据模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_online = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    @property
    def password(self):
        """获取密码（只读，实际返回错误）"""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """设置密码，生成哈希值"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_login_status(self, is_online=True):
        """更新登录状态"""
        self.is_online = is_online
        if is_online:
            self.last_login = datetime.datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        """用户对象的字符串表示"""
        return f'<User {self.username}>'

class Message(db.Model):
    """消息数据模型"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 允许空（系统消息）
    username = db.Column(db.String(80), nullable=False)  # 直接存储用户名（用于系统消息）
    type = db.Column(db.String(20), default='normal')  # 消息类型：normal, system, weather, news, music
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # 关系
    sender = db.relationship('User', backref=db.backref('messages', lazy=True))
    
    def __repr__(self):
        """消息对象的字符串表示"""
        return f'<Message {self.id} from {self.username}>'

# 数据库初始化函数
def init_db(app):
    """初始化数据库"""
    with app.app_context():
        db.create_all()
