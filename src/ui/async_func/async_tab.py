# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal

from src.ui.async_func.async_operate_abc import ConnWorker, LoadingMaskThreadWorkManager

_author_ = 'luwt'
_date_ = '2021/11/22 16:52'


# ----------------------- thread worker -----------------------


class SendRequestWorker(ConnWorker):

    success_signal = pyqtSignal(str)

    def __init__(self, method, *args):
        super().__init__(*args)
        self.method = method

    def do_work(self):
        method_result = self.client.invoke(self.method)
        self.success_signal.emit(method_result)


# ----------------------- thread worker manager -----------------------


class AsyncSendRequestManager(LoadingMaskThreadWorkManager):

    def __init__(self, fail_callback, callback, masked_widget, window, title, method, *args):
        self.method = method
        self.args = args
        self.fail_callback = fail_callback
        self.callback = callback
        super().__init__(masked_widget, window, title)

    def get_worker(self):
        return SendRequestWorker(self.method, *self.args)

    def success_post_process(self, *args):
        self.callback(*args)

    def fail_post_process(self):
        self.fail_callback()





