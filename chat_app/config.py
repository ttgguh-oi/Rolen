import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'  # 密钥
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'chat_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API配置（示例，实际使用时需替换为真实API密钥）
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY') or 'your-weather-api-key'
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or 'your-news-api-key'
    MUSIC_API_KEY = os.environ.get('MUSIC_API_KEY') or 'your-music-api-key'
    
    # 其他配置
    DEBUG = True
    TESTING = False

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True

# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

# 测试环境配置
class TestingConfig(Config):
    TESTING = True

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
