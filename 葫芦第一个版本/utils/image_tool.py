# utils/image_tool.py
import difflib
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
import os
import re
import easyocr
import json
import logging

# 初始化 logger
logger = logging.getLogger(__name__)

class ImageTool:
    def __init__(self):
        self.reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)  # 初始化 easyocr 读取器，启用 GPU 加速

    def find_image(self, template_path, region=None, confidence=0.7, grayscale=True, save_screenshot=False, screenshot_path="./screenshot.png"):
        """
        增强版图像识别方法
        :param template_path: 模板图片路径
        :param region: 搜索区域 (left, top, right, bottom)
        :param confidence: 匹配置信度阈值
        :param grayscale: 是否使用灰度匹配
        :param save_screenshot: 是否保存截取的屏幕图像
        :param screenshot_path: 保存截取屏幕图像的路径
        :return: (x, y) 中心坐标 或 None
        """
        try:
            # 截取屏幕
            screen = ImageGrab.grab(bbox=region) if region else ImageGrab.grab()
            screen = np.array(screen)

            # 转换为灰度图像
            if grayscale:
                if len(screen.shape) == 3 and screen.shape[2] == 3:
                    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                elif len(screen.shape) == 2:
                    pass  # 已经是灰度图像
                else:
                    raise ValueError("输入图像的通道数不正确")
                # 高斯模糊去噪
                screen = cv2.GaussianBlur(screen, (3, 3), 0)
                # 自适应二值化
                screen = cv2.adaptiveThreshold(screen, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY, 11, 2)

            # 对模板做相同处理
            template = cv2.imread(template_path, 0 if grayscale else 1)
            if template is None:
                raise FileNotFoundError(f"模板图片不存在: {template_path}")

            if grayscale:
                template = cv2.GaussianBlur(template, (3, 3), 0)
                template = cv2.adaptiveThreshold(template, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
                
            # 保存截图
            if save_screenshot:
                cv2.imwrite(screenshot_path, screen)
                
            # 模板匹配
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            logger.info(f"匹配图片：{template_path},最大匹配值: {max_val}")

            if max_val >= confidence:
                h, w = template.shape[:2]
                return (
                    max_loc[0] + w // 2 + (region[0] if region else 0),
                    max_loc[1] + h // 2 + (region[1] if region else 0)
                )
            return None
        except Exception as e:
            logger.error(f"图像识别失败: {str(e)}")
            return None

    def capture_region(self, region, filename, folder="./image"):
        """
        截取指定区域并保存到文件
        :param region: (left, top, width, height)
        :param filename: 保存文件名（无需后缀）
        :param folder: 保存目录
        :return: (bool) 是否保存成功
        """
        try:
            # 转换区域格式为(left, top, right, bottom)
            actual_region = (
                region[0],
                region[1],
                region[0] + region[2],
                region[1] + region[3]
            )
            # 检查区域坐标是否正确
            if actual_region[2] <= actual_region[0] or actual_region[3] <= actual_region[1]:
                raise ValueError("截取区域的坐标不正确：右边界应大于左边界，下边界应大于上边界")
            
            # 创建目录（如果不存在）
            os.makedirs(folder, exist_ok=True)
            
            # 截取并保存
            screenshot = ImageGrab.grab(bbox=actual_region)
            filepath = os.path.join(folder, f"{filename}.png")
            screenshot.save(filepath)
            return True
            
        except Exception as e:
            logger.error(f"截图保存失败：{str(e)}")
            return False

    def _clean_text(self, text):
        """清理OCR识别结果"""
        return ''.join(text).strip().replace('\n', '').replace('\f', '')
    
    def _parse_attr(self, text):
        """解析词条"""
        # 预处理文本
        cleaned_text = ''.join(text).strip().replace('\n', '').replace('\f', '')
        cleaned_text = re.sub(r'声骸技能.*', '', cleaned_text)

        # 拆分所有元素
        elements = cleaned_text.split()
        
        # 初始化属性列表和数值列表
        attributes = []
        values = []
        
        # 正则表达式匹配组合属性（如"攻击30.0%"）和纯数值
        pattern_combined = re.compile(r'^([^\d]+?)(\d+\.?\d*%?)$')  # 组合属性
        pattern_value = re.compile(r'^\d+\.?\d*%?$')                # 纯数值
        
        for elem in elements:
            # 处理组合属性（属性+数值）
            match_combined = pattern_combined.match(elem)
            if match_combined:
                attr = match_combined.group(1).strip()
                value = match_combined.group(2).strip()
                attributes.append(attr)
                values.append(value)
                continue
            
            # 处理纯数值
            if pattern_value.match(elem):
                values.append(elem)
                continue
            
            # 处理纯属性
            attributes.append(elem.strip())
            # 输出当前的 attributes 和 values 列表内容

        # 读取 cost.json 文件
        with open('./data/cost.json', 'r', encoding='utf-8') as f:
            cost_data = json.load(f)

        # 生成键值对
        attrs = {}
        attr_index = 1
        value_index = 0
        for i in range(len(attributes)):
            attr = attributes[i]
            if attr_index == 1:  # attr1
                if attr in cost_data["cost4"] or attr in cost_data["cost3"] or attr in cost_data["cost1"]:
                    attrs[f"attr{attr_index}"] = attr
                    if value_index < len(values):
                        attrs[f"attr{attr_index}_num"] = values[value_index]
                        value_index += 1
                    attr_index += 1
            else:  # attr2 - attr7
                if attr in cost_data["attr"]:
                    attrs[f"attr{attr_index}"] = attr
                    if value_index < len(values):
                        attrs[f"attr{attr_index}_num"] = values[value_index]
                        value_index += 1
                    attr_index += 1
 
        # 如果 attr1 不存在，将 attr2 的值改为 attr1
        if "attr1" not in attrs and "attr2" in attrs:
            attrs["attr1"] = attrs.pop("attr2")
            if "attr2_num" in attrs:
                attrs["attr1_num"] = attrs.pop("attr2_num")
        
        return attrs

    def _parse_cost_level(self, text):
        """解析COST和等级"""
        match = re.search(r'COST\s*(\d+)\s*\+\s*(\d+)', text)
        return {
            "cost": int(match.group(1)) if match else 0,
            "level": int(match.group(2)) if match else 0
        }

    def _match_echo_set(self, region):
        """匹配声骸套装"""
        set_dir = "./image/echo_kind"
        best_match = None
        best_match_val = 0.5  # 设置初始匹配值阈值
  
        # 截取指定区域的图像
        screen = ImageGrab.grab(bbox=region)
        image = np.array(screen.convert('L'))  # 转换为灰度图像

        for set_file in os.listdir(set_dir):
            template_path = os.path.join(set_dir, set_file)
            template = cv2.imread(template_path, 0)
            if template is None:
                continue

            # 模板匹配
            res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
        
            # 如果匹配值大于0.5且匹配值最高，则更新最佳匹配
            if (max_val > best_match_val):
                best_match_val = max_val
                best_match = set_file

        return best_match or "未知套装"
    
    def find_name(self, image_path, echo_data):
        """
        读取图像中含有“.”的名称
        :param image_path: 图像路径
        :param echo_data: echo.json 数据
        :return: 处理后的名称
        """
        recognized_name = self._clean_text(self.reader.readtext(image_path, detail=0, paragraph=True))
        # 将识别的文字中的“.”符号替换为“・”
        processed_name = recognized_name.replace('.', '・')
        # 去除处理后的名称中的空格
        processed_name = processed_name.replace(' ', '')
        return processed_name


