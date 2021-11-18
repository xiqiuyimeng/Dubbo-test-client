# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QMovie, QIcon

from src.function.db.conn_sqlite import ConnSqlite
from src.function.db.opened_item_sqlite import OpenedItemSqlite
from src.ui.box.message_box import pop_fail
from src.ui.func.tree import add_conn_tree_item, tree_node_factory, Context
from src.ui.scrollable_widget.scrollable_widget import MyTreeWidget
from src.ui.tab.tab_widget import MyTabWidget

_author_ = 'luwt'
_date_ = '2021/11/16 11:12'


class ReopenWorker(QThread):

    # 定义重新打开结果信号，第一次应该返回 Connection list
    conns_result = pyqtSignal(list)
    # 后续返回 OpenedItem list
    opened_items_result = pyqtSignal(list)
    # 错误信号
    error_signal = pyqtSignal(Exception)
    # 结束信号
    finish_signal = pyqtSignal()

    def __init__(self, window, tree_widget):
        super().__init__()
        self.window = window
        self.tree_widget = tree_widget

    def run(self):
        try:
            # 首先查询连接列表
            conns = ConnSqlite().select_all()
            self.conns_result.emit(conns)
            1/0
            # 查询 OpenedItem
            for conn in conns:
                # 从OpenedItem中查询连接，正常来说，一定可以查到，并且应该只有一条数据
                self.recursive_get_children(0, conn.id)
        except Exception as e:
            print(e)
            self.error_signal.emit(e)
        finally:
            # 任务结束发射结束信号
            self.finish_signal.emit()

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


class AsyncReopen(QObject):

    def __init__(self, window, tree_widget: MyTreeWidget, tab_widget: MyTabWidget):
        super().__init__()
        self.window = window
        self.tree_widget = tree_widget
        self.tab_widget = tab_widget
        self._movie = QMovie(":/gif/loading_simple.gif")
        self.header_item = self.tree_widget.headerItem()
        self.icon = self.header_item.icon(0)

        # 临时变量，key为conn id，value为conn item
        self.conn_item_dict = dict()
        # 打开项的临时变量，key为opened item id，value为(item, expanded)
        self.opened_item_dict = dict()

        # 自定义线程工作对象
        self.worker = ReopenWorker(self.window, self.tree_widget)
        # 接收线程信号
        self.worker.conns_result.connect(lambda conns: self.make_connections(conns))
        self.worker.opened_items_result.connect(lambda opened_items: self.make_opened_items(opened_items))
        self.worker.error_signal.connect(lambda e: self.handle_error(e))
        self.worker.finish_signal.connect(lambda: self.finish_reopen())

    def handle_error(self, exception):
        pop_fail(exception.args[0], self.window)

    def reopen_item_start(self):
        self.tab_widget.reopen_flag = True
        self._movie.start()
        self._movie.frameChanged.connect(lambda: self.header_item.setIcon(0, QIcon(self._movie.currentPixmap())))
        # 开启线程
        self.worker.start()

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

    def finish_reopen(self):
        # 按顺序排列tab
        self.tab_widget.insert_tab_by_order()
        self.tab_widget.reopen_flag = False
        self._movie.stop()
        self.header_item.setIcon(0, self.icon)
        # 删除临时变量
        del self.conn_item_dict
        del self.opened_item_dict



