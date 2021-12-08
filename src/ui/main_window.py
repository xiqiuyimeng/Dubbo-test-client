# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QVBoxLayout, QToolBar, QSplitter

from src.constant.conn_dialog_constant import ADD_CONN_MENU, EDIT_CONN_MENU
from src.function.db.conn_sqlite import Connection
from src.ui.async_func.async_reopen_item import AsyncReopenManager
from src.ui.dialog.conn.conn_dialog import ConnDialog
from src.ui.func.common import keep_center, close_sqlite
from src.ui.func.menu_bar import fill_menu_bar
from src.ui.func.tool_bar import fill_tool_bar
from src.ui.func.tree import tree_node_factory, Context
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
        self.main_splitter = QSplitter()
        self.main_splitter.setOrientation(Qt.Horizontal)
        self.main_splitter.setObjectName("main_splitter")
        self.horizontalLayout.addWidget(self.main_splitter)
        self.horizontalLayout.setSpacing(0)
        # 左边树结构frame
        self.tree_frame = QtWidgets.QFrame(self.main_splitter)
        self.tree_frame.setObjectName("tree_frame")
        self.tree_layout = QtWidgets.QVBoxLayout(self.tree_frame)
        self.tree_layout.setObjectName("tree_layout")
        self.tree_layout.setSpacing(0)
        self.tree_layout.setContentsMargins(0, 0, 0, 0)
        # 左边树结构
        self.tree_widget = MyTreeWidget(self.tree_frame, self)
        self.tree_widget.setObjectName("tree_widget")
        self.tree_widget.headerItem().setText(0, "连接列表")
        self.tree_layout.addWidget(self.tree_widget)
        # 右边tab区frame
        self.tab_frame = QtWidgets.QFrame(self.main_splitter)
        self.tab_frame.setObjectName("tab_frame")
        self.tab_layout = QtWidgets.QVBoxLayout(self.tab_frame)
        self.tab_layout.setObjectName("tab_layout")
        # 右边tab区
        self.tab_widget = MyTabWidget(self.tab_frame, main_window=self)
        self.tab_widget.setObjectName("tab_widget")
        self.tab_bar = MyTabBar(self.tab_widget)
        self.tab_bar.setObjectName("tab_bar")
        self.tab_widget.setTabBar(self.tab_bar)
        self.tab_layout.addWidget(self.tab_widget)
        self.tab_layout.setSpacing(0)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
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
        self.reopen_manager = ...
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
        self.main_splitter.setStretchFactor(0, 2)
        self.main_splitter.setStretchFactor(1, 9)
        # 填充菜单栏
        fill_menu_bar(self)
        # 填充工具栏
        fill_tool_bar(self)
        # 设置名称显示在图标下面（默认本来是只显示图标）
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.main_layout.addWidget(self.central_widget)

    def bind_action(self):
        # 异步重新打开上次退出时的工作状态
        self.reopen_manager = AsyncReopenManager(self, self.tree_widget, self.tab_widget)
        self.reopen_manager.start()
        # 双击树节点事件
        self.tree_widget.doubleClicked.connect(self.get_tree_list)
        # 点击、展开、收起节点，都需要让列根据内容自适应，从而可以保证水平滚动条
        self.tree_widget.doubleClicked.connect(self.handle_expanded_changed)
        self.tree_widget.expanded.connect(self.handle_expanded_changed)
        self.tree_widget.collapsed.connect(self.handle_expanded_changed)
        # 右击事件
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.right_click_menu)

    def translate_ui(self):
        self.setWindowTitle(self._translate("MainWindow", "MainWindow"))

    def add_conn(self):
        """打开添加连接窗口"""
        conn_info = Connection(*((None,) * len(Connection._fields)))
        conn_dialog = ConnDialog(conn_info, ADD_CONN_MENU, self.geometry(), self.tree_widget)
        conn_dialog.exec()

    def edit_conn(self, conn_info, tree_item):
        """打开编辑连接窗口"""
        conn_dialog = ConnDialog(conn_info, EDIT_CONN_MENU, self.geometry(), tree_item=tree_item)
        conn_dialog.exec()

    def get_tree_list(self):
        """获取树的子节点，双击触发，连接 -> service -> method，按顺序读取出来"""
        item = self.tree_widget.currentItem()
        node = tree_node_factory(item)
        Context(node).open_item(item, self)

    def handle_expanded_changed(self, index):
        # 根据当前内容决定列宽度
        self.tree_widget.tree_column_resize()
        # 如果正在启动软件，不需要进行监听
        if not self.tab_widget.reopen_flag:
            item = self.tree_widget.itemFromIndex(index)
            # method节点没有expanded属性，没有必要进行处理，监听conn和service节点就可以
            if item.parent() is None or item.parent().parent() is None:
                expanded = self.tree_widget.itemFromIndex(index).isExpanded()
                self.tree_widget.update_expanded(item.text(1), expanded, item)

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

    def del_history(self):
        item = self.tree_widget.currentItem()
        node = tree_node_factory(item)
        Context(node).del_history(item, self)

    def close(self):
        close_sqlite()
        self.tab_widget.close()
        super().close()
