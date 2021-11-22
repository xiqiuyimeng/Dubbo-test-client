# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel

from src.function.db.conn_sqlite import ConnSqlite
from src.function.db.opened_item_sqlite import OpenedItemSqlite
from src.function.db.tab_sqlite import TabSqlite

_author_ = 'luwt'
_date_ = '2021/11/1 11:27'


def keep_center(window, screen_rect):
    # 获取当前窗口（window）坐标系
    window_rect = window.geometry()
    # 计算新的位置，使窗体在参照物（screen_rect）中心
    center_left = (screen_rect.width() - window_rect.width()) >> 1
    center_top = (screen_rect.height() - window_rect.height()) >> 1
    # 为了保证在参照物的中心，需要跟随当前参照物的位置移动
    window.move(center_left + screen_rect.x(), center_top + screen_rect.y())


def set_up_label(parent: QWidget, text: str, obj_name: str):
    """建立label"""
    label = QLabel(parent)
    label.setObjectName(obj_name)
    label.setText(text)
    # 设置可选中
    label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    return label


def close_sqlite():
    # 关闭sqlite连接
    ConnSqlite().close()
    OpenedItemSqlite().close()
    TabSqlite().close()
