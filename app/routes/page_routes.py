from flask import render_template, current_app
import socket
import os

# 使用本地导入，因为page_bp是在当前包的__init__.py中定义的
from . import page_bp

# 获取本地IP地址
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

# 首页路由
@page_bp.route('/')
def index():
    local_ip = get_local_ip()
    return render_template('index.html', local_ip=local_ip)

# 旧上传页路由
@page_bp.route('/old-upload')
def old_upload():
    local_ip = get_local_ip()
    return render_template('upload.html', local_ip=local_ip)
