# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QMovie, QIcon

from src.constant.main_constant import TEST_CONN_MENU, SUCCESS_TEST_PROMPT
from src.function.db.conn_sqlite import Connection
from src.function.dubbo.dubbo_client import DubboClient
from src.ui.box.message_box import pop_ok, pop_fail
from src.ui.loading_mask.loading_widget import LoadingMask
from src.ui.tree_item.my_tree_item import MyTreeWidgetItem

_author_ = 'luwt'
_date_ = '2021/11/16 11:23'


# ----------------------- thread worker -----------------------


class ConnWorker(QThread):

    error_signal = pyqtSignal(str)
    success_signal: pyqtSignal = ...

    def __init__(self, host, port, timeout):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout

    def run(self):
        try:
            self.do_run()
        except Exception as e:
            self.error_signal.emit(str(e))

    def do_run(self): ...


class TestConnWorker(ConnWorker):

    success_signal = pyqtSignal()

    def __init__(self, host, port, timeout):
        super().__init__(host, port, timeout)

    def do_run(self):
        DubboClient(self.host, self.port, self.timeout).test_connection()
        self.success_signal.emit()


# ----------------------- thread worker 管理 -----------------------


class TestConnABC(QObject):

    def __init__(self, host, port, timeout, window=None):
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout
        self.window = window

        self.test_pre_process()
        # 自定义线程工作对象
        self.worker = TestConnWorker(self.host, self.port, self.timeout)
        self.worker.success_signal.connect(lambda: self.test_success())
        self.worker.error_signal.connect(lambda error_msg: self.test_fail(error_msg))
        self.worker.start()

    def test_success(self):
        self.test_post_process()
        self.test_success_post_process()

    def test_fail(self, error_msg):
        self.test_post_process()
        pop_fail(error_msg, TEST_CONN_MENU, self.window)

    def test_pre_process(self): ...

    def test_post_process(self): ...

    def test_success_post_process(self): ...


class TestConn(TestConnABC):

    def __init__(self, window, conn_info: Connection):
        self.window = window
        self.conn_info = conn_info
        self.movie = QMovie(":/gif/loading.gif")
        super().__init__(*(conn_info[2:]), window)

    def test_pre_process(self):
        self.loading_mask = LoadingMask(self.window, self.movie)
        self.loading_mask.show()

    def test_post_process(self):
        self.loading_mask.close()

    def test_success_post_process(self):
        pop_ok(SUCCESS_TEST_PROMPT, TEST_CONN_MENU, self.window)


class SimpleTestConn(TestConnABC):

    def __init__(self, host, port, timeout, item: MyTreeWidgetItem):
        self.item = item
        self.movie = QMovie(":/gif/loading_simple.gif")
        self.icon = self.item.icon(0)
        super().__init__(host, port, timeout)

    def test_pre_process(self):
        self.movie.start()
        self.movie.frameChanged.connect(lambda: self.item.setIcon(0, QIcon(self.movie.currentPixmap())))

    def test_post_process(self):
        self.movie.stop()
        self.item.setIcon(0, self.icon)





