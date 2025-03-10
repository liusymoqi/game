import os
import random
import win32gui
import win32con
import pyautogui
import time
import re
import logging
from utils.image_tool import ImageTool
import cv2
import json
from echo_sort.open_backpack import open_backpack, switch_to_echo_tab, adjust_sort_order
from echo_sort.echo_data import read_echo_info, process_echo, second_echo

# 初始化 logger
logger = logging.getLogger(__name__)

class GameController:
    def __init__(self):
        self.image_tool = ImageTool()
        self.game_window = None
        self.multiplayer_icon = "./image/multiplayer_icon.png"  # 需准备的图片
        self.load_data()  # 加载数据

    def load_data(self):
        """加载数据"""
        with open('./data/echo.json', 'r', encoding='utf-8') as f:
            self.echo_data = json.load(f)
        with open('./data/default_rules.json', 'r', encoding='utf-8') as f:
            self.default_rules = json.load(f)

    def activate_game_window(self, retry=3, delay=2):
        """
        激活游戏窗口并验证是否成功进入游戏界面
        :param retry: 最大重试次数
        :param delay: 每次重试间隔(秒)
        :return: (bool) 是否成功激活
        """
        logger.info("正在跳转到游戏...")
        for _ in range(retry):
            # 1. 获取游戏窗口句柄
            def enum_windows_callback(hwnd, results):
                if re.match(f"^鸣潮", win32gui.GetWindowText(hwnd)):
                    results.append(hwnd)
            
            results = []
            win32gui.EnumWindows(enum_windows_callback, results)
            self.game_window = results[0] if results else None

            if not self.game_window:
                logger.warning("未找到游戏窗口")
                time.sleep(delay)
                continue
                
            try:
                # 2. 激活窗口
                win32gui.ShowWindow(self.game_window, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.game_window)
                time.sleep(2)  # 等待窗口激活
                
                # 3. 调整窗口分辨率（可选）
                win32gui.MoveWindow(self.game_window, 0, 0, 3440, 1440, True)
                
                # 4. 验证游戏界面状态
                if self.image_tool.find_image(self.multiplayer_icon, confidence=0.8):
                    logger.info("成功进入游戏界面")
                    return True
                    
            except Exception as e:
                logger.error(f"窗口操作异常: {str(e)}")
            
            time.sleep(0.2)
        
        logger.error("无法激活游戏窗口")
        return False