import { formatFileSize, formatTime, showMessage, getFileIcon, initDarkMode, toggleDarkMode, copyToClipboard } from './utils.js';

// 全局变量
let socket;
let fileList = [];
let isUploading = false;

// DOM元素
const elements = {
    dropZone: document.querySelector('.drop-zone'),
    fileInput: document.querySelector('.file-input'),
    fileInputLabel: document.querySelector('.file-input-label'),
    progressContainer: document.querySelector('.progress-container'),
    progressBar: document.querySelector('.progress-fill'),
    progressText: document.querySelector('.progress-text'),
    filesContainer: document.querySelector('.files-container'),
    logsContainer: document.querySelector('.logs-container'),
    modeToggle: document.querySelector('.mode-toggle'),
    qrCodeLink: document.querySelector('.qr-code-link')
};

// 初始化函数
function init() {
    // 初始化深色模式
    initDarkMode();
    
    // 初始化WebSocket
    initWebSocket();
    
    // 初始化事件监听器
    initEventListeners();
    
    // 加载文件列表
    loadFileList();
    
    // 初始化拖放功能
    initDragAndDrop();
}

// 初始化WebSocket连接
function initWebSocket() {
    // 获取当前页面的协议和主机
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}`;
    
    socket = io.connect(wsUrl);
    
    // 连接成功事件
    socket.on('connect', () => {
        addLog('WebSocket连接成功', 'success');
    });
    
    // 连接断开事件
    socket.on('disconnect', () => {
        addLog('WebSocket连接断开', 'error');
        // 尝试重连
        setTimeout(initWebSocket, 3000);
    });
    
    // 接收日志事件
    socket.on('log', (data) => {
        addLog(data.message, data.level);
    });
    
    // 接收刷新文件列表事件
    socket.on('refresh_files', () => {
        loadFileList();
        addLog('文件列表已更新', 'info');
    });
    
    // 错误事件
    socket.on('error', (error) => {
        addLog(`WebSocket错误: ${error}`, 'error');
    });
}

// 初始化事件监听器
function initEventListeners() {
    // 深色模式切换
    if (elements.modeToggle) {
        elements.modeToggle.addEventListener('click', toggleDarkMode);
    }
    
    // 文件输入变化事件（兼容移动端）
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
        // 添加input事件监听，确保在移动端也能触发
        elements.fileInput.addEventListener('input', handleFileSelect);
    }
    
    // 文件输入标签点击事件
    if (elements.fileInputLabel) {
        elements.fileInputLabel.addEventListener('click', () => {
            if (elements.fileInput) {
                elements.fileInput.click();
            }
        });
    }
    
    // QR码链接复制事件
    if (elements.qrCodeLink) {
        elements.qrCodeLink.addEventListener('click', (e) => {
            e.preventDefault();
            const url = elements.qrCodeLink.href;
            copyToClipboard(url).then(success => {
                if (success) {
                    showMessage('链接已复制到剪贴板', 'success');
                } else {
                    showMessage('复制失败，请手动复制', 'error');
                }
            });
        });
    }
}

// 初始化拖放功能
function initDragAndDrop() {
    if (!elements.dropZone) return;
    
    // 拖放事件处理
    elements.dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.dropZone.classList.add('dragover');
    });
    
    elements.dropZone.addEventListener('dragleave', () => {
        elements.dropZone.classList.remove('dragover');
    });
    
    elements.dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.dropZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            const files = Array.from(e.dataTransfer.files);
            uploadFiles(files);
        }
    });
    
    // 点击拖放区域选择文件
    elements.dropZone.addEventListener('click', () => {
        if (elements.fileInput) {
            elements.fileInput.click();
        }
    });
}

// 处理文件选择
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        uploadFiles(files);
        // 清除文件输入的value，允许用户再次选择相同的文件
        e.target.value = '';
    }
}

// 上传文件
function uploadFiles(files) {
    if (isUploading) {
        showMessage('当前有文件正在上传，请稍后再试', 'warning');
        return;
    }
    
    isUploading = true;
    let uploadCount = 0;
    const totalFiles = files.length;
    
    files.forEach(file => {
        uploadFile(file, () => {
            uploadCount++;
            if (uploadCount === totalFiles) {
                isUploading = false;
                hideProgress();
            }
        });
    });
}

// 单个文件上传
function uploadFile(file, onComplete) {
    const formData = new FormData();
    formData.append('file', file);
    
    // 创建XHR对象（兼容移动端）
    const xhr = new XMLHttpRequest();
    
    // 设置超时时间（10分钟，适应大文件）
    xhr.timeout = 600000;
    
    // 显示进度条
    showProgress();
    
    // 更新进度
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            updateProgress(percentComplete, file.name);
        }
    });
    
    // 上传完成
    xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    showMessage(`文件上传成功: ${file.name}`, 'success');
                    loadFileList(); // 重新加载文件列表
                    // 发送WebSocket消息，通知所有客户端刷新文件列表
                    socket.emit('refresh_files');
                } else {
                    showMessage(`文件上传失败: ${response.error}`, 'error');
                }
            } catch (error) {
                showMessage(`文件上传成功，但解析响应失败: ${file.name}`, 'warning');
                loadFileList();
                socket.emit('refresh_files');
            }
        } else {
            showMessage(`文件上传失败: HTTP ${xhr.status}`, 'error');
        }
        
        onComplete();
    });
    
    // 上传错误
    xhr.addEventListener('error', () => {
        showMessage(`文件上传错误: ${file.name}`, 'error');
        onComplete();
    });
    
    // 上传超时
    xhr.addEventListener('timeout', () => {
        showMessage(`文件上传超时: ${file.name}`, 'error');
        onComplete();
    });
    
    // 发送请求
    xhr.open('POST', '/upload');
    // 添加请求头，确保移动端正确处理
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.send(formData);
}

// 显示进度条
function showProgress() {
    if (elements.progressContainer) {
        elements.progressContainer.classList.add('visible');
    }
}

// 隐藏进度条
function hideProgress() {
    if (elements.progressContainer) {
        elements.progressContainer.classList.remove('visible');
        updateProgress(0, '');
    }
}

// 更新进度条
function updateProgress(percent, filename) {
    if (elements.progressBar) {
        elements.progressBar.style.width = `${percent}%`;
    }
    
    if (elements.progressText) {
        elements.progressText.textContent = filename 
            ? `${filename} - ${percent.toFixed(1)}%` 
            : '';
    }
}

// 加载文件列表
function loadFileList() {
    fetch('/files')
        .then(response => response.json())
        .then(data => {
            fileList = data;
            renderFileList();
        })
        .catch(error => {
            console.error('加载文件列表失败:', error);
            addLog('加载文件列表失败', 'error');
        });
}

// 渲染文件列表
function renderFileList() {
    if (!elements.filesContainer) return;
    
    elements.filesContainer.innerHTML = '';
    
    if (fileList.length === 0) {
        elements.filesContainer.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px;">暂无文件</div>';
        return;
    }
    
    fileList.forEach(file => {
        const fileElement = createFileElement(file);
        elements.filesContainer.appendChild(fileElement);
    });
}

// 截断文件名，保留后缀名
function truncateFileName(filename, maxLength = 25) {
    if (filename.length <= maxLength) {
        return filename;
    }
    
    const parts = filename.split('.');
    if (parts.length <= 1) {
        // 没有后缀名，直接截断
        return filename.substring(0, maxLength) + '...';
    }
    
    const extension = parts.pop();
    const name = parts.join('.');
    const extensionLength = extension.length + 1; // +1 for the dot
    
    // 确保至少保留文件名的前几个字符和后缀名
    const maxNameLength = maxLength - extensionLength - 3; // -3 for the ellipsis
    if (maxNameLength <= 0) {
        // 如果后缀名太长，只显示后缀名
        return '...' + filename.substring(filename.length - maxLength);
    }
    
    return name.substring(0, maxNameLength) + '...' + '.' + extension;
}

// 创建文件元素
function createFileElement(file) {
    const div = document.createElement('div');
    div.className = 'file-item';
    
    const extension = file.name.split('.').pop().toLowerCase();
    const icon = getFileIcon(extension);
    const truncatedName = truncateFileName(file.name);
    
    div.innerHTML = `
        <div class="file-info">
            <div class="file-icon">${icon}</div>
            <div class="file-details">
                <div class="file-name" title="${file.name}">${truncatedName}</div>
                <div class="file-meta">
                    ${file.size} • ${formatTime(file.mtime)}
                </div>
            </div>
        </div>
        <div class="file-actions">
            <button class="action-btn download-btn" title="下载" onclick="downloadFile('${file.name}')">
                ⬇️
            </button>
            <button class="action-btn delete-btn" title="删除" onclick="deleteFile('${file.name}')">
                🗑️
            </button>
        </div>
    `;
    
    return div;
}

// 下载文件
function downloadFile(filename) {
    window.location.href = `/download/${filename}`;
}

// 删除文件
function deleteFile(filename) {
    if (confirm(`确定要删除文件 "${filename}" 吗？`)) {
        fetch(`/delete/${filename}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(`文件删除成功: ${filename}`, 'success');
                loadFileList(); // 重新加载文件列表
            } else {
                showMessage(`文件删除失败: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('删除文件失败:', error);
            showMessage('删除文件失败', 'error');
        });
    }
}

// 添加日志条目
function addLog(message, level = 'info') {
    if (!elements.logsContainer) return;
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${level}`;
    
    const timestamp = new Date().toLocaleTimeString('zh-CN');
    
    logEntry.innerHTML = `
        <span class="log-timestamp">${timestamp}</span>
        <span class="log-message">${message}</span>
    `;
    
    // 添加到日志容器
    elements.logsContainer.appendChild(logEntry);
    
    // 滚动到底部
    elements.logsContainer.scrollTop = elements.logsContainer.scrollHeight;
    
    // 限制日志条目数量（最多100条）
    const logEntries = elements.logsContainer.querySelectorAll('.log-entry');
    if (logEntries.length > 100) {
        logEntries[0].remove();
    }
}

// 绑定全局函数（供HTML调用）
window.downloadFile = downloadFile;
window.deleteFile = deleteFile;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
