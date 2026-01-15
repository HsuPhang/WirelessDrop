import os
from flask import current_app

# 检查文件类型是否允许
def allowed_file(filename):
    # 如果ALLOWED_EXTENSIONS为空集合，允许所有文件类型
    if not current_app.config['ALLOWED_EXTENSIONS']:
        return True
    # 否则检查文件扩展名是否在允许列表中
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# 安全处理文件名已直接从werkzeug导入，此函数保留用于向后兼容
def secure_filename(filename):
    from werkzeug.utils import secure_filename as werkzeug_secure_filename
    return werkzeug_secure_filename(filename)

# 格式化文件大小
def format_file_size(size_bytes):
    """将字节大小格式化为人类可读的形式"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

# 获取文件扩展名
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

# 获取文件类型图标
def get_file_icon(extension):
    """根据文件扩展名返回对应的图标类名"""
    icon_map = {
        '.txt': 'file-text',
        '.pdf': 'file-pdf',
        '.png': 'file-image',
        '.jpg': 'file-image',
        '.jpeg': 'file-image',
        '.gif': 'file-image',
        '.zip': 'file-zip',
        '.rar': 'file-zip',
        '.7z': 'file-zip',
        '.doc': 'file-word',
        '.docx': 'file-word',
        '.xls': 'file-excel',
        '.xlsx': 'file-excel',
        '.ppt': 'file-powerpoint',
        '.pptx': 'file-powerpoint',
        '.mp4': 'file-video',
        '.mp3': 'file-audio',
        '.avi': 'file-video'
    }
    return icon_map.get(extension, 'file')
