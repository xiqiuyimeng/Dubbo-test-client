# -*- coding: utf-8 -*-
"""
树节点，目前使用了四个隐藏列存储字段：
第一列：存储opened item db 中存储的对应项的id
第二列：连接节点存储的是conn db 中存储的连接信息，方法节点存储的是 opened item db 中存储的对应的ext_info
第三列：只有连接节点用到，存储是否正在执行测试连接任务，如果是的话，需要在右键菜单中展示取消，可以取消当前测试任务
"""
from PyQt5.QtWidgets import QTreeWidgetItem

_author_ = 'luwt'
_date_ = '2021/11/3 22:38'


class MyTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, parent):
        super().__init__(parent)
        self.async_worker = ...

    def setText(self, column, text):
        if not isinstance(text, str):
            text = str(text)
        super().setText(column, text)
