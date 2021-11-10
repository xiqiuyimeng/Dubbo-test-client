# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QTreeWidgetItem

_author_ = 'luwt'
_date_ = '2021/11/3 22:38'


class MyTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, tree, parent):
        super().__init__(parent)
        self.tree = tree

    def setText(self, column, text):
        if not isinstance(text, str):
            text = str(text)
        super().setText(column, text)
