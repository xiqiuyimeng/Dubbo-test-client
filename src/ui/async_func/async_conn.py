# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal

from src.constant.main_constant import TEST_CONN_MENU, OPEN_CONN_MENU, OPEN_SERVICE_MENU, \
    OPEN_METHOD_MENU, SUCCESS_TEST_PROMPT
from src.function.db.conn_sqlite import Connection
from src.function.db.opened_item_sqlite import OpenedItem, OpenedItemSqlite
from src.ui.async_func.async_operate_abc import LoadingMaskThreadWorkManager, IconMovieThreadWorkManager, ThreadWorkerABC, ConnWorker
from src.ui.box.message_box import pop_ok

_author_ = 'luwt'
_date_ = '2021/11/16 11:23'


# ----------------------- thread worker -----------------------


class TestConnWorker(ConnWorker):

    success_signal = pyqtSignal()

    def __init__(self, *args):
        super().__init__(*args)

    def do_work(self):
        self.client.test_connection()
        self.success_signal.emit()


class OpenItemChildrenWorker(ConnWorker):

    success_signal = pyqtSignal(list)

    def __init__(self, saved_id, *args):
        super().__init__(*args)
        self.saved_id = saved_id
        self.result = list()

    def do_work(self):
        data = self.get_data()
        if data:
            self.deal_data(data)
            # 更新当前连接节点的expanded状态
            OpenedItemSqlite().update_expanded(self.saved_id, True)
        self.success_signal.emit(self.result)

    def get_data(self) -> list: ...

    def deal_data(self, data): ...


class OpenConnWorker(OpenItemChildrenWorker):

    def __init__(self, *args):
        super().__init__(*args)

    def get_data(self) -> list:
        return self.client.get_service_list()

    def deal_data(self, data):
        # 在opened item中保存下
        for service in data:
            saved_service_item = OpenedItem(None, service, None, None, False, False, self.saved_id, 1)
            saved_service_id = OpenedItemSqlite().insert(saved_service_item)
            self.result.append((service, saved_service_id))


class OpenServiceWorker(OpenItemChildrenWorker):

    def __init__(self, service_name, *args):
        super().__init__(*args)
        self.service_name = service_name

    def get_data(self) -> list:
        return self.client.get_method_list(self.service_name)

    def deal_data(self, data):
        for method_dict in data:
            method_name = method_dict.get("method_name")
            # 保存子节点信息
            saved_method_item = OpenedItem(None, method_name, str(method_dict), None, False, False, self.saved_id, 2)
            saved_method_id = OpenedItemSqlite().insert(saved_method_item)
            self.result.append((method_dict, saved_method_id))
            
            
class OpenMethodWorker(ThreadWorkerABC):
    
    success_signal = pyqtSignal(int)
    
    def __init__(self, tab_id, order, method_id):
        super().__init__()
        self.tab_id = tab_id
        self.order = order
        self.method_id = method_id
        
    def do_run(self):
        # 从库中读取 opened item
        opened_tab_info = OpenedItemSqlite().select_by_name(self.tab_id)
        if opened_tab_info:
            self.success_signal.emit(opened_tab_info.item_order)
        else:
            # 存库
            tab_item = OpenedItem(None, self.tab_id, None, self.order, True, False, self.method_id, 3)
            OpenedItemSqlite().add_tab(tab_item)
            self.success_signal.emit(-1)


# ----------------------- thread worker manager -----------------------
# ----------------------- 测试连接相关 -----------------------


class AsyncTestConnManager(LoadingMaskThreadWorkManager):

    def __init__(self, window, conn_info: Connection):
        self.conn_info = conn_info
        super().__init__(window, TEST_CONN_MENU)

    def get_worker(self):
        return TestConnWorker(*self.conn_info[2:])

    def success_post_process(self):
        pop_ok(SUCCESS_TEST_PROMPT, self.error_box_title, self.window)


class AsyncSimpleTestConnManager(IconMovieThreadWorkManager):

    def __init__(self, item, conn_info, window):
        self.conn_info = conn_info
        super().__init__(item, window, TEST_CONN_MENU)

    def get_worker(self):
        return TestConnWorker(*self.conn_info[2:])


# ----------------------- 打开相关 -----------------------


class AsyncOpenItemChildrenManager(IconMovieThreadWorkManager):

    def __init__(self, saved_id, callback, item, *args):
        self.saved_id = saved_id
        self.callback = callback
        super().__init__(item, *args)

    def success_post_process(self, *args):
        self.callback(*args, self.item)


class AsyncOpenConnManager(AsyncOpenItemChildrenManager):

    def __init__(self, conn_info, *args):
        self.conn_info = conn_info
        super().__init__(*args, OPEN_CONN_MENU)

    def get_worker(self):
        return OpenConnWorker(self.saved_id, *self.conn_info)


class AsyncOpenServiceManager(AsyncOpenItemChildrenManager):

    def __init__(self, conn_info, service_name, *args):
        self.conn_info = conn_info
        self.service_name = service_name
        super().__init__(*args, OPEN_SERVICE_MENU)

    def get_worker(self):
        return OpenServiceWorker(self.service_name, self.saved_id, *self.conn_info)


class AsyncOpenMethodManager(IconMovieThreadWorkManager):

    def __init__(self, item, window, tab_id, order, method_id, callback):
        self.tab_id = tab_id
        self.order = order
        self.method_id = method_id
        self.callback = callback
        super().__init__(item, window, OPEN_METHOD_MENU)

    def get_worker(self):
        return OpenMethodWorker(self.tab_id, self.order, self.method_id)

    def success_post_process(self, *args):
        self.callback(*args, self.item, self.window.tab_widget, self.tab_id)

