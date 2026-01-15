import datetime

# 使用相对导入
from .. import socketio

def push_log(message, level='info', device_info='服务器'):
    """推送日志到所有连接的WebSocket客户端"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_data = {
        'timestamp': timestamp,
        'message': f'[{device_info}] {message}',
        'level': level
    }
    socketio.emit('log', log_data, to='*')
