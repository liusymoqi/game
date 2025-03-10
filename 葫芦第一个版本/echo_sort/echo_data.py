import pyautogui
import time
import os
import logging

# 配置日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_echoes(image_tool, echo_data, lock_rules, discard_rules, deal_max=3000):
    """
    处理声骸的主循环
    :param image_tool: ImageTool 实例
    :param echo_data: echo.json 数据
    :param lock_rules: 锁定规则字典
    :param discard_rules: 弃置规则字典
    :return: (bool) 是否成功处理
    """
    try:
        # 初始化计数器
        deal_sum = 0
        deal_num = 0

        while deal_sum < deal_max:
            # 将从 265*430 开始的 2200*250 范围的区域的图片保存起来
            image_tool.capture_region((275, 435, 205, 240), "second_echo", folder="./image")

            # 点击 375*275 位置选择首位声骸，读取屏幕右侧声骸信息
            click_position = (375 + deal_num * 220, 275)
            echo_info = read_echo_info(image_tool, echo_data, click_position=click_position)
            if not echo_info:
                logger.error("无法读取声骸信息")
                return False

            # 处理声骸
            result = process_echo(image_tool, echo_data, echo_info, lock_rules, discard_rules)
            if "声骸名称不在套装对应的COST下" in result:
                logger.info(f"处理第 {deal_sum} 个声骸: {result}")
                logger.info(f"声骸详细信息: {echo_info}")
            else:
                logger.info(f"处理第 {deal_sum} 个声骸: {result}")

            # 更新计数器
            deal_sum += 1
            deal_num += 1

            if deal_num >= 10:
                deal_num = 0
                if not second_echo(image_tool):
                    logger.error("滑动过长仍未符合")
                    return False

        return True
    except Exception as e:
        logger.error(f"处理声骸时出错: {str(e)}")
        return False

def read_echo_info(image_tool, echo_data, click_position=(375, 275), attempt=3):
    """
    读取声骸详细信息
    :param image_tool: ImageTool 实例
    :param echo_data: echo.json 数据
    :param click_position: 鼠标点击位置 (x, y)
    :param attempt: 最大尝试次数
    :return: dict/None 包含声骸信息的字典，失败返回None
    """
    for _ in range(attempt):
        try:
            # 点击选择声骸
            pyautogui.click(click_position[0], click_position[1])
            time.sleep(0.1)

            # 初始化数据容器
            echo_info = {"count": 1}

            # 1. 读取声骸名称
            image_tool.capture_region((2600, 150, 750, 80), "name_img", folder="./image/region")
            name_img_path = "./image/region/name_img.png"
            echo_info["name"] = image_tool.find_name(name_img_path, echo_data)

            # 2. 读取COST和等级
            image_tool.capture_region((3135, 265, 200, 130), "cost_img", folder="./image/region")
            cost_img_path = "./image/region/cost_img.png"
            cost_text = image_tool._clean_text(image_tool.reader.readtext(cost_img_path, detail=0, paragraph=True))
            echo_info.update(image_tool._parse_cost_level(cost_text))

            # 3. 识别所属套装
            echo_info["set"] = image_tool._match_echo_set((2790, 400, 2850, 460))

            # 4. 读取主词条
            image_tool.capture_region((2600, 525, 740, 475), "main_attr_img", folder="./image/region")
            main_attr_img_path = "./image/region/main_attr_img.png"
            echo_info.update(image_tool._parse_attr(image_tool.reader.readtext(main_attr_img_path, detail=0, paragraph=True)))

            # 5. 识别锁定状态
            lock_icon_path = "./image/locked_icon.png"
            echo_info["locked"] = image_tool.find_image(
                lock_icon_path,
                region=(3070, 400, 3350, 500),
                confidence=0.9,  # 提高置信度阈值
                grayscale=True  # 强制灰度匹配
            ) is not None

            # 6. 识别弃置状态（假设区域相同）
            discard_icon_path = "./image/discarded_icon.png"
            echo_info["discarded"] = image_tool.find_image(
                discard_icon_path,
                region=(3070, 400, 3350, 500), 
                confidence=0.9,
                grayscale=True,
            ) is not None
           
            return echo_info

        except Exception as e:
            logger.error(f"读取声骸信息失败（剩余尝试次数{attempt-1}）: {str(e)}")
            attempt -= 1
            time.sleep(1)
    
    logger.error("无法读取声骸信息")
    return None

def process_echo(image_tool, echo_data, echo_info, lock_rules, discard_rules):
    """
    处理声骸信息，判断是否锁定或弃置
    :param image_tool: ImageTool 实例
    :param echo_data: echo.json 数据
    :param echo_info: 声骸信息字典
    :param lock_rules: 锁定规则字典
    :param discard_rules: 弃置规则字典
    :return: (str) 处理结果信息
    """
    try:
        # 判断声骸所属套装
        echo_set = echo_info.get("set")
        if not echo_set:
            return "无法识别声骸套装"

        # 处理 echo_set 可能是图片文件名的情况
        echo_set = os.path.splitext(echo_set)[0]  # 去掉文件扩展名

        # 查找 echo_set 对应的套装名称
        echo_set_name = None
        for set_name, set_data in echo_data.items():
            if set_data["num"] == echo_set:
                echo_set_name = set_name
                break

        if not echo_set_name:
            return f"无法识别声骸套装: {echo_set}"

        # 判断声骸名称是否在该套装对应的cost下
        echo_name = echo_info.get("name")
        echo_cost = echo_info.get("cost")
        if echo_cost == 1:
            cost_key = "cost1"
        elif echo_cost == 3:
            cost_key = "cost3"
        elif echo_cost == 4:
            cost_key = "cost4"
        else:
            return f"未知的声骸COST: {echo_cost}"

        if echo_name not in echo_data[echo_set_name].get(cost_key, []):
            return f"声骸名称不在套装对应的COST下: {echo_name}"

        # 根据锁定和弃置规则判断
        attr1 = echo_info.get("attr1")
        if attr1 in lock_rules[echo_set_name].get(cost_key, []):
            # 检查是否已锁定
            if echo_info.get("locked"):
                return f"声骸已锁定: {echo_name}"
            else:
                # 执行锁定操作
                pyautogui.press('c')
                time.sleep(0.01)
                if image_tool.find_image("./image/locked_icon.png", region=(3070, 400, 3350, 500), confidence=0.9):
                    return f"声骸已锁定: {echo_name}"
                else:
                    return f"声骸锁定失败: {echo_name}"
        elif attr1 in discard_rules[echo_set_name].get(cost_key, []):
            # 检查是否已弃置
            if echo_info.get("discarded"):
                return f"声骸已弃置: {echo_name}"
            else:
                # 执行弃置操作
                pyautogui.press('z')
                time.sleep(0.01)
                if image_tool.find_image("./image/discarded_icon.png", region=(3070, 400, 3350, 500), confidence=0.9):
                    return f"声骸已弃置: {echo_name}"
                else:
                    return f"声骸弃置失败: {echo_name}"
        else:
            return f"声骸不符合锁定或弃置规则: {echo_name}"

    except Exception as e:
        return f"处理声骸信息时出错: {str(e)}"

def second_echo(image_tool):
    """操控鼠标滑动滚轮，直到指定区域与 second_echo 图片完全符合"""
    try:
        max_attempts = 1  # 最大尝试次数
        attempts = 0

        while attempts < max_attempts:
            # 滑动滚轮
            pyautogui.scroll(-933)  # 向下滑动滚轮，值越大滑动越多
            # 截取当前区域图片
            time.sleep(0.5)
            logger.info(f"第{attempts+1}次滑动")
            # 比较当前区域图片与 second_echo 图片
            if image_tool.find_image("./image/second_echo.png", region=(265, 155, 480, 405), confidence=0.6):
                return True

            attempts += 1

        logger.error("滑动过长仍未符合")
        return False

    except Exception as e:
        logger.error(f"滑动过程中发生错误: {str(e)}")
        return False

