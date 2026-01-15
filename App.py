import logging
import sys
import os

# 添加当前目录到Python路径（正确做法）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting WirelessDrop application...")

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
    # 可选：紧急退出（避免运行不完整的服务）
    sys.exit(1)
