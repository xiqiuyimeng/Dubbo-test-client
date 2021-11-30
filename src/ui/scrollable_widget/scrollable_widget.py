# -*- coding: utf-8 -*-
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QAbstractScrollArea, QTreeWidget, QTextBrowser

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
        self.update_expanded_manager = ...

    def update_expanded(self, opened_item_id, expanded, item):
        self.update_expanded_manager = AsyncUpdateExpandedManager(opened_item_id, expanded, item,
                                                                  self.window, SYNC_ITEM_EXPANDED)
        self.update_expanded_manager.start()

    def tree_column_resize(self):
        """树节点打开或关闭，都应该重新设置，这样能保证列跟随内容变化，也就是可以随内容自动添加或去掉水平滚动条"""
        self.resizeColumnToContents(0)


class MyTextBrowser(QTextBrowser, MyScrollableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_text(self, text):
        """
        设置文本时，使用append方法，这时全部文本会被追加到控件中，
        光标处于文本末端，此时再次设置光标为文本初始位置，
        这可以避免当文本过大时，调用setText方法，控件只展示了当前文本，剩余部分未完全加载展示，
        导致在滚动时，控件加载展示对应文本，会有卡顿感
        """
        self.append(text)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)

