# ui/echo_sort_ui.py
# 导入必要的 PyQt5 模块
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QListWidget, QPushButton, QDialog, QCheckBox,
    QScrollArea, QLabel, QListWidgetItem, QAbstractItemView, QMessageBox
)
# 导入 PyQt5 的核心模块中的类
from PyQt5.QtCore import Qt, QEvent, QTimer
# 从 utils.game_controller 模块导入 GameController 类
from utils.game_controller import GameController

class EchoSortWidget(QWidget):
    def __init__(self):
        """
        类的构造函数，用于初始化 EchoSortWidget 实例。
        此方法会完成以下操作：
        1. 调用父类的构造函数。
        2. 初始化存储所有词条、锁定规则和弃置规则的字典。
        3. 初始化用户界面。
        4. 加载数据并初始化默认规则。
        5. 创建 GameController 实例。
        6. 初始化 EchoSorter 实例，并传入 UI 状态更新回调函数。
        7. 安装事件过滤器以处理按键事件。
        8. 初始化 Esc 键计数器和计时器。
        """
        # 调用父类 QWidget 的构造函数
        super().__init__()
        # 用于存储所有可用的词条信息
        self.all_cost_attrs = {}  
        # 存储用户选择的锁定规则
        self.selected_lock_rules = {}
        # 存储用户选择的弃置规则
        self.selected_discard_rules = {}
        # 初始化用户界面
        self.init_ui()
        # 加载数据并初始化默认规则
        self.load_data()
        # 创建 GameController 实例，用于控制游戏相关操作
        self.game_controller = GameController()

        # 从 echo_sort.echo_sort 模块导入 EchoSorter 类
        from echo_sort.echo_sort import EchoSorter
        # 初始化 EchoSorter 实例，并传入 UI 状态更新回调函数
        self.sorter = EchoSorter(self.update_ui_status)

        # 安装事件过滤器，用于处理按键事件
        self.installEventFilter(self)

        # 初始化 Esc 键计数器，用于记录按下 Esc 键的次数
        self.esc_counter = 0
        # 创建一个 QTimer 实例，用于计时
        self.esc_timer = QTimer()
        # 设置计时器的间隔为 1 秒
        self.esc_timer.setInterval(1000)  
        # 当计时器超时时，调用 reset_esc_counter 方法重置计数器
        self.esc_timer.timeout.connect(self.reset_esc_counter)

    def eventFilter(self, obj, event):
        """
        事件过滤器，用于处理按键事件。
        当按下 Esc 键时，暂停整理操作。
        :param obj: 事件发生的对象
        :param event: 发生的事件
        :return: 如果事件被处理则返回 True，否则返回父类的处理结果
        """
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                # 按下 Esc 键，暂停整理操作
                self.pause_sorting()
                return True
        # 其他事件交给父类处理
        return super().eventFilter(obj, event)

    def reset_esc_counter(self):
        """
        重置 Esc 键计数器，并停止计时器。
        当计时器超时时，会调用此方法。
        """
        # 将 Esc 键计数器重置为 0
        self.esc_counter = 0
        # 停止计时器
        self.esc_timer.stop()

    def pause_sorting(self):
        """
        暂停整理操作，并更新 UI 状态为已暂停。
        调用 EchoSorter 实例的 pause_sorting 方法暂停整理，
        并调用 update_ui_status 方法更新 UI 状态。
        """
        # 调用 EchoSorter 实例的 pause_sorting 方法暂停整理
        self.sorter.pause_sorting()
        # 调用 update_ui_status 方法更新 UI 状态为已暂停
        self.update_ui_status("paused")

    def init_ui(self):
        """
        初始化用户界面，包括布局和各个组件。
        此方法会创建以下组件：
        1. 主布局，使用水平布局。
        2. 左侧锁定设置区域，包含一个列表和相关的布局。
        3. 右侧弃置设置区域，包含一个列表和相关的布局。
        4. 右侧显示区域，包含当前设置展示区、状态标签和操作按钮。
        """
        # 创建主布局，使用水平布局
        main_layout = QHBoxLayout(self)
        
        # 创建左侧锁定设置组
        self.lock_group = QGroupBox("锁定设置")
        # 创建锁定规则列表
        self.lock_list = QListWidget()
        # 设置列表的选择模式为单选
        self.lock_list.setSelectionMode(QAbstractItemView.SingleSelection)
        # 当列表项被点击时，调用 show_lock_options 方法
        self.lock_list.itemClicked.connect(self.show_lock_options)
        # 创建锁定规则列表的布局
        lock_layout = QVBoxLayout()
        # 将锁定规则列表添加到布局中
        lock_layout.addWidget(self.lock_list)
        # 将布局设置给锁定设置组
        self.lock_group.setLayout(lock_layout)
        
        # 创建右侧弃置设置组
        self.discard_group = QGroupBox("弃置设置")
        # 创建弃置规则列表
        self.discard_list = QListWidget()
        # 设置列表的选择模式为单选
        self.discard_list.setSelectionMode(QAbstractItemView.SingleSelection)
        # 当列表项被点击时，调用 show_discard_options 方法
        self.discard_list.itemClicked.connect(self.show_discard_options)
        # 创建弃置规则列表的布局
        discard_layout = QVBoxLayout()
        # 将弃置规则列表添加到布局中
        discard_layout.addWidget(self.discard_list)
        # 将布局设置给弃置设置组
        self.discard_group.setLayout(discard_layout)
        
        # 将锁定设置组和弃置设置组添加到主布局中
        main_layout.addWidget(self.lock_group, 35)
        main_layout.addWidget(self.discard_group, 35)
        
        # 创建右侧显示区域的布局
        self.right_layout = QVBoxLayout()
        
        # 创建当前设置展示区
        self.current_settings = QListWidget()
        # 设置当前设置展示区的最大宽度
        self.current_settings.setMaximumWidth(300)
        # 添加当前设置标签
        self.right_layout.addWidget(QLabel("当前设置"))
        # 将当前设置展示区添加到布局中
        self.right_layout.addWidget(self.current_settings)

        # 创建状态标签，初始文本为准备就绪
        self.status_label = QLabel("准备就绪")
        # 设置状态标签的对齐方式为居中
        self.status_label.setAlignment(Qt.AlignCenter)
        # 设置状态标签的样式
        self.status_label.setStyleSheet("font-size: 14px; color: #666;")
        
        # 在布局中插入状态标签
        self.right_layout.insertWidget(1, self.status_label)
        
        # 创建开始整理按钮
        btn_start = QPushButton("开始整理")
        # 设置按钮的固定高度
        btn_start.setFixedHeight(45)
        # 设置按钮的样式
        btn_start.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {background-color: #1976D2;}
        """)
        # 当按钮被点击时，调用 start_sorting 方法
        btn_start.clicked.connect(self.start_sorting)
        # 将开始整理按钮添加到布局中
        self.right_layout.addWidget(btn_start)
        
        # 将右侧显示区域的布局添加到主布局中
        main_layout.addLayout(self.right_layout, 30)

    def load_data(self):
        """
        加载数据并初始化默认规则。
        此方法会完成以下操作：
        1. 创建 DataLoader 实例，用于加载数据。
        2. 加载声骸数据、默认规则和所有可用词条。
        3. 初始化锁定规则和弃置规则。
        4. 填充套装列表并更新当前设置的显示。
        """
        # 从 utils.data_loader 模块导入 DataLoader 类
        from utils.data_loader import DataLoader
        # 创建 DataLoader 实例
        loader = DataLoader()
        # 加载声骸数据
        self.echo_data = loader.load_echo_data()
        # 加载默认规则
        self.default_rules = loader.load_default_rules()
        # 加载所有可用词条
        self.all_cost_attrs = loader.get_all_cost_attrs()  
        
        # 初始化锁定规则和弃置规则
        for set_name in self.echo_data.keys():
            # 初始化锁定规则
            self.selected_lock_rules[set_name] = {
                "cost1": self.default_rules[set_name]["cost1"]["lock"],
                "cost3": self.default_rules[set_name]["cost3"]["lock"],
                "cost4": self.default_rules[set_name]["cost4"]["lock"]
            }
            # 初始化弃置规则
            self.selected_discard_rules[set_name] = {
                "cost1": self.default_rules[set_name]["cost1"]["discard"],
                "cost3": self.default_rules[set_name]["cost3"]["discard"],
                "cost4": self.default_rules[set_name]["cost4"]["discard"]
            }
        
        # 填充套装列表
        self.populate_set_lists()
        # 更新当前设置的显示
        self.update_current_display()

    def populate_set_lists(self):
        """
        填充套装列表，将声骸数据中的套装名称添加到锁定规则列表和弃置规则列表中。
        此方法会先清空两个列表，然后遍历声骸数据的键，将每个键添加到两个列表中。
        """
        # 清空锁定规则列表
        self.lock_list.clear()
        # 清空弃置规则列表
        self.discard_list.clear()
        # 遍历声骸数据的键
        for set_name in self.echo_data.keys():
            # 将套装名称添加到锁定规则列表中
            self.lock_list.addItem(set_name)
            # 将套装名称添加到弃置规则列表中
            self.discard_list.addItem(set_name)

    def show_lock_options(self, item):
        """
        显示锁定词条选择对话框。
        当锁定规则列表中的项被点击时，调用此方法。
        此方法会获取点击项的文本，并调用 show_options_dialog 方法显示对话框。
        :param item: 被点击的列表项
        """
        # 获取点击项的文本
        set_name = item.text()
        # 调用 show_options_dialog 方法显示锁定规则设置对话框
        self.show_options_dialog(set_name, "lock")

    def show_discard_options(self, item):
        """
        显示弃置词条选择对话框。
        当弃置规则列表中的项被点击时，调用此方法。
        此方法会获取点击项的文本，并调用 show_options_dialog 方法显示对话框。
        :param item: 被点击的列表项
        """
        # 获取点击项的文本
        set_name = item.text()
        # 调用 show_options_dialog 方法显示弃置规则设置对话框
        self.show_options_dialog(set_name, "discard")

    def show_options_dialog(self, set_name, rule_type):
        """
        显示词条选择对话框，用于设置锁定或弃置规则。
        此方法会创建一个对话框，包含各个 cost 类型的词条选择区域，
        每个区域有复选框用于选择词条，还有全选和反选按钮。
        最后会添加一个确认按钮，点击确认按钮会调用 save_selections 方法保存选择。
        :param set_name: 套装名称
        :param rule_type: 规则类型，"lock" 或 "discard"
        """
        # 创建一个对话框
        dialog = QDialog(self)
        # 设置对话框的标题
        dialog.setWindowTitle(f"{set_name} - {rule_type}规则设置")
        # 设置对话框的最小尺寸
        dialog.setMinimumSize(500, 400)
        
        # 创建对话框的布局
        layout = QVBoxLayout()
        # 创建滚动区域
        scroll = QScrollArea()
        # 创建内容区域
        content = QWidget()
        # 创建内容区域的布局
        content_layout = QVBoxLayout()
        
        # 定义 cost 类型列表
        cost_types = ["cost1", "cost3", "cost4"]
        
        # 遍历每个 cost 类型
        for cost in cost_types:
            # 创建一个组框，用于显示该 cost 类型的词条选择
            group = QGroupBox(f"{cost.upper()} 词条选择")
            # 创建组框的布局
            group_layout = QVBoxLayout()
            
            # 获取该 cost 类型的所有可用词条
            all_attrs = self.get_available_attrs(cost)
            
            # 获取当前已选的词条
            current_selected = (
                self.selected_lock_rules[set_name][cost] 
                if rule_type == "lock" 
                else self.selected_discard_rules[set_name][cost]
            )
            
            # 创建复选框列表
            checkboxes = []
            # 遍历所有可用词条
            for attr in all_attrs:
                # 创建一个复选框
                cb = QCheckBox(attr)
                # 设置复选框的默认选中状态
                cb.setChecked(attr in current_selected)  
                # 将复选框添加到列表中
                checkboxes.append(cb)
                # 将复选框添加到组框的布局中
                group_layout.addWidget(cb)

            # 创建全选/反选按钮布局
            btn_row = QHBoxLayout()
            # 创建全选按钮
            btn_all = QPushButton("全选")
            # 创建反选按钮
            btn_invert = QPushButton("反选")
            # 将全选按钮添加到布局中
            btn_row.addWidget(btn_all)
            # 将反选按钮添加到布局中
            btn_row.addWidget(btn_invert)
            
            # 为全选按钮绑定点击事件，点击后全选所有复选框
            btn_all.clicked.connect(lambda _, cbs=checkboxes: 
                [cb.setChecked(True) for cb in cbs])
            # 为反选按钮绑定点击事件，点击后反选所有复选框
            btn_invert.clicked.connect(lambda _, cbs=checkboxes: 
                [cb.setChecked(not cb.isChecked()) for cb in cbs])
            
            # 将按钮布局添加到组框的布局中
            group_layout.addLayout(btn_row)
            # 将组框的布局设置给组框
            group.setLayout(group_layout)
            # 将组框添加到内容区域的布局中
            content_layout.addWidget(group)
        
        # 创建确认按钮
        btn_confirm = QPushButton("确认")
        # 为确认按钮绑定点击事件，点击后保存选择
        btn_confirm.clicked.connect(lambda: self.save_selections(
            set_name, cost_types, content, rule_type, dialog))
        
        # 将内容区域的布局设置给内容区域
        content.setLayout(content_layout)
        # 将内容区域添加到滚动区域中
        scroll.setWidget(content)
        # 将滚动区域添加到对话框的布局中
        layout.addWidget(scroll)
        # 将确认按钮添加到对话框的布局中
        layout.addWidget(btn_confirm)
        # 将对话框的布局设置给对话框
        dialog.setLayout(layout)
        # 显示对话框
        dialog.exec_()

    def update_ui_status(self, status, msg=None):
        """
        UI 状态更新回调函数，根据传入的状态更新状态标签的文本和样式。
        此方法会根据不同的状态，设置状态标签的文本和颜色。
        :param status: 状态，如 "running", "success", "error", "paused"
        :param msg: 可选的错误消息
        """
        # 定义状态映射字典，包含不同状态对应的文本和颜色
        status_map = {
            "running": ("运行中...", "#2196F3"),
            "success": ("整理完成", "#4CAF50"),
            "error": (f"错误: {msg}", "#F44336"),
            "paused": ("已暂停", "#FF9800")
        }
        # 根据状态获取对应的文本和颜色，如果状态不存在则使用默认值
        text, color = status_map.get(status, ("未知状态", "#666"))
        # 设置状态标签的文本
        self.status_label.setText(text)
        # 设置状态标签的样式
        self.status_label.setStyleSheet(f"font-size: 14px; color: {color};")

    def get_available_attrs(self, cost_type):
        """
        获取指定 cost 类型的所有可用词条。
        此方法会从 all_cost_attrs 字典中获取指定 cost 类型的词条列表，
        如果不存在则返回空列表。
        :param cost_type: cost 类型，如 "cost1", "cost3", "cost4"
        :return: 可用词条列表
        """
        # 从 all_cost_attrs 字典中获取指定 cost 类型的词条列表，如果不存在则返回空列表
        return self.all_cost_attrs.get(cost_type, [])

    def save_selections(self, set_name, cost_types, content, rule_type, dialog):
        """
        保存选择的词条，更新规则存储并更新当前设置的显示。
        此方法会遍历每个 cost 类型，获取选中的词条，并过滤掉无效词条，
        然后根据规则类型更新锁定或弃置规则，最后更新当前设置的显示并关闭对话框。
        :param set_name: 套装名称
        :param cost_types: cost 类型列表
        :param content: 对话框的内容区域
        :param rule_type: 规则类型，"lock" 或 "discard"
        :param dialog: 对话框实例
        """
        # 用于存储选择的词条
        selections = {}
        # 遍历每个 cost 类型
        for i, cost in enumerate(cost_types):
            # 获取该 cost 类型的组框
            group = content.layout().itemAt(i).widget()
            # 获取组框中的所有复选框
            checkboxes = group.findChildren(QCheckBox)
            # 获取选中的词条
            selected = [cb.text() for cb in checkboxes if cb.isChecked()]
            
            # 获取该 cost 类型的所有可用词条
            valid_attrs = self.get_available_attrs(cost)
            # 过滤掉无效词条
            selections[cost] = [attr for attr in selected if attr in valid_attrs]
        
        # 根据规则类型更新锁定或弃置规则
        if rule_type == "lock":
            self.selected_lock_rules[set_name] = selections
        else:
            self.selected_discard_rules[set_name] = selections
        
        # 更新当前设置的显示
        self.update_current_display()
        # 关闭对话框
        dialog.close()

    def update_current_display(self):
        """
        优化后的设置显示逻辑，将锁定规则和弃置规则显示在当前设置展示区。
        此方法会先清空当前设置展示区，然后遍历锁定规则和弃置规则，
        将规则信息以列表项的形式添加到展示区。
        """
        # 清空当前设置展示区
        self.current_settings.clear()
        
        # 合并锁定规则和弃置规则
        all_rules = [
            ("🔒 锁定规则", self.selected_lock_rules, Qt.darkGreen),
            ("🗑️ 弃置规则", self.selected_discard_rules, Qt.darkRed)
        ]
        
        # 遍历所有规则
        for title, rules, color in all_rules:
            # 创建规则标题项
            header = QListWidgetItem(title)
            # 设置标题项的前景色
            header.setForeground(color)
            # 设置标题项不可选中
            header.setFlags(header.flags() & ~Qt.ItemIsSelectable)  
            # 将标题项添加到当前设置展示区
            self.current_settings.addItem(header)
            
            # 遍历每个套装的规则
            for set_name, cost_rules in rules.items():
                # 标记是否有规则
                has_rule = False
                # 遍历每个 cost 类型的规则
                for cost, attrs in cost_rules.items():
                    if attrs:
                        # 如果有规则，标记为 True
                        has_rule = True
                        # 创建套装和 cost 类型的列表项
                        item = QListWidgetItem(f"   {set_name} - {cost}")
                        # 设置列表项的数据
                        item.setData(Qt.UserRole, (set_name, cost))
                        # 将列表项添加到当前设置展示区
                        self.current_settings.addItem(item)
                        # 遍历每个词条
                        for attr in attrs:
                            # 创建词条的列表项
                            sub_item = QListWidgetItem(f"     • {attr}")
                            # 设置词条列表项的前景色
                            sub_item.setForeground(Qt.darkGray)
                            # 将词条列表项添加到当前设置展示区
                            self.current_settings.addItem(sub_item)
                
                if not has_rule:
                    # 如果没有规则，创建未设置规则的列表项
                    item = QListWidgetItem(f"   {set_name} - 未设置规则")
                    # 设置列表项的前景色
                    item.setForeground(Qt.gray)
                    # 将列表项添加到当前设置展示区
                    self.current_settings.addItem(item)

    def start_sorting(self):
        """
        开始整理按钮点击事件处理函数，调用 EchoSorter 的 start_sorting 方法开始整理。
        如果在整理过程中发生错误，会弹出错误消息框。
        """
        try:
            # 调用 EchoSorter 实例的 start_sorting 方法开始整理
            self.sorter.start_sorting(self.selected_lock_rules, self.selected_discard_rules)
        except Exception as e:
            # 如果发生异常，弹出错误消息框
            QMessageBox.critical(self, "错误", f"整理过程中发生错误: {str(e)}")