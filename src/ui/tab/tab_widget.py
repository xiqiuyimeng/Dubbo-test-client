# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QTabWidget

_author_ = 'luwt'
_date_ = '2021/11/8 16:49'


class MyTabWidget(QTabWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)


