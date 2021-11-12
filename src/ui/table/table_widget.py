# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from src.constant.tab_constant import PARAM_TABLE_HEADER
from src.ui.table.table_item import MyTableItem

_author_ = 'luwt'
_date_ = '2021/11/11 18:02'


class ParamTableWidget(QTableWidget):

    # 表格项文本变化信号，row, col, text
    item_data_changed = pyqtSignal(int, int, str)

    def __init__(self, tab_ui):
        super().__init__()
        self.set_table_header()
        self.tab_ui = tab_ui

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
                # 可编辑列，使用自定义的部件代替QTableWidgetItem
                param_value_item = MyTableItem()
                self.setCellWidget(row, 1, param_value_item)
                param_value_item.textEdited.connect(self.item_data_change_event)
                param_desc_item = MyTableItem()
                self.setCellWidget(row, 2, param_desc_item)
                param_desc_item.textEdited.connect(self.item_data_change_event)

    def fill_table_column(self, values, column):
        """表格填充，值的个数必须要与表格行数相同，若大于表格行数，则会忽略掉超出部分"""
        if len(values) > self.rowCount():
            values = values[:self.rowCount()]
        # 根据指定的列，填充表格
        [self.cellWidget(row, column).setText(value) for row, value in enumerate(values)]

    def item_data_change_event(self, text):
        """获取当前的行列及改变的文本，发送信号"""
        self.item_data_changed.emit(self.currentRow(), self.currentColumn(), text)



