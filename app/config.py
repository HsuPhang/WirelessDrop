import os

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    # 取消文件大小限制（设置为非常大的值）
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024 * 1024  # 50GB
    
    # 允许所有文件类型（空集合表示不限制）
    ALLOWED_EXTENSIONS = set()  # 空集合表示允许所有文件类型
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
