# -*- coding: utf-8 -*-
"""
菜单栏列表生成
"""

from PyQt5 import QtGui, QtWidgets

from src.constant.main_constant import FILE_MENU, HELP_MENU, ADD_CONN_MENU, EXIT_MENU, ABOUT_MENU

_author_ = 'luwt'
_date_ = '2021/11/01 8:26'


def fill_menu_bar(window):
    """
    填充菜单栏
    :param window: 启动的主窗口界面对象
    """
    window.file_menu = window.menubar.addMenu(FILE_MENU)
    window.file_menu.setObjectName("file_menu")
    add_conn_menu(window)
    exit_app_menu(window)

    window.help_menu = window.menubar.addMenu(HELP_MENU)
    window.help_menu.setObjectName("help_menu")
    help_menu(window)
    about_menu(window)


def add_conn_menu(window):
    """
    添加连接菜单
    :param window: 启动的主窗口界面对象
    """
    add_action = QtWidgets.QAction(QtGui.QIcon(':/icon/add.png'), ADD_CONN_MENU, window)
    add_action.setShortcut('Ctrl+N')
    add_action.setStatusTip('在左侧列表中添加一条连接')
    # add_action.triggered.connect(lambda: add_conn_func(window, window.screen_rect))

    window.file_menu.addAction(add_action)


def exit_app_menu(window):
    """
    退出菜单
    :param window: 启动的主窗口界面对象
    """
    exit_action = QtWidgets.QAction(QtGui.QIcon(':/icon/exit.png'), EXIT_MENU, window)
    exit_action.setShortcut('Ctrl+Q')
    exit_action.setStatusTip('退出应用程序')
    exit_action.triggered.connect(window.close)

    window.file_menu.addAction(exit_action)


def help_menu(window):
    """帮助菜单"""
    help_action = QtWidgets.QAction(QtGui.QIcon(":/icon/add.png"), HELP_MENU, window)
    help_action.setShortcut('Ctrl+H')
    help_action.setStatusTip('帮助信息')
    # help_action.triggered.connect(gui.help)
    window.help_menu.addAction(help_action)


def about_menu(window):
    """关于菜单"""
    about_action = QtWidgets.QAction(QtGui.QIcon(":/icon/exit.png"), ABOUT_MENU, window)
    about_action.setStatusTip('关于')
    # about_action.triggered.connect(gui.about)
    window.help_menu.addAction(about_action)
