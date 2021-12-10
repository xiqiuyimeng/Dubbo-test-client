# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel

_author_ = 'luwt'
_date_ = '2021/12/9 12:27'


class LabelButton(QLabel):

    # 点击信号
    clicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

    def mousePressEvent(self, ev):
        self.clicked.emit()

