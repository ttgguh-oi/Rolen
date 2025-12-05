# 聊天应用项目结构

## 项目概述
一个基于Flask和Socket.IO的实时聊天应用，支持@功能（天气查询、新闻获取、音乐播放）和完整的用户系统。

## 技术栈
- 后端：Flask + Socket.IO + SQLite
- 前端：HTML + CSS + JavaScript + Bootstrap
- API：天气API、新闻API、音乐API

## 项目结构
```
chat_app/
├── app.py              # 主应用文件
├── config.py           # 配置文件
├── models.py           # 数据模型
├── requirements.txt    # 依赖列表
├── static/             # 静态文件
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── chat.js
│   └── images/
├── templates/          # 模板文件
│   ├── login.html
│   ├── register.html
│   └── chat.html
└── utils/              # 工具函数
    ├── weather.py
    ├── news.py
    └── music.py
```

## 功能模块

### 1. 用户系统
- 注册：用户名、密码验证
- 登录：身份认证
- 状态管理：上线/下线状态
- 用户数据管理：SQLite存储

### 2. 聊天功能
- 实时消息发送/接收
- 消息历史记录
- 用户列表显示

### 3. @功能
- @天气：查询指定城市天气，同步修改聊天背景
- @60s新闻：获取每日60秒新闻，以图文列表呈现
- @音乐：搜索并播放音乐，生成音乐卡片同步给所有用户
