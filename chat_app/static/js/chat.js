// 聊天应用客户端代码

// 初始化Socket.IO
const socket = io();

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const onlineUsersList = document.getElementById('online-users-list');
    
    // 发送消息
    function sendMessage() {
        const message = messageInput.value.trim();
        
        if (message) {
            // 发送消息到服务器
            socket.emit('send_message', { message: message });
            
            // 清空输入框
            messageInput.value = '';
        }
    }
    
    // 点击发送按钮
    sendButton.addEventListener('click', sendMessage);
    
    // 回车键发送消息
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // 接收新消息
    socket.on('new_message', function(data) {
        if (data.type === 'html' || data.type === 'weather' || data.type === 'news' || data.type === 'music') {
            addHtmlMessage(data.sender.username, data.content, data.message_time);
        } else {
            addMessage(data.sender.username, data.content, data.message_time);
        }
    });
    
    // 接收在线用户列表更新
    socket.on('update_online_users', function(data) {
        updateOnlineUsersList(data.users);
    });
    
    // 添加HTML消息到聊天区域（用于电影播放等）
    function addHtmlMessage(username, htmlContent, time) {
        const messageItem = document.createElement('div');
        messageItem.className = 'message-item';
        
        messageItem.innerHTML = `
            <div class="message-header">
                <span class="message-username">${username}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">${htmlContent}</div>
        `;
        
        chatMessages.appendChild(messageItem);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // 添加普通消息到聊天区域
    function addMessage(username, message, time) {
        const messageItem = document.createElement('div');
        messageItem.className = 'message-item';
        
        messageItem.innerHTML = `
            <div class="message-header">
                <span class="message-username">${username}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">${message}</div>
        `;
        
        chatMessages.appendChild(messageItem);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // 添加HTML消息到聊天区域（用于电影播放、新闻、音乐等）
    function addHtmlMessage(username, htmlContent, time) {
        const messageItem = document.createElement('div');
        messageItem.className = 'message-item';
        
        messageItem.innerHTML = `
            <div class="message-header">
                <span class="message-username">${username}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">${htmlContent}</div>
        `;
        
        chatMessages.appendChild(messageItem);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // 更新在线用户列表
    function updateOnlineUsersList(users) {
        onlineUsersList.innerHTML = '';
        
        users.forEach(username => {
            const userItem = document.createElement('div');
            userItem.className = 'user-item';
            userItem.innerHTML = `
                <i class="fa fa-circle online-status"></i>
                <span>${username}</span>
            `;
            onlineUsersList.appendChild(userItem);
        });
    }
    

    
    // 显示通知
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show';
        notification.role = 'alert';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // 添加到聊天消息区域
        chatMessages.appendChild(notification);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 3秒后自动关闭通知
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

// 音乐播放功能（全局函数，供音乐卡片调用）
let audio = null;

function playMusic(url) {
    if (audio) {
        audio.pause();
    }
    audio = new Audio(url);
    audio.play();
}

function pauseMusic() {
    if (audio) {
        audio.pause();
    }
}

function stopMusic() {
    if (audio) {
        audio.pause();
        audio.currentTime = 0;
    }
}
