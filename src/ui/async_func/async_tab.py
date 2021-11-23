# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal

from src.function.db.tab_sqlite import TabObj, TabSqlite
from src.ui.async_func.async_operate_abc import ConnWorker, LoadingMaskThreadWorkManager, ThreadWorkerABC, \
    ThreadWorkManagerABC

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


class ReadTabObjWorker(ThreadWorkerABC):

    success_signal = pyqtSignal(TabObj)

    def __init__(self, tab_id):
        super().__init__()
        self.tab_id = tab_id

    def do_run(self):
        tab_obj = TabSqlite().select_by_tab_id(self.tab_id)
        self.success_signal.emit(tab_obj)


class SaveTabObjWorker(ThreadWorkerABC):

    success_signal = pyqtSignal(int)

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def do_run(self):
        while True:
            stop_flag, tab_obj = self.queue.get()
            if stop_flag:
                break
            if tab_obj.id:
                TabSqlite().update_selective(tab_obj)
                self.success_signal.emit(-1)
            else:
                tab_obj_id = TabSqlite().insert(tab_obj)
                self.success_signal.emit(tab_obj_id)


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


class AsyncReadTabObjManager(LoadingMaskThreadWorkManager):

    def __init__(self, tab_id, callback, *args):
        self.tab_id = tab_id
        self.callback = callback
        super().__init__(*args)

    def get_worker(self):
        return ReadTabObjWorker(self.tab_id)

    def success_post_process(self, *args):
        self.callback(*args)


class AsyncSaveTabObjManager(ThreadWorkManagerABC):

    def __init__(self, queue, *args):
        self.queue = queue
        self.callback = ...
        super().__init__(*args)

    def get_worker(self):
        return SaveTabObjWorker(self.queue)

    def save_tab_obj(self, tab_obj, callback):
        self.callback = callback
        self.queue.put((False, tab_obj))

    def quit(self):
        self.queue.put((True, None))

    def success_post_process(self, *args):
        self.callback(*args)

