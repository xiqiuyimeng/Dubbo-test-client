# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QVBoxLayout, QToolBar

from src.constant.conn_dialog_constant import ADD_CONN_MENU
from src.function.db.conn_sqlite import Connection, ConnSqlite
from src.ui.dialog.conn.conn_dialog import ConnDialog
from src.ui.func.common import keep_center
from src.ui.func.menu_bar import fill_menu_bar
from src.ui.func.tool_bar import fill_tool_bar
from src.ui.func.tree import tree_node_factory, Context, add_conn_item, reopen_conn_item, add_conn_tree_item
from src.ui.scrollable_widget.scrollable_widget import MyTreeWidget
from src.ui.tab.tab_bar import MyTabBar
from src.ui.tab.tab_widget import MyTabWidget

_author_ = 'luwt'
_date_ = '2021/10/31 17:39'


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, screen_rect):
        super().__init__()
        # 当前屏幕的分辨率大小
        self.desktop_screen_rect = screen_rect
        # 创建主控件，用以包含所有内容
        self.main_widget = QtWidgets.QWidget()
        # 主控件中的布局
        self.main_layout = QVBoxLayout()
        # 主部件
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setObjectName("central_widget")
        # 主部件布局为水平布局
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        # 左边树结构frame
        self.tree_frame = QtWidgets.QFrame(self.central_widget)
        self.tree_frame.setObjectName("tree_frame")
        self.horizontalLayout.addWidget(self.tree_frame)
        self.tree_layout = QtWidgets.QVBoxLayout(self.tree_frame)
        self.tree_layout.setObjectName("tree_layout")
        # 左边树结构
        self.tree_widget = MyTreeWidget(self.central_widget)
        self.tree_widget.setObjectName("tree_widget")
        self.tree_widget.headerItem().setText(0, "连接列表")
        self.tree_layout.addWidget(self.tree_widget)
        # 右边tab区frame
        self.tab_frame = QtWidgets.QFrame(self.central_widget)
        self.tab_frame.setObjectName("tab_frame")
        self.horizontalLayout.addWidget(self.tab_frame)
        self.tab_layout = QtWidgets.QVBoxLayout(self.tab_frame)
        self.tab_layout.setObjectName("tab_layout")
        # 右边tab区
        self.tab_widget = MyTabWidget(self.tab_frame)
        self.tab_widget.setObjectName("tab_widget")
        self.tab_bar = MyTabBar(self.tab_widget)
        self.tab_bar.setObjectName("tab_bar")
        self.tab_widget.setTabBar(self.tab_bar)
        self.tab_layout.addWidget(self.tab_widget)
        # 菜单栏
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        # 工具栏
        self.toolBar = QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self._translate = QtCore.QCoreApplication.translate
        self.setup_ui()
        self.translate_ui()
        self.bind_action()

    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.setWindowFlags(Qt.WindowTitleHint)
        # 按当前分辨率计算窗口大小
        self.resize(self.desktop_screen_rect.width() * 0.65, self.desktop_screen_rect.height() * 0.7)
        # 窗体居中
        keep_center(self, self.desktop_screen_rect)

        # 设置所有控件间距为0
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 7)
        # 填充菜单栏
        fill_menu_bar(self)
        # 填充工具栏
        fill_tool_bar(self)
        # self.toolBar.setIconSize(QSize(50, 40))
        # 设置名称显示在图标下面（默认本来是只显示图标）
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.main_layout.addWidget(self.central_widget)

    def bind_action(self):
        # 初始化树：初始化获取树结构的第一层元素，为数据库连接列表
        self.get_saved_conns()
        # 双击树节点事件
        self.tree_widget.doubleClicked.connect(self.get_tree_list)
        # 点击、展开、收起节点，都需要让列根据内容自适应，从而可以保证水平滚动条
        self.tree_widget.doubleClicked.connect(self.tree_widget.tree_column_resize)
        self.tree_widget.expanded.connect(self.tree_widget.tree_column_resize)
        self.tree_widget.collapsed.connect(self.tree_widget.tree_column_resize)
        # 右击事件
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.right_click_menu)

    def translate_ui(self):
        self.setWindowTitle(self._translate("MainWindow", "MainWindow"))

    def add_conn(self):
        """打开添加连接窗口"""
        conn_info = Connection(*((None,) * len(Connection._fields)))
        conn_dialog = ConnDialog(conn_info, ADD_CONN_MENU, self.geometry())
        conn_dialog.conn_signal.connect(lambda conn: add_conn_item(self, conn))
        conn_dialog.exec()

    def get_saved_conns(self):
        """获取所有已存储的连接，生成页面树结构第一层"""
        conns = ConnSqlite().select_all()
        self.tab_widget.reopen_flag = True
        for conn in conns:
            # conn属性：id name host port timeout
            # 根节点，展示连接的列表，将连接信息写入隐藏列
            item = add_conn_tree_item(self, conn)
            # 查出当前连接有没有保存在打开项中
            reopen_conn_item(self, item, parent_id=conn.id)
        self.tab_widget.reopen_flag = False
        # 按顺序排列tab
        self.tab_widget.insert_tab_by_order()

    def get_tree_list(self):
        """获取树的子节点，双击触发，连接 -> service -> method，按顺序读取出来"""
        item = self.tree_widget.currentItem()
        node = tree_node_factory(item)
        Context(node).open_item(item, self)

    def right_click_menu(self, pos):
        """
        右键菜单功能，实现右键弹出菜单功能
        :param pos:右键的坐标位置
        """
        # 获取当前元素，只有在元素上才显示菜单
        item = self.tree_widget.itemAt(pos)
        if item:
            # 生成右键菜单
            menu = QtWidgets.QMenu()
            node = tree_node_factory(item)
            menu_names = Context(node).get_menu_names(item, self)
            [menu.addAction(QtWidgets.QAction(option, menu)) for option in menu_names]
            # 右键菜单点击事件
            menu.triggered.connect(lambda action: Context(node).handle_menu_func(item, action.text(), self))
            # 右键菜单弹出位置跟随焦点位置
            menu.exec_(QCursor.pos())


