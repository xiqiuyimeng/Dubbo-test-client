# -*- coding: utf-8 -*-
from queue import Queue

from PyQt5.QtWidgets import QTabWidget

from src.constant.main_constant import SAVE_TAB_DATA
from src.ui.async_func.async_tab import AsyncSaveTabObjManager

_author_ = 'luwt'
_date_ = '2021/11/8 16:49'


class MyTabWidget(QTabWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent=parent)
        self.main_window = main_window
        # 标识是否在软件启动，重新打开项目中
        self.reopen_flag = False
        # 在启动过程中，暂存tab 列表，方便按排序展示
        self.temp_tab_list = list()
        # 临时变量，存储下库中存储的当前tab，仅在启动过程中使用
        self.current = None
        # 维护一个队列，用来持续保存tab页的数据
        self.queue = Queue()
        self.async_save_manager = AsyncSaveTabObjManager(self.queue,
                                                         self.main_window,
                                                         SAVE_TAB_DATA)
        self.async_save_manager.start()

    def insert_tab_by_order(self):
        # 按order排序
        self.temp_tab_list.sort(key=lambda x: x[0])
        [self.addTab(tab[1], tab[2]) for tab in self.temp_tab_list]
        if self.current:
            self.setCurrentIndex(self.current)
        del self.temp_tab_list
        del self.current

    def close(self):
        self.async_save_manager.quit()
        super().close()


class ParamTabWidget(QTabWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)

    def decide_current_tab(self, method_param_list, param_type=None):
        # 如果参数列表不存在，则关闭tabWidget
        if not method_param_list:
            self.hide()
        else:
            # 优先考虑param_type，根据param_type的值来决定
            if param_type is not None:
                self.setCurrentIndex(param_type)
            else:
                # 最后考虑实际的参数个数，参数个数大于1应该使用args
                if len(method_param_list) > 1:
                    self.setCurrentIndex(0)
                else:
                    self.setCurrentIndex(1)



