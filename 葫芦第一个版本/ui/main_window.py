# ui/main_window.py
# 导入必要的 PyQt5 模块
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QStackedWidget
)

class MainWindow(QMainWindow):
    def __init__(self):
        """
        主窗口类的构造函数，用于初始化窗口的界面和功能模块。
        """
        # 调用父类 QMainWindow 的构造函数
        super().__init__()
        # 初始化用户界面
        self.init_ui()
        # 初始化各个功能模块
        self.init_modules()
        
        # 创建主界面的中心部件
        self.central_widget = QWidget()
        # 将中心部件设置为当前窗口的中心部件
        self.setCentralWidget(self.central_widget)
        # 创建一个垂直布局用于管理中心部件内的子部件
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 创建顶部的功能选择按钮区域
        self.create_function_buttons()
        
        # 创建一个堆叠窗口，用于管理不同的功能页面
        self.stacked_widget = QStackedWidget()
        # 将堆叠窗口添加到主布局中
        self.main_layout.addWidget(self.stacked_widget)
        
        # 再次调用初始化模块的方法，确保模块初始化完成
        self.init_modules()

    def create_function_buttons(self):
        """
        创建顶部的功能选择按钮，包括声骸整理、声骸强化、配装优化和伤害计算按钮。
        为这些按钮设置样式和点击事件，点击按钮可以切换不同的功能页面。
        """
        # 创建一个水平布局用于放置功能按钮
        btn_layout = QHBoxLayout()

        # 创建声骸整理按钮
        self.btn_sort = QPushButton("声骸整理")
        # 创建声骸强化按钮
        self.btn_enhance = QPushButton("声骸强化")
        # 创建配装优化按钮
        self.btn_optimize = QPushButton("配装优化")
        # 创建伤害计算按钮
        self.btn_damage = QPushButton("伤害计算")

        # 定义按钮的样式表
        button_style = """
            QPushButton {
                font-size: 14px; 
                padding: 8px;
                min-width: 120px;
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        # 为每个按钮应用样式表并设置固定高度
        for btn in [self.btn_sort, self.btn_enhance, self.btn_optimize, self.btn_damage]:
            btn.setStyleSheet(button_style)
            btn.setFixedHeight(40)
        
        # 将按钮添加到水平布局中
        btn_layout.addWidget(self.btn_sort)
        btn_layout.addWidget(self.btn_enhance)
        btn_layout.addWidget(self.btn_optimize)
        btn_layout.addWidget(self.btn_damage)
        # 将水平布局添加到主布局中
        self.main_layout.addLayout(btn_layout)

        # 连接按钮的点击信号到切换页面的方法
        self.btn_sort.clicked.connect(lambda: self.switch_page(0))
        self.btn_enhance.clicked.connect(lambda: self.switch_page(1))
        self.btn_optimize.clicked.connect(lambda: self.switch_page(2))
        self.btn_damage.clicked.connect(lambda: self.switch_page(3))

    def init_modules(self):
        """
        初始化各个功能模块，将声骸整理模块添加到堆叠窗口中，
        其他模块暂时用空的 QWidget 占位。
        """
        # 从 ui.echo_sort_ui 模块导入 EchoSortWidget 类
        from ui.echo_sort_ui import EchoSortWidget
        
        # 创建声骸整理模块的实例
        self.echo_sort_widget = EchoSortWidget()
        # 将声骸整理模块添加到堆叠窗口中
        self.stacked_widget.addWidget(self.echo_sort_widget)
        
        # 为声骸强化模块添加一个空的 QWidget 占位
        self.stacked_widget.addWidget(QWidget())  # 强化
        # 为配装优化模块添加一个空的 QWidget 占位
        self.stacked_widget.addWidget(QWidget())  # 优化
        # 为伤害计算模块添加一个空的 QWidget 占位
        self.stacked_widget.addWidget(QWidget())  # 伤害

    def switch_page(self, index):
        """
        切换堆叠窗口中显示的功能页面。
        :param index: 要显示的页面的索引
        """
        # 设置堆叠窗口当前显示的页面索引
        self.stacked_widget.setCurrentIndex(index)

    def init_ui(self):
        """
        初始化主窗口的用户界面，包括主界面布局、功能按钮区域和堆叠窗口。
        """
        # 创建主界面的中心部件
        self.central_widget = QWidget()
        # 将中心部件设置为当前窗口的中心部件
        self.setCentralWidget(self.central_widget)
        # 创建一个垂直布局用于管理中心部件内的子部件
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 创建顶部的功能选择按钮区域
        self.create_function_buttons()
        
        # 创建一个堆叠窗口，用于管理不同的功能页面
        self.stacked_widget = QStackedWidget()
        # 将堆叠窗口添加到主布局中
        self.main_layout.addWidget(self.stacked_widget)