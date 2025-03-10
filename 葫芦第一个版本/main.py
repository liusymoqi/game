import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from config.logger_config import setup_logger

def load_styles():
    try:
        with open('ui/style.qss', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def main():
    # 初始化日志系统
    logger = setup_logger()
    logger.info("====== 应用程序启动 ======")
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion样式
    
    # 加载自定义样式
    style = load_styles()
    if style:
        app.setStyleSheet(style)
    
    window = MainWindow()
    window.setWindowTitle("葫芦 - 鸣潮工具集")
    window.setMinimumSize(800, 600)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":  
    main()