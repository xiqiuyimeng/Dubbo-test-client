# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from src.constant.tab_constant import PARAM_TABLE_HEADER

_author_ = 'luwt'
_date_ = '2021/11/11 18:02'


class ParamTableWidget(QTableWidget):

    def __init__(self):
        super().__init__()
        self.set_table_header()
        # 表格行交替颜色
        self.setAlternatingRowColors(True)

    def set_table_header(self):
        # 3 列表格
        self.setColumnCount(3)
        # 表头标题
        self.setHorizontalHeaderLabels(PARAM_TABLE_HEADER)
        # 最后一列拉伸
        self.horizontalHeader().setStretchLastSection(True)
        # 表格列宽均分，最后一列拉伸
        self.setColumnWidth(0, round(self.width() / 3))
        self.setColumnWidth(1, round(self.width() / 3))

    def init_table(self, method_param_list):
        # 初始化表格内容，按逗号拆分参数，根据参数个数填充表格
        if method_param_list:
            self.setRowCount(len(method_param_list))
            for row, param_type in enumerate(method_param_list):
                param_type_item = QTableWidgetItem()
                param_type_item.setText(param_type)
                # flags，必须首先是ItemIsEnabled启用后，才能再设置别的状态
                param_type_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.setItem(row, 0, param_type_item)
                param_value_item = QTableWidgetItem()
                self.setItem(row, 1, param_value_item)
                param_desc_item = QTableWidgetItem()
                self.setItem(row, 2, param_desc_item)

    def fill_table_column(self, values, column):
        """表格填充，值的个数必须要与表格行数相同，若大于表格行数，则会忽略掉超出部分"""
        if len(values) > self.rowCount():
            values = values[:self.rowCount()]
        # 根据指定的列，填充表格
        [self.item(row, column).setText(value) for row, value in enumerate(values)]



