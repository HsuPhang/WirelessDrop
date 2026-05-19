import logging
import sys
import os
import socket

# 添加当前目录到Python路径（正确做法）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 获取本地IP地址
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logging.error(f"Error getting local IP: {e}")
        return '127.0.0.1'

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting WirelessDrop application...")

# 输出本地IP地址
local_ip = get_local_ip()
print(f"\n====================================")
print(f"WirelessDrop 启动信息")
print(f"====================================")
print(f"本地IP地址: {local_ip}")
print(f"访问地址: http://{local_ip}:5000")
print(f"你可以在同一网络的任何设备上访问此地址")
print(f"====================================\n")
logger.info(f"Local access URL: http://{local_ip}:5000")

try:
    from app import create_app, socketio
    app = create_app()
    logger.info("Application created successfully")

    if __name__ == '__main__':
        logger.info("Running app on http://0.0.0.0:5000")
        # 修正：生产环境需关闭 debug 模式
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)

except Exception as e:
    # 修正：完整记录异常堆栈到日志
    logger.exception("Fatal error during startup:")
    print(f"启动失败: {e}")
    # 可选：紧急退出（避免运行不完整的服务）
    sys.exit(1)
