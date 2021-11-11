# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QTabWidget

from src.constant.tab_constant import ARGS_PARAM_TYPE, JSON_PARAM_TYPE

_author_ = 'luwt'
_date_ = '2021/11/8 16:49'


class MyTabWidget(QTabWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)
        # 保存已经打开的tab页字典，key为 tab_id, value为tab页widget，方便取到tab widget
        self.opened_tab_ids = dict()


class ParamTabWidget(QTabWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)

    def decide_current_tab(self, method_param_list, param_type, args_tab, json_tab):
        # 如果参数列表不存在，则关闭tabWidget
        if not method_param_list:
            self.hide()
        else:
            # 优先考虑param_type，根据param_type的值来决定
            if param_type:
                if param_type == ARGS_PARAM_TYPE:
                    self.setCurrentWidget(args_tab)
                elif param_type == JSON_PARAM_TYPE:
                    self.setCurrentWidget(json_tab)
            else:
                # 最后考虑实际的参数个数，参数个数大于1应该使用args
                if len(method_param_list) > 1:
                    self.setCurrentWidget(args_tab)
                else:
                    self.setCurrentWidget(json_tab)



