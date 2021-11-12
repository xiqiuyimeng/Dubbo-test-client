# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QLineEdit

_author_ = 'luwt'
_date_ = '2021/11/12 09:26'


class MyTableItem(QLineEdit):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("border-width:0;border-style:outset")








