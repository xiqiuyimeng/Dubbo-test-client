# -*- coding: utf-8 -*-
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QAbstractScrollArea, QTextBrowser

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

