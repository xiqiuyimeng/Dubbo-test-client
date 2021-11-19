# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from src.constant.conn_dialog_constant import SAVE_CONN_SUCCESS_PROMPT, ADD_CONN_MENU, EDIT_CONN_MENU
from src.function.db.conn_sqlite import ConnSqlite, Connection
from src.function.db.opened_item_sqlite import OpenedItem, OpenedItemSqlite
from src.function.db.tab_sqlite import TabSqlite
from src.ui.box.message_box import pop_fail, pop_ok
from src.ui.func.tree import add_conn_tree_item

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
        self.sync_opened_item()

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


class DelConnDBWorker(ConnDBWorker):

    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id

    def do_run(self):
        # 删除conn连接
        ConnSqlite().delete(self.conn_id)
        # 删除opened item中的连接
        OpenedItemSqlite().delete_by_parent(self.conn_id)
        # 删除tab
        TabSqlite().delete_by_conn_id(self.conn_id)

# ----------------------- thread worker 管理 -----------------------


class ConnDBABC(QObject):

    def __init__(self, window, title, prompt):
        super().__init__()
        self.window = window
        self.title = title
        self.prompt = prompt
        # 自定义线程工作对象
        self.worker = self.get_worker()

        self.worker.success_signal.connect(lambda opened_conn_id, conn:
                                           self.success(opened_conn_id, conn))
        self.worker.error_signal.connect(lambda error_msg: self.fail(error_msg))
        self.worker.start()

    def get_worker(self) -> ConnDBWorker: ...

    def success(self, opened_conn_id, conn):
        pop_ok(self.prompt, self.title, self.window)
        self.post_process(opened_conn_id, conn)

    def fail(self, error_msg):
        pop_fail(error_msg, self.title, self.window)

    def post_process(self, opened_conn_id, conn): ...


class AddConnDB(ConnDBABC):

    def __init__(self, conn_info: Connection, window, title, prompt, tree_widget):
        self.conn_info = conn_info
        self.tree_widget = tree_widget
        super().__init__(window, title, prompt)

    def get_worker(self) -> ConnDBWorker:
        return AddConnDBWorker(self.conn_info)

    def post_process(self, opened_conn_id, conn_info):
        self.window.close()
        add_conn_tree_item(self.tree_widget, conn_info, opened_conn_id)


class EditConnDB(ConnDBABC):

    def __init__(self, conn_info: Connection, window, title, prompt, tree_item):
        self.conn_info = conn_info
        self.tree_item = tree_item
        super().__init__(window, title, prompt)

    def get_worker(self) -> ConnDBWorker:
        return EditConnDBWorker(self.conn_info)

    def post_process(self, opened_conn_id, conn):
        self.window.close()
        self.tree_item.setText(2, dict(zip(conn._fields, conn)))
        self.tree_item.setText(0, conn.name)




