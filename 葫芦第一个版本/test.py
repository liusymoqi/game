import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import win32gui
import win32con
import re
from utils.image_tool import ImageTool
from echo_sort.echo_data import second_echo


def activate_game_window(retry=3, delay=2):
    """
    激活游戏窗口并验证是否成功进入游戏界面
    :param retry: 最大重试次数
    :param delay: 每次重试间隔(秒)
    :return: (bool) 是否成功激活
    """
    print("正在跳转到游戏...")
    for _ in range(retry):
        # 1. 获取游戏窗口句柄
        def enum_windows_callback(hwnd, results):
            if re.match(f"^鸣潮", win32gui.GetWindowText(hwnd)):
                results.append(hwnd)

        results = []
        win32gui.EnumWindows(enum_windows_callback, results)
        game_window = results[0] if results else None

        if not game_window:
            print("未找到游戏窗口")
            time.sleep(delay)
            continue

        try:
            # 2. 激活窗口
            win32gui.ShowWindow(game_window, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(game_window)
            time.sleep(2)  # 等待窗口激活

            # 3. 调整窗口分辨率（可选）
            win32gui.MoveWindow(game_window, 0, 0, 3440, 1440, True)

            return True

        except Exception as e:
            print(f"窗口操作异常: {str(e)}")

        time.sleep(0.2)

    print("无法激活游戏窗口")
    return False


def run_test():
    try:
        scroll_value = int(entry.get())

        # 2. 点击开始测试后，跳转到游戏窗口
        if not activate_game_window():
            messagebox.showerror("错误", "无法激活游戏窗口")
            return

        image_tool = ImageTool()

        # 3. 截取第二排的图片作为second_echo中的对比图片
        image_tool.capture_region((275, 435, 205, 240), "second_echo", folder="./image")

        def modified_second_echo(image_tool):
            try:
                max_attempts = 120  # 最大尝试次数
                attempts = 0
            
                scroll_value2 = 0 - scroll_value

                while attempts < max_attempts:
                    # 滑动滚轮
                    print(f"滑动值: {scroll_value2}")
                    pyautogui.scroll(scroll_value2)  # 使用测试的滑动值
                    # 截取当前区域图片
                    print(f"第{attempts + 1}次滑动")
                    time.sleep(2)
                    # 比较当前区域图片与 second_echo 图片
                    if image_tool.find_image("./image/second_echo.png", region=(265, 155, 480, 405), confidence=0.6):
                        return False

                    attempts += 1

                print("滑动过长仍未符合")
                return False

            except Exception as e:
                print(f"滑动过程中发生错误: {str(e)}")
                return False

        # 4. 开始调用second_echo方法直接往下滑动滚轮，重复20次
        success_count = 0
        for i in range(1):
            print(f"第 {i + 1} 轮测试")
            result = modified_second_echo(image_tool)
            if result:
                success_count += 1

        messagebox.showinfo("测试结果", f"滑动值 {scroll_value} 的测试中，20 次尝试成功 {success_count} 次。")
    except ValueError:
        messagebox.showerror("输入错误", "请输入一个有效的整数。")


# 创建主窗口
root = tk.Tk()
root.title("滑动值测试")

# 创建标签和输入框
label = tk.Label(root, text="请输入滑动值:")
label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

# 创建开始测试按钮
button = tk.Button(root, text="开始测试", command=run_test)
button.pack(pady=20)

# 运行主循环
root.mainloop()