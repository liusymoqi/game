# config/logger_config.py
import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    # 创建logs目录
    log_dir = os.path.join(os.path.dirname(__file__), '../logs')
    os.makedirs(log_dir, exist_ok=True)

    # 基础配置
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器（按天滚动）
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        when='midnight',
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger