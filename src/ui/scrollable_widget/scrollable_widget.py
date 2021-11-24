# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QAbstractScrollArea, QTreeWidget

from src.constant.main_constant import SYNC_ITEM_EXPANDED
from src.ui.async_func.async_conn_db import AsyncUpdateExpandedManager

_author_ = 'luwt'
_date_ = '2021/11/3 22:28'


class MyScrollableWidget(QAbstractScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, a0):
        """设置滚动条在进入控件区域的时候显示"""
        self.verticalScrollBar().setHidden(False)
        self.horizontalScrollBar().setHidden(False)

    def leaveEvent(self, a0):
        """设置滚动条在离开控件区域的时候隐藏"""
        self.verticalScrollBar().setHidden(True)
        self.horizontalScrollBar().setHidden(True)


class MyTreeWidget(QTreeWidget, MyScrollableWidget):

    def __init__(self, parent, window):
        super().__init__(parent)
        self.window = window

    def update_expanded(self, opened_item_id, expanded, item):
        AsyncUpdateExpandedManager(opened_item_id, expanded, item, self.window, SYNC_ITEM_EXPANDED).start()

    def tree_column_resize(self):
        """树节点打开或关闭，都应该重新设置，这样能保证列跟随内容变化，也就是可以随内容自动添加或去掉水平滚动条"""
        self.resizeColumnToContents(0)
