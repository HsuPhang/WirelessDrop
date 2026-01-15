import os
import sys
from flask import Flask
from flask_socketio import SocketIO


socketio = SocketIO(cors_allowed_origins="*")


def get_resource_path(relative_path):
    """ 处理 PyInstaller 的资源路径 """
    # 获取当前文件的绝对路径
    current_file = os.path.abspath(__file__)
    # 获取app包的父目录（即项目根目录）
    app_root = os.path.dirname(os.path.dirname(current_file))
    
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(app_root, relative_path)

def create_app():
    """ 创建并配置Flask应用 """
    template_dir = get_resource_path('templates')
    static_dir = get_resource_path('app/static')

    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)

    from .config import Config
    app.config.from_object(Config)

    # 确保上传目录存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from .routes import register_blueprints
    register_blueprints(app)

    socketio.init_app(app, cors_allowed_origins="*")

    return app