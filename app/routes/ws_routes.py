from flask_socketio import emit
from flask import request

# 使用本地导入，因为ws_bp是在当前包的__init__.py中定义的
from . import ws_bp
from .. import socketio

# 存储连接的客户端信息
clients = {}

# WebSocket连接事件
@socketio.on('connect')
def handle_connect():
    # 获取客户端IP和用户代理
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    
    # 简化设备信息
    if 'Mobile' in user_agent or 'iPhone' in user_agent or 'Android' in user_agent:
        device_type = '移动端设备'
    else:
        device_type = '桌面设备'
    
    import time
    # 存储客户端信息
    clients[request.sid] = {
        'ip': client_ip,
        'user_agent': user_agent,
        'device_type': device_type,
        'connected_at': time.time()
    }
    
    # 广播连接消息
    emit('log', {
        'message': f'{device_type} ({client_ip}) 已连接',
        'level': 'success'
    }, to='*')

# WebSocket断开连接事件
@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in clients:
        client = clients[request.sid]
        # 广播断开连接消息
        emit('log', {
            'message': f'{client["device_type"]} ({client["ip"]}) 已断开连接',
            'level': 'info'
        }, to='*')
        # 移除客户端信息
        del clients[request.sid]

# 接收客户端消息事件
@socketio.on('message')
def handle_message(message):
    client = clients.get(request.sid, {'device_type': '未知设备', 'ip': '未知IP'})
    emit('log', {
        'message': f'{client["device_type"]} ({client["ip"]})：{message}',
        'level': 'info'
    }, to='*')

# 接收刷新文件列表事件
@socketio.on('refresh_files')
def handle_refresh_files():
    client = clients.get(request.sid, {'device_type': '未知设备', 'ip': '未知IP'})
    # 广播刷新文件列表消息给所有客户端（包括发送者）
    emit('refresh_files', to='*')
    # 记录日志
    emit('log', {
        'message': f'{client["device_type"]} ({client["ip"]}) 触发了文件列表刷新',
        'level': 'info'
    }, to='*')
