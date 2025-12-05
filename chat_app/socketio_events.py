from flask import session, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 初始化SocketIO
socketio = SocketIO()

# 延迟导入，避免循环导入问题
WeatherAPI = None
NewsAPI = None
MusicAPI = None
db = None
User = None
Message = None

def init_api_instances():
    """初始化API实例和数据库模型"""
    global WeatherAPI, NewsAPI, MusicAPI, db, User, Message
    from utils.weather import WeatherAPI as WeatherAPIClass
    from utils.news import NewsAPI as NewsAPIClass
    from utils.music import MusicAPI as MusicAPIClass
    from models import db as db_instance, User as UserModel, Message as MessageModel
    
    WeatherAPI = WeatherAPIClass()
    NewsAPI = NewsAPIClass()
    MusicAPI = MusicAPIClass()
    db = db_instance
    User = UserModel
    Message = MessageModel

# 初始化API实例
init_api_instances()

# 在线用户列表
online_users = {}

# API实例（直接使用init_api_instances中创建的全局对象）
weather_api = WeatherAPI
news_api = NewsAPI
music_api = MusicAPI

@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    if 'username' in session:
        username = session['username']
        online_users[username] = True
        
        # 更新在线用户列表
        update_online_users()
        
        # 记录连接日志
        print(f"用户 {username} 已连接")
        
        # 发送欢迎消息
        welcome_message = {
            'sender': {
                'username': '系统'
            },
            'content': f'欢迎 {username} 加入聊天室！',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'message_time': time.strftime('%H:%M:%S'),
            'type': 'system'
        }
        emit('new_message', welcome_message, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    if 'username' in session:
        username = session['username']
        if username in online_users:
            del online_users[username]
            
            # 更新在线用户列表
            update_online_users()
            
            # 记录断开日志
            print(f"用户 {username} 已断开连接")
            
            # 发送离开消息
            leave_message = {
                'sender': {
                    'username': '系统'
                },
                'content': f'{username} 已离开聊天室',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'message_time': time.strftime('%H:%M:%S'),
                'type': 'system'
            }
            emit('new_message', leave_message, broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    """处理用户发送的消息"""
    if 'username' not in session:
        return
    
    username = session['username']
    content = data.get('message', '')
    message_type = data.get('type', 'normal')
    
    if not content.strip():
        return
    
    # 检查是否包含@命令
    if content.startswith('@'):
        handle_at_command(content, username)
        return
    
    # 查找用户ID
    user = User.query.filter_by(username=username).first()
    
    # 保存消息到数据库
    message = Message(
        sender_id=user.id if user else None,
        username=username,
        content=content,
        type=message_type
    )
    db.session.add(message)
    db.session.commit()
    
    # 发送消息给所有客户端
    message_data = {
        'id': message.id,
        'sender': {
            'username': username
        },
        'content': content,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'message_time': time.strftime('%H:%M:%S'),
        'type': message_type
    }
    emit('new_message', message_data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    """处理用户输入状态"""
    if 'username' not in session:
        return
    
    username = session['username']
    is_typing = data.get('is_typing', False)
    
    emit('user_typing', {
        'username': username,
        'is_typing': is_typing
    }, broadcast=True, include_self=False)

def handle_at_command(content, username):
    """处理@命令"""
    command = content[1:].strip()
    parts = command.split(' ', 1)
    
    if not parts:
        return
    
    cmd_type = parts[0].lower()
    params = parts[1] if len(parts) > 1 else ''
    
    response_message = {
        'sender': {
            'username': '系统'
        },
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'message_time': time.strftime('%H:%M:%S'),
        'type': 'system'
    }
    
    # 处理不同的@命令
    if cmd_type == '天气' or cmd_type == 'weather':
        city = params.strip() if params else '北京'
        weather_data = weather_api.get_weather(city)
        
        if weather_data['success']:
            response_message['content'] = f"{city} 当前天气：{weather_data['description']}，温度 {weather_data['temperature']}°C"
            response_message['type'] = 'weather'
        else:
            response_message['content'] = f"无法获取 {city} 的天气信息：{weather_data['error']}"
    
    elif cmd_type == '新闻' or cmd_type == 'news':
        news_data = news_api.get_60s_news()
        
        if news_data['success']:
            # 构建新闻列表的HTML
            news_html = '<div class="news-list"><h6>每日60秒新闻</h6>'
            for news in news_data['news']:
                news_html += f'<div class="news-item"><h6>{news["title"]}</h6><p>{news["content"]}</p></div>'
            news_html += '</div>'
            response_message['content'] = news_html
            response_message['type'] = 'html'
        else:
            response_message['content'] = f"无法获取新闻信息：{news_data['error']}"
    
    elif cmd_type == '音乐' or cmd_type == 'music':
        if not params:
            response_message['content'] = '请输入要搜索的音乐名称，例如：@音乐 晴天'
            emit('new_message', response_message, broadcast=True)
            return
            
        search_result = music_api.search_music(params, limit=1)
        
        if search_result['success'] and search_result['songs']:
            song = search_result['songs'][0]
            card_result = music_api.generate_music_card(song['id'])
            
            if card_result['success']:
                response_message['content'] = f"{username} 分享了一首音乐：{song['title']} - {song['artist']}"
                response_message['type'] = 'html'
            else:
                response_message['content'] = f"无法生成音乐卡片：{card_result['error']}"
        else:
            response_message['content'] = f"未找到音乐 '{params}'"
    
    elif cmd_type == '电影' or cmd_type == 'movie':
        if not params:
            response_message['content'] = '请输入电影URL，例如：@电影 https://example.com/movie'
            emit('new_message', response_message, broadcast=True)
            return
        
        try:
            # 提取电影URL
            movie_url = params.strip()
            
            # 生成电影播放的iframe代码
            iframe_html = f'<iframe src="{movie_url}" width="400" height="400" frameborder="0" allowfullscreen></iframe>'
            response_message['content'] = iframe_html
            response_message['type'] = 'html'
        except Exception as e:
            response_message['content'] = f"无法处理电影URL：{str(e)}"
    
    elif cmd_type == '帮助' or cmd_type == 'help':
        help_content = '''
        可用命令：<br>
        @天气 [城市] - 查询指定城市的天气信息<br>
        @新闻 - 获取每日60秒新闻<br>
        @音乐 [歌曲名] - 搜索并播放音乐<br>
        @电影 [URL] - 播放指定URL的电影<br>
        @帮助 - 显示帮助信息<br>
        '''
        response_message['content'] = help_content
        response_message['type'] = 'html'
    
    else:
        response_message['content'] = f"未知命令：@{cmd_type}，使用 @帮助 查看可用命令"
    
    # 发送响应消息
    emit('new_message', response_message, broadcast=True)

@socketio.on('play_music')
def handle_play_music(data):
    """处理音乐播放请求"""
    song_id = data.get('song_id')
    if song_id:
        emit('music_play', {
            'song_id': song_id
        }, broadcast=True)

@socketio.on('pause_music')
def handle_pause_music(data):
    """处理音乐暂停请求"""
    song_id = data.get('song_id')
    if song_id:
        emit('music_pause', {
            'song_id': song_id
        }, broadcast=True)

@socketio.on('stop_music')
def handle_stop_music(data):
    """处理音乐停止请求"""
    song_id = data.get('song_id')
    if song_id:
        emit('music_stop', {
            'song_id': song_id
        }, broadcast=True)

@socketio.on('change_background')
def handle_change_background(data):
    """处理背景切换请求"""
    background_type = data.get('type')
    if background_type:
        emit('background_changed', {
            'type': background_type
        }, broadcast=True)

@socketio.on('get_online_users')
def handle_get_online_users():
    """处理获取在线用户列表请求"""
    update_online_users()

@socketio.on('update_profile')
def handle_update_profile(data):
    """处理用户资料更新"""
    if 'username' not in session:
        return
    
    username = session['username']
    new_avatar = data.get('avatar')
    
    # 这里可以添加更新用户头像的逻辑
    # 例如更新数据库中的用户头像信息
    
    # 广播用户资料更新
    emit('user_profile_updated', {
        'username': username,
        'avatar': new_avatar
    }, broadcast=True)

def update_online_users():
    """更新在线用户列表"""
    online_list = list(online_users.keys())
    emit('update_online_users', {
        'users': online_list,
        'count': len(online_list)
    }, broadcast=True)

def get_online_users():
    """获取在线用户列表"""
    return list(online_users.keys())
