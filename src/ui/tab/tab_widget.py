# -*- coding: utf-8 -*-
from PyQt5 import QtGui
from PyQt5.QtWidgets import QTabWidget

_author_ = 'luwt'
_date_ = '2021/11/8 16:49'


class MyTabWidget(QTabWidget):

    def __init__(self):
        super().__init__()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        width = self.width()
        tab_count = self.count()
        super().showEvent(a0)


