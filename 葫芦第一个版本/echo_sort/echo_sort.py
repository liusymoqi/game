# echo_sort/echo_sort.py
import time
import logging
from utils.game_controller import GameController
from PyQt5.QtWidgets import QMessageBox
from utils.image_tool import ImageTool
from echo_sort.open_backpack import open_backpack, switch_to_echo_tab, adjust_sort_order
from echo_sort.echo_data import read_echo_info, process_echo, second_echo, handle_echoes

# 初始化 logger
logger = logging.getLogger(__name__)

class EchoSorter:
    def __init__(self, ui_callback):
        # 初始化 GameController 实例，用于控制游戏窗口
        self.gc = GameController()
        # 标记整理流程是否正在运行
        self.running = False
        # 用于更新 UI 状态的回调函数
        self.ui_callback = ui_callback  

    def start_sorting(self, lock_rules, discard_rules):
        """完整的整理流程"""
        try:
            # 标记整理流程开始运行
            self.running = True
            logger.info("== 开始整理流程 ==")

            # 1. 激活游戏窗口
            if not self.gc.activate_game_window():
                self._show_error("无法连接到游戏窗口，请确保游戏已启动")
                return False

            # 2. 检查多人游戏图标
            if not self._check_game_ui_ready():
                self._show_error("未检测到游戏主界面")
                return False

            # 3. 打开背包
            logger.info("\n--- 正在尝试打开背包 ---")
            if not open_backpack(self.gc.image_tool):
                self._show_error("无法打开背包，请手动检查游戏状态")
                return False

            # 4. 切换到声骸背包
            logger.info("\n--- 正在验证背包类型 ---")
            if not switch_to_echo_tab(self.gc.image_tool):
                self._show_error("无法切换到声骸背包，请手动检查")
                return False

            # 5. 调整排序顺序
            logger.info("\n--- 正在验证排序方式 ---")
            if not adjust_sort_order(self.gc.image_tool):
                self._show_error("无法设置时间排序，请手动调整")
                return False

            # 6. 处理声骸
            if not handle_echoes(self.gc.image_tool, self.gc.echo_data, lock_rules, discard_rules):
                self._show_error("处理声骸时出错")
                return False

            return True
        except Exception as e:
            self._show_error(f"运行时错误: {str(e)}")
            return False

    def pause_sorting(self):
        """暂停整理"""
        self.running = False
        logger.info("== 整理已暂停 ==")

    def _check_game_ui_ready(self, timeout=10):
        """循环检测游戏界面准备状态"""
        for _ in range(timeout):
            if self.gc.image_tool.find_image(self.gc.multiplayer_icon):
                return True
            time.sleep(1)
        return False

    def _show_error(self, msg):
        """统一错误处理"""
        self.running = False
        logger.error(msg)  # 使用 logger 记录错误信息
        QMessageBox.critical(None, "运行错误", msg)
        self.ui_callback("error", msg)