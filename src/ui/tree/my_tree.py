# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QTreeWidget

from src.constant.main_constant import SYNC_ITEM_EXPANDED
from src.ui.async_func.async_conn_db import AsyncUpdateExpandedManager
from src.ui.searcher.smart_items_view.smart_items_view import SmartSearcherTreeWidget

_author_ = 'luwt'
_date_ = '2021/12/10 12:48'


class MyTreeWidget(QTreeWidget, SmartSearcherTreeWidget):

    def __init__(self, parent, window):
        super().__init__(parent)
        self.window = window
        self.update_expanded_manager = ...
        self.tab_id_splits = ...

    def update_expanded(self, opened_item_id, expanded, item):
        self.update_expanded_manager = AsyncUpdateExpandedManager(opened_item_id, expanded, item,
                                                                  self.window, SYNC_ITEM_EXPANDED)
        self.update_expanded_manager.start()

    def tree_column_resize(self):
        """树节点打开或关闭，都应该重新设置，这样能保证列跟随内容变化，也就是可以随内容自动添加或去掉水平滚动条"""
        self.resizeColumnToContents(0)

    def recursive_search_item(self, parent, level=1):
        """搜索符合条件的方法节点"""
        for idx in range(parent.childCount()):
            item = parent.child(idx)
            if item.text(0) == self.tab_id_splits[level]:
                # level = 2，搜索到了方法节点
                if level == 2:
                    return item
                return self.recursive_search_item(item, level + 1)

