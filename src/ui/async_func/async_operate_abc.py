# -*- coding: utf-8 -*-
"""
定义打开线程操作管理基类，方便子类使用
"""
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtWidgets import QTreeWidgetItem

from src.ui.box.message_box import pop_fail
from src.ui.loading_mask.loading_widget import LoadingMask

_author_ = 'luwt'
_date_ = '2021/11/21 15:44'


# ----------------------- thread worker ABC -----------------------


class ThreadWorkerABC(QThread):

    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.do_run()
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.do_finally()

    def do_run(self): ...

    def do_finally(self): ...


# ----------------------- thread worker manager ABC -----------------------


class ThreadWorkABC(QObject):

    def __init__(self, window, error_box_title):
        super().__init__()
        self.window = window
        self.error_box_title = error_box_title

        self.pre_process()
        # 自定义线程工作对象
        self.worker = self.get_worker()
        self.worker.error_signal.connect(lambda error_msg: self.fail(error_msg))
        self.worker.success_signal.connect(lambda *args: self.success(*args))

    def start(self):
        self.worker.start()

    def success(self, *args):
        self.post_process()
        self.success_post_process(*args)

    def fail(self, error_msg):
        self.post_process()
        pop_fail(error_msg, self.error_box_title, self.window)

    def pre_process(self): ...

    def get_worker(self) -> QThread: ...

    def post_process(self): ...

    def success_post_process(self, *args): ...


class LoadingMaskType(ThreadWorkABC):

    def __init__(self, *args):
        self.movie = QMovie(":/gif/loading.gif")
        self.loading_mask: LoadingMask = ...
        super().__init__(*args)

    def pre_process(self):
        self.loading_mask = LoadingMask(self.window, self.movie)
        self.loading_mask.show()

    def post_process(self):
        self.loading_mask.close()


class IconMovieType(ThreadWorkABC):

    def __init__(self, item: QTreeWidgetItem, *args):
        self.item = item
        self.movie = QMovie(":/gif/loading_simple.gif")
        self.icon = self.item.icon(0)
        super().__init__(*args)

    def pre_process(self):
        self.movie.start()
        self.movie.frameChanged.connect(lambda: self.item.setIcon(0, QIcon(self.movie.currentPixmap())))

    def post_process(self):
        self.movie.stop()
        self.item.setIcon(0, self.icon)