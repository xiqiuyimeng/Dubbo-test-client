# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QTabWidget

_author_ = 'luwt'
_date_ = '2021/11/8 16:49'


class MyTabWidget(QTabWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)
        # 保存已经打开的tab页字典，key为 tab_id, value为tab页widget，方便取到tab widget
        self.opened_tab_ids = dict()



