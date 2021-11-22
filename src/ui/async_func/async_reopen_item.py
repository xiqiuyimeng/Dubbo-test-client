# -*- coding: utf-8 -*-
"""
在重新启动软件过程中，实现异步读取数据机制，但是由于sqlite3不支持多线程下的操作，所以在读取tab数据时，
并没有用异步的形式，实际考虑，应该不会有太大影响，其余打开树结构的数据均采用异步形式
"""
from PyQt5.QtCore import pyqtSignal

from src.constant.main_constant import REOPEN_PROJECT_TITLE
from src.function.db.conn_sqlite import ConnSqlite
from src.function.db.opened_item_sqlite import OpenedItemSqlite
from src.ui.async_func.async_operate_abc import ThreadWorkerABC, IconMovieThreadWorkManager
from src.ui.func.tree import add_conn_tree_item, tree_node_factory, Context
from src.ui.scrollable_widget.scrollable_widget import MyTreeWidget
from src.ui.tab.tab_widget import MyTabWidget

_author_ = 'luwt'
_date_ = '2021/11/16 11:12'


class ReopenWorker(ThreadWorkerABC):

    # 定义重新打开结果信号，第一次应该返回 Connection list
    conns_result = pyqtSignal(list)
    # 后续返回 OpenedItem list
    opened_items_result = pyqtSignal(list)
    # 结束信号
    success_signal = pyqtSignal()

    def __init__(self, window, tree_widget):
        super().__init__()
        self.window = window
        self.tree_widget = tree_widget

    def do_run(self):
        # 首先查询连接列表
        conns = ConnSqlite().select_all()
        self.conns_result.emit(conns)
        # 查询 OpenedItem
        for conn in conns:
            # 从OpenedItem中查询连接，正常来说，一定可以查到，并且应该只有一条数据
            self.recursive_get_children(0, conn.id)

    def do_finally(self):
        # 任务结束发射结束信号
        self.success_signal.emit()

    def recursive_get_children(self, level, parent_id):
        if level <= 3:
            opened_items = self.get_children(level, parent_id)
            if opened_items:
                [self.recursive_get_children(level + 1, opened_item.id) for opened_item in opened_items]

    def get_children(self, level, parent_id):
        opened_items = OpenedItemSqlite().select_children(parent_id, level)
        if opened_items:
            self.opened_items_result.emit(opened_items)
            return opened_items


class AsyncReopenManager(IconMovieThreadWorkManager):

    def __init__(self, window, tree_widget: MyTreeWidget, tab_widget: MyTabWidget):
        self.tree_widget = tree_widget
        super().__init__(tree_widget.headerItem(), window, REOPEN_PROJECT_TITLE)
        self.tab_widget = tab_widget
        self.tab_widget.reopen_flag = True

        # 临时变量，key为conn id，value为conn item
        self.conn_item_dict = dict()
        # 打开项的临时变量，key为opened item id，value为(item, expanded)
        self.opened_item_dict = dict()
        # 接收线程信号
        self.worker.conns_result.connect(self.make_connections)
        self.worker.opened_items_result.connect(self.make_opened_items)

    def get_worker(self):
        return ReopenWorker(self.window, self.tree_widget)

    def make_connections(self, conns):
        # 构建连接层
        for conn in conns:
            conn_item = add_conn_tree_item(self.tree_widget, conn)
            self.conn_item_dict[conn.id] = conn_item

    def set_id_expanded(self, opened_items):
        for opened_item in opened_items:
            # 将opened item中保存的连接id写入item的隐藏列，构建打开字典，key为opened item id，value为(item, expanded)
            item = self.conn_item_dict[opened_item.parent_id]
            item.setText(1, opened_item.id)
            self.opened_item_dict[opened_item.id] = (item, opened_item.expanded)

    def make_opened_items(self, opened_items):
        level = opened_items[0].level
        # 如果是连接，那么只需要设置下id和expanded
        if level == 0:
            self.set_id_expanded(opened_items)
        # 如果是其他类型，按策略来执行
        else:
            self.reopen_item(opened_items)

    def reopen_item(self, opened_items):
        # item_value 为 (item, expanded)
        item_value = self.opened_item_dict.get(opened_items[0].parent_id)
        node = tree_node_factory(item_value[0])
        Context(node).reopen_item(item_value[0], opened_items, self.opened_item_dict,
                                  item_value[1], self.tab_widget)

    def success_post_process(self, *args):
        # 按顺序排列tab
        self.tab_widget.insert_tab_by_order()
        self.tab_widget.reopen_flag = False
        # 删除临时变量
        del self.conn_item_dict
        del self.opened_item_dict



