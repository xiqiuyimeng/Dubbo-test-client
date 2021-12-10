# -*- coding: utf-8 -*-
from queue import Queue

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget

from src.constant.main_constant import SAVE_TAB_DATA
from src.ui.async_func.async_tab import AsyncSaveTabObjManager

_author_ = 'luwt'
_date_ = '2021/11/8 16:49'


class MyTabWidget(QTabWidget):

    # 当前至少存在一个tab
    opened_tab_signal = pyqtSignal()
    # 清除所有tab
    clear_tabs_signal = pyqtSignal()

    def __init__(self, parent, main_window):
        super().__init__(parent=parent)
        self.main_window = main_window
        # 在启动过程中，暂存tab 列表，方便按排序展示
        self.temp_tab_list = list()
        # 存储tab_id顺序
        self.tab_id_list = list()
        # 临时变量，存储下库中存储的当前tab，仅在启动过程中使用
        self.current = None
        # 维护一个队列，用来持续保存tab页的数据
        self.queue = Queue()
        self.async_save_manager = AsyncSaveTabObjManager(self.queue,
                                                         self.main_window,
                                                         SAVE_TAB_DATA)
        self.async_save_manager.start()

    def read_saved_tab(self, idx):
        """当前页变化时，调用tab的read_saved_tab方法"""
        if idx >= 0:
            tab = self.widget(idx)
            tab_ui = tab.property("tab_ui")
            tab_ui.read_saved_tab()

    def insert_tab_by_order(self):
        # 按order排序
        self.temp_tab_list.sort(key=lambda x: x[0])
        if self.temp_tab_list:
            self.fill_tab_id_list(list(map(lambda x: x[1].property('tab_id'), self.temp_tab_list)))
        [self.addTab(tab[1], tab[2]) for tab in self.temp_tab_list]
        if self.current is not None:
            self.setCurrentIndex(self.current)
            self.read_saved_tab(self.current)
        del self.temp_tab_list
        del self.current
        # 在处理完后，将信号连上
        self.currentChanged.connect(self.read_saved_tab)
        # 当前选项卡指针改变时（选项卡顺序改变时也会触发），修改数据库
        self.currentChanged.connect(self.tabBar().change_current_order)

    def close(self):
        self.async_save_manager.worker_quit()
        super().close()

    def fill_tab_id_list(self, data):
        # 如果当前还不存在tab，那么这是第一个，发送信号
        if self.count() == 0:
            self.opened_tab_signal.emit()
        if isinstance(data, list):
            self.tab_id_list = data
        else:
            self.tab_id_list.append(data)

    def clear_tab_id_list(self):
        self.clear_tabs_signal.emit()
        self.tab_id_list.clear()


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



