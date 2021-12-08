# -*- coding: utf-8 -*-
import json

from PyQt5.QtCore import pyqtSignal

from src.constant.tab_constant import RESULT_DISPLAY_JSON
from src.function.db.tab_sqlite import TabObj, TabSqlite
from src.ui.async_func.async_operate_abc import ConnWorker, LoadingMaskThreadWorkManager, ThreadWorkerABC, \
    ThreadWorkManagerABC, LoadingMaskWidgetThreadWorkManager, IconMovieThreadWorkManager

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
            stop_flag, tab_dict = self.queue.get()
            if stop_flag:
                break
            # 首先查询tab_id是否已存在，如果存在，则为更新操作
            tab = TabSqlite().select_by_tab_id(tab_dict.get("tab_id"))
            if tab.id:
                tab_dict["id"] = tab.id
                tab_obj = TabObj(**tab_dict)
                TabSqlite().update_selective(tab_obj)
                self.success_signal.emit(-1)
            else:
                tab_obj = TabObj(**tab_dict)
                tab_obj_id = TabSqlite().insert(tab_obj)
                self.success_signal.emit(tab_obj_id)


class TextBrowserWorker(ThreadWorkerABC):

    success_signal = pyqtSignal()

    def __init__(self, result_display_combo_box, text, result_browser):
        super().__init__()
        self.result_display_combo_box = result_display_combo_box
        self.text = text
        self.result_browser = result_browser

    def do_run(self):
        # 尝试json解析文本
        if self.result_display_combo_box.currentText() == RESULT_DISPLAY_JSON and self.text:
            # 如果解析出错，应该用原生展示
            try:
                json_format_result = json.dumps(json.loads(self.text), indent=4, ensure_ascii=False)
                self.result_browser.set_text(json_format_result)
            except:
                self.result_browser.set_text(self.text)
                self.result_display_combo_box.setCurrentIndex(0)
        else:
            self.result_browser.set_text(self.text)
        self.success_signal.emit()


class DelConnHistoryWorker(ThreadWorkerABC):

    success_signal = pyqtSignal(tuple)

    def __init__(self, conn_id):
        self.conn_id = conn_id
        super().__init__()

    def do_run(self):
        tab_ids = TabSqlite().select_tab_ids_by_conn_id(self.conn_id)
        TabSqlite().delete_by_conn_id(self.conn_id)
        self.success_signal.emit(tab_ids)


class DelServiceHistoryWorker(ThreadWorkerABC):

    success_signal = pyqtSignal(tuple)

    def __init__(self, conn_service_path):
        self.conn_service_path = conn_service_path
        super().__init__()

    def do_run(self):
        tab_ids = TabSqlite().select_tab_ids_like(self.conn_service_path)
        TabSqlite().delete_by_tab_ids(tab_ids)
        self.success_signal.emit(tab_ids)


class DelMethodHistoryWorker(ThreadWorkerABC):

    success_signal = pyqtSignal(str)

    def __init__(self, tab_id):
        self.tab_id = tab_id
        super().__init__()

    def do_run(self):
        TabSqlite().delete_by_tab_ids((self.tab_id, ))
        self.success_signal.emit(self.tab_id)


# ----------------------- thread worker manager -----------------------


class AsyncSendRequestManager(LoadingMaskThreadWorkManager):

    def __init__(self, fail_callback, callback, masked_widget, masked_layout, window, title, method, *args):
        self.method = method
        self.args = args
        self.fail_callback = fail_callback
        self.callback = callback
        super().__init__(masked_widget, masked_layout, window, title)

    def get_worker(self):
        return SendRequestWorker(self.method, *self.args)

    def success_post_process(self, *args):
        self.callback(*args)

    def fail_post_process(self):
        self.fail_callback()


class AsyncReadTabObjManager(LoadingMaskWidgetThreadWorkManager):

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

    def save_tab_obj(self, tab_dict, callback):
        self.callback = callback
        self.queue.put((False, tab_dict))

    def worker_quit(self):
        self.queue.put((True, None))
        super().worker_quit()

    def success_post_process(self, *args):
        self.callback(*args)


class AsyncDisplayTextBrowserManager(LoadingMaskThreadWorkManager):

    def __init__(self, result_display_combo_box, text, result_browser, callback, *args):
        self.result_display_combo_box = result_display_combo_box
        self.text = text
        self.result_browser = result_browser
        self.callback = callback
        super().__init__(result_browser, *args)

    def get_worker(self):
        return TextBrowserWorker(self.result_display_combo_box, self.text, self.result_browser)

    def success_post_process(self, *args):
        self.callback()


class AsyncDelConnHistoryManager(IconMovieThreadWorkManager):

    def __init__(self, conn_id, callback, *args):
        self.conn_id = conn_id
        self.callback = callback
        super().__init__(*args)

    def get_worker(self):
        return DelConnHistoryWorker(self.conn_id)

    def success_post_process(self, *args):
        self.callback(*args, self.window)


class AsyncDelServiceHistoryManager(IconMovieThreadWorkManager):

    def __init__(self, conn_service_path, callback, *args):
        self.conn_service_path = conn_service_path
        self.callback = callback
        super().__init__(*args)

    def get_worker(self):
        return DelServiceHistoryWorker(self.conn_service_path)

    def success_post_process(self, *args):
        self.callback(*args, self.window)


class AsyncDelMethodHistoryManager(IconMovieThreadWorkManager):

    def __init__(self, tab_id, callback, *args):
        self.tab_id = tab_id
        self.callback = callback
        super().__init__(*args)

    def get_worker(self):
        return DelMethodHistoryWorker(self.tab_id)

    def success_post_process(self, *args):
        self.callback(self.window.tab_widget, *args)
