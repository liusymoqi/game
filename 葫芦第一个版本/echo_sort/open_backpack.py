import pyautogui
import time
import logging

# 初始化 logger
logger = logging.getLogger(__name__)

def open_backpack(image_tool, retry=3, interval=1.5):
    """
    打开背包并验证是否成功
    :param image_tool: ImageTool 实例
    :param retry: 最大重试次数
    :param interval: 重试间隔(秒)
    :return: (bool) 是否成功打开
    """
    close_btn_img = "./image/backpack_close.png"  # 需准备的关闭按钮图片
    
    for attempt in range(1, retry+1):
        logger.info(f"尝试打开背包 ({attempt}/{retry})...")
        
        # 按下B键打开背包
        pyautogui.press('b')
        time.sleep(0.5)  # 等待界面响应
        
        # 识别关闭按钮
        if image_tool.find_image(close_btn_img, confidence=0.85):
            logger.info("背包界面已成功打开")
            return True
            
        logger.warning("未检测到背包界面")
        time.sleep(interval)
    
    logger.error(f"无法打开背包，已重试{retry}次")
    return False

def switch_to_echo_tab(image_tool, retry=3):
    """
    切换到声骸背包标签页
    :param image_tool: ImageTool 实例
    :param retry: 最大重试次数
    :return: (bool) 是否切换成功
    """
    filter_icon = "./image/filter_icon.png"  # 筛选图标（声骸背包特有）
    echo_tab_icon = "./image/echo_tab.png"   # 声骸标签页图标
    
    # 检查是否已在声骸背包
    if image_tool.find_image(filter_icon, confidence=0.8):
        logger.info("当前已在声骸背包")
        return True
        
    for attempt in range(1, retry+1):
        logger.info(f"尝试切换到声骸背包 ({attempt}/{retry})...")
        
        # 定位声骸标签页按钮
        tab_pos = image_tool.find_image(echo_tab_icon, confidence=0.7)
        if not tab_pos:
            logger.warning("未找到声骸标签页入口")
            continue
            
        # 精确点击标签页中心位置
        pyautogui.moveTo(tab_pos[0], tab_pos[1], duration=0.3)
        pyautogui.click()
        time.sleep(0.5)  # 等待界面切换
        
        # 验证是否切换成功
        if image_tool.find_image(filter_icon, confidence=0.8):
            logger.info("成功进入声骸背包")
            return True
            
    logger.error("切换到声骸背包失败")
    return False

def adjust_sort_order(image_tool, max_attempts=3):
    """
    调整排序为按获得时间排序
    :param image_tool: ImageTool 实例
    :param max_attempts: 最大调整尝试次数
    :return: (bool) 是否成功调整
    """
    time_sort_icon = "./image/time_sort_icon.png"   # 当前是时间排序的标识
    sort_menu_icon = "./image/sort_menu_icon.png"   # 排序按钮图标
    sort_list_icon = "./image/sort_list_open.png"   # 展开的排序列表标识
    sort_option_icon = "./image/sort_time_option.png" # 时间排序选项图标

    # 步骤5：检查当前排序状态
    if image_tool.find_image(time_sort_icon, confidence=0.85):
        logger.info("当前已是按获得时间排序")
        return True

    for attempt in range(1, max_attempts+1):
        logger.info(f"\n--- 第{attempt}次尝试调整排序 ---")
        
        # 步骤5a：点击排序按钮
        sort_btn = image_tool.find_image(sort_menu_icon, confidence=0.6)
        if not sort_btn:
            logger.warning("未找到排序按钮")
            continue
            
        pyautogui.moveTo(sort_btn[0], sort_btn[1], duration=0.3)
        pyautogui.click()
        time.sleep(0.5)  # 等待菜单展开

        # 步骤5b：验证排序列表是否打开
        if not image_tool.find_image(sort_list_icon, confidence=0.8):
            logger.warning("排序列表未正常展开")
            continue

        # 步骤6a：选择时间排序选项
        time_option = image_tool.find_image(sort_option_icon, confidence=0.75)
        if not time_option:
            logger.warning("未找到时间排序选项")
            continue
            
        pyautogui.moveTo(time_option[0], time_option[1], duration=0.3)
        pyautogui.click()
        time.sleep(0.2)  # 等待列表关闭

        # 步骤6b：验证排序结果
        if image_tool.find_image(time_sort_icon, confidence=0.85):
            logger.info("成功设置为按获得时间排序")
            return True

        logger.warning("排序状态验证未通过")
    
    logger.error(f"无法调整排序，已尝试{max_attempts}次")
    return False