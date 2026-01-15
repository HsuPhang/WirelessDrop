from flask import request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
import os

# 使用本地导入，因为file_bp是在当前包的__init__.py中定义的
from . import file_bp
from ..utils.file_utils import allowed_file, format_file_size
from ..utils.log_utils import push_log
from .. import socketio

# 获取客户端设备信息
def get_device_info():
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    if 'Mobile' in user_agent or 'iPhone' in user_agent or 'Android' in user_agent:
        device_type = '移动端设备'
    else:
        device_type = '桌面设备'
    return f'{device_type} ({client_ip})'

# 文件上传路由
@file_bp.route('/upload', methods=['POST'])
def upload_file():
    device_info = get_device_info()
    
    if 'file' not in request.files:
        push_log('错误：请求中没有文件部分', 'error', device_info)
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        push_log('错误：没有选择文件', 'error', device_info)
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # 获取文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        # 保存文件
        file.save(file_path)
        
        push_log(f'文件上传成功：{filename} ({format_file_size(file_size)})', 'success', device_info)
        # 广播刷新文件列表
        socketio.emit('refresh_files', to='*')
        return jsonify({'success': True, 'filename': filename, 'size': format_file_size(file_size)})
    else:
        push_log(f'错误：不允许的文件类型 - {file.filename}', 'error', device_info)
        return jsonify({'error': 'File type not allowed'}), 400

# 文件列表路由
@file_bp.route('/files', methods=['GET'])
def get_files():
    files = []
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                file_stats = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': format_file_size(file_stats.st_size),
                    'mtime': file_stats.st_mtime,
                    'full_size': file_stats.st_size
                })
    
    # 按修改时间排序（最新在前）
    files.sort(key=lambda x: x['mtime'], reverse=True)
    
    return jsonify(files)

# 文件下载路由
@file_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    device_info = get_device_info()
    try:
        push_log(f'文件下载：{filename}', 'info', device_info)
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        push_log(f'文件下载错误：{filename} - {str(e)}', 'error', device_info)
        return jsonify({'error': 'File not found'}), 404

# 文件删除路由
@file_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    device_info = get_device_info()
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))
    
    if os.path.exists(file_path):
        os.remove(file_path)
        push_log(f'文件删除成功：{filename}', 'success', device_info)
        # 广播刷新文件列表
        socketio.emit('refresh_files', to='*')
        return jsonify({'success': True})
    else:
        push_log(f'错误：文件不存在 - {filename}', 'error', device_info)
        return jsonify({'error': 'File not found'}), 404

# 新建目录路由
@file_bp.route('/mkdir', methods=['POST'])
def create_directory():
    device_info = get_device_info()
    data = request.get_json()
    dir_name = data.get('dir_name')
    
    if not dir_name:
        push_log('错误：目录名不能为空', 'error', device_info)
        return jsonify({'error': 'Directory name is required'}), 400
    
    dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(dir_name))
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        push_log(f'目录创建成功：{dir_name}', 'success', device_info)
        # 广播刷新文件列表
        socketio.emit('refresh_files', to='*')
        return jsonify({'success': True})
    else:
        push_log(f'错误：目录已存在 - {dir_name}', 'error', device_info)
        return jsonify({'error': 'Directory already exists'}), 400
