# -*- coding: utf-8 -*-
from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal

from src.function.db.conn_sqlite import ConnSqlite, Connection
from src.function.db.opened_item_sqlite import OpenedItem, OpenedItemSqlite
from src.function.db.tab_sqlite import TabSqlite
from src.ui.async_func.async_operate_abc import LoadingMaskType, IconMovieType, ThreadWorkABC
from src.ui.box.message_box import pop_ok

_author_ = 'luwt'
_date_ = '2021/11/18 17:16'


# ----------------------- thread worker -----------------------

class ConnDBWorker(QThread):

    error_signal = pyqtSignal(str)
    success_signal = pyqtSignal(int, Connection)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.do_run()
            self.sync_opened_item()
            self.emit_signal()
        except Exception as e:
            self.error_signal.emit(str(e))

    def do_run(self): ...

    def sync_opened_item(self): ...

    def emit_signal(self): ...


class AddConnDBWorker(ConnDBWorker):

    def __init__(self, conn_info: Connection):
        super().__init__()
        self.conn_info = conn_info
        self.opened_id: int = ...

    def do_run(self):
        conn_id = ConnSqlite().insert(self.conn_info)
        self.conn_info = Connection(conn_id, *self.conn_info[1:])

    def sync_opened_item(self):
        opened_item = OpenedItem(None, None, None, None, False, False, self.conn_info.id, 0)
        self.opened_id = OpenedItemSqlite().insert(opened_item)

    def emit_signal(self):
        self.success_signal.emit(self.opened_id, self.conn_info)


class EditConnDBWorker(ConnDBWorker):

    def __init__(self, conn_info: Connection):
        super().__init__()
        self.conn_info = conn_info
        self.opened_id: int = ...

    def do_run(self):
        ConnSqlite().update_selective(self.conn_info)

    def emit_signal(self):
        self.success_signal.emit(None, self.conn_info)


class DelWorkerABC(QThread):

    error_signal = pyqtSignal(str)
    success_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.do_run()
        except Exception as e:
            self.error_signal.emit(str(e))

    def do_run(self): ...


class CloseConnDBWorker(DelWorkerABC):

    def __init__(self, parent_id, level):
        super().__init__()
        self.parent_id = parent_id
        self.level = level

    def do_run(self):
        # 获取应该被删除的tab order
        tab_orders = OpenedItemSqlite().get_tab_orders((self.parent_id,), self.level)
        # 根据父id递归删除
        OpenedItemSqlite().recursive_delete(self.parent_id, self.level)
        self.success_signal.emit(tab_orders if tab_orders else list())


class DelConnDBWorker(DelWorkerABC):

    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id

    def do_run(self):
        # 删除conn连接
        ConnSqlite().delete(self.conn_id)
        # 删除opened item
        OpenedItemSqlite().delete_by_parent(self.conn_id)
        # 删除tab
        TabSqlite().delete_by_conn_id(self.conn_id)
        # 发射空信号就可以
        self.success_signal.emit(list())


class CloseDelConnDBWorker(DelWorkerABC):

    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id

    def do_run(self):
        # 获取应该被删除的tab order
        tab_orders = OpenedItemSqlite().get_tab_orders((self.conn_id,))
        # 根据父id递归删除
        OpenedItemSqlite().recursive_delete(self.conn_id, 0)
        # 删除conn连接
        ConnSqlite().delete(self.conn_id)
        # 删除tab
        TabSqlite().delete_by_conn_id(self.conn_id)
        self.success_signal.emit(tab_orders if tab_orders else list())


class CheckNameConnDBWorker(QThread):

    error_signal = pyqtSignal(str)
    success_signal = pyqtSignal(bool, str)

    def __init__(self, conn_id, queue):
        super().__init__()
        self.conn_id = conn_id
        self.queue = queue

    def run(self):
        try:
            while True:
                stop_flag, conn_name = self.queue.get()
                if stop_flag:
                    break
                if conn_name:
                    name_available = ConnSqlite().check_name_available(self.conn_id, conn_name)
                    self.success_signal.emit(name_available, conn_name)
                else:
                    self.success_signal.emit(True, None)
        except Exception as e:
            self.error_signal.emit(str(e))


# ----------------------- thread worker 管理 -----------------------


class ConnDBABC(LoadingMaskType):

    def __init__(self, window, title, prompt):
        super().__init__(window, title)
        self.prompt = prompt

    def post_process(self):
        super().post_process()
        pop_ok(self.prompt, self.error_box_title, self.window)
        self.window.close()


class AsyncAddConnDB(ConnDBABC):

    def __init__(self, conn_info: Connection, tree_widget, callback, *args):
        self.conn_info = conn_info
        self.tree_widget = tree_widget
        self.callback = callback
        super().__init__(*args)

    def get_worker(self) -> ConnDBWorker:
        return AddConnDBWorker(self.conn_info)

    def success_post_process(self, opened_conn_id, conn_info):
        self.callback(self.tree_widget, conn_info, opened_conn_id)


class AsyncEditConnDB(ConnDBABC):

    def __init__(self, conn_info: Connection, tree_item, *args):
        self.conn_info = conn_info
        self.tree_item = tree_item
        super().__init__(*args)

    def get_worker(self) -> ConnDBWorker:
        return EditConnDBWorker(self.conn_info)

    def success_post_process(self, opened_conn_id, conn):
        self.tree_item.setText(2, dict(zip(conn._fields, conn)))
        self.tree_item.setText(0, conn.name)


# ----------------------- 关闭相关 -----------------------

class AsyncCloseConnDB(IconMovieType):

    def __init__(self, parent_id, level, callback, *args):
        self.parent_id = parent_id
        self.level = level
        self.callback = callback
        super().__init__(*args)

    def get_worker(self):
        return CloseConnDBWorker(self.parent_id, self.level)

    def success_post_process(self, *args):
        self.callback(*args, self.item, self.window.tab_widget)


class AsyncDelConnDB(IconMovieType):

    def __init__(self, conn_id, callback, tree_widget, *args):
        self.conn_id = conn_id
        self.callback = callback
        self.tree_widget = tree_widget
        super().__init__(*args)

    def get_worker(self):
        return DelConnDBWorker(self.conn_id)

    def success_post_process(self, *args):
        self.callback(self.item, self.tree_widget)


class AsyncCloseDelConnDB(IconMovieType):

    def __init__(self, conn_id, callback, *args):
        self.conn_id = conn_id
        self.callback = callback
        super().__init__(*args)

    def get_worker(self):
        return CloseDelConnDBWorker(self.conn_id)

    def success_post_process(self, *args):
        self.callback(self.item, self.window.tab_widget, self.window.tree_widget, *args)


class AsyncCheckNameConnDB(ThreadWorkABC):

    def __init__(self, conn_id, callback, *args):
        self.conn_id = conn_id
        self.callback = callback
        self.queue = Queue()
        self.worker_ = CheckNameConnDBWorker(self.conn_id, self.queue)
        super().__init__(*args)

    def get_worker(self):
        return self.worker_

    def check_name_available(self, conn_name):
        self.queue.put((False, conn_name))

    def success_post_process(self, *args):
        self.callback(*args)

    def quit(self):
        self.queue.put((True, None))
