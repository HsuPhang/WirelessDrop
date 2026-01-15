// 前端工具函数库

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 格式化时间戳
 * @param {number} timestamp - 时间戳
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * 生成唯一ID
 * @returns {string} 唯一ID
 */
export function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * 显示状态消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型（success, error, warning, info）
 * @param {number} duration - 显示时长（毫秒）
 */
export function showMessage(message, type = 'info', duration = 3000) {
    const messageElement = document.createElement('div');
    messageElement.className = `status-message ${type}`;
    messageElement.textContent = message;
    
    // 添加到页面
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(messageElement, container.firstChild);
        
        // 自动移除
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, duration);
    }
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 检查文件类型是否允许
 * @param {string} filename - 文件名
 * @param {Array} allowedTypes - 允许的文件类型数组
 * @returns {boolean} 是否允许
 */
export function isAllowedFileType(filename, allowedTypes) {
    const ext = filename.split('.').pop().toLowerCase();
    return allowedTypes.includes(ext);
}

/**
 * 获取文件扩展名
 * @param {string} filename - 文件名
 * @returns {string} 文件扩展名
 */
export function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

/**
 * 获取文件类型图标
 * @param {string} extension - 文件扩展名
 * @returns {string} 图标类名
 */
export function getFileIcon(extension) {
    const iconMap = {
        'txt': '📄',
        'pdf': '📑',
        'png': '🖼️',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'gif': '🖼️',
        'zip': '📦',
        'rar': '📦',
        '7z': '📦',
        'doc': '📝',
        'docx': '📝',
        'xls': '📊',
        'xlsx': '📊',
        'ppt': '📋',
        'pptx': '📋',
        'mp4': '🎬',
        'mp3': '🎵',
        'avi': '🎬'
    };
    return iconMap[extension] || '📄';
}

/**
 * 切换深色/浅色模式
 */
export function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('light-mode');
    
    // 保存设置到localStorage
    const isLightMode = body.classList.contains('light-mode');
    localStorage.setItem('darkMode', !isLightMode);
    
    // 更新按钮文本
    const toggleBtn = document.querySelector('.mode-toggle');
    if (toggleBtn) {
        toggleBtn.textContent = isLightMode ? '切换到深色模式' : '切换到浅色模式';
    }
}

/**
 * 初始化深色模式
 */
export function initDarkMode() {
    // 从localStorage获取设置，默认为深色模式
    const isDarkMode = localStorage.getItem('darkMode') !== 'false';
    if (!isDarkMode) {
        document.body.classList.add('light-mode');
    }
    
    // 更新按钮文本
    const toggleBtn = document.querySelector('.mode-toggle');
    if (toggleBtn) {
        toggleBtn.textContent = isDarkMode ? '切换到浅色模式' : '切换到深色模式';
    }
}

/**
 * 平滑滚动到元素
 * @param {HTMLElement} element - 目标元素
 * @param {number} duration - 滚动时长（毫秒）
 */
export function scrollToElement(element, duration = 300) {
    const targetPosition = element.offsetTop;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }
    
    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<boolean>} 是否复制成功
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('复制失败:', err);
        return false;
    }
}

/**
 * 检查是否支持拖放
 * @returns {boolean} 是否支持拖放
 */
export function isDragAndDropSupported() {
    return 'draggable' in document.createElement('div') && 
           'ondragstart' in document.createElement('div') && 
           'ondrop' in document.createElement('div');
}

/**
 * 显示加载指示器
 * @param {HTMLElement} container - 容器元素
 */
export function showLoader(container) {
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.innerHTML = '<div class="spinner"></div>';
    container.appendChild(loader);
}

/**
 * 隐藏加载指示器
 * @param {HTMLElement} container - 容器元素
 */
export function hideLoader(container) {
    const loader = container.querySelector('.loader');
    if (loader) {
        loader.remove();
    }
}
