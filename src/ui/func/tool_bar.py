# -*- coding: utf-8 -*-
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

_author_ = 'luwt'
_date_ = '2021/11/1 11:51'


def fill_tool_bar(window):
    add_insert_conn_tool(window)
    add_refresh_tool(window)
    add_del_history_tool(window)
    add_exit_tool(window)


def add_insert_conn_tool(window):
    # 指定图标
    insert_tool = QAction(QIcon(':/icon/add.png'), '添加连接', window)
    insert_tool.setStatusTip('在左侧列表中添加一条连接')
    insert_tool.triggered.connect(window.add_conn)
    window.toolBar.addAction(insert_tool)


def add_refresh_tool(window):
    refresh_tool = QAction(QIcon(':/icon/refresh.png'), '刷新', window)
    refresh_tool.setStatusTip('刷新')
    refresh_tool.setShortcut('F5')
    # refresh_tool.triggered.connect(gui.refresh)
    window.toolBar.addAction(refresh_tool)


def add_del_history_tool(window):
    del_history_tool = QAction(QIcon(':/icon/remove.png'), '删除历史记录', window)
    del_history_tool.setStatusTip('删除指定项下保存的方法测试记录')
    del_history_tool.triggered.connect(window.del_history)
    window.toolBar.addAction(del_history_tool)


def add_exit_tool(window):
    exit_tool = QAction(QIcon(':/icon/exit.png'), '退出程序', window)
    exit_tool.setStatusTip('退出应用程序')
    exit_tool.triggered.connect(window.close)
    window.toolBar.addSeparator()
    window.toolBar.addAction(exit_tool)
