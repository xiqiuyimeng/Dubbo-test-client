# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItemIterator

from src.ui.searcher.searcher_func.searcher import Searcher

_author_ = 'luwt'
_date_ = '2022/1/21 09:53'


class TreeSearcher(Searcher):

    def __init__(self, target_tree: QTreeWidget, main_widget):
        super().__init__(target_tree, main_widget)

    def iterate_search(self, text, match_items):
        iterator = QTreeWidgetItemIterator(self.target)
        while iterator.value():
            item = iterator.value()
            # 简单搜索，单字符匹配，确定范围
            self.simple_match_text(text, item, match_items)
            iterator = iterator.__iadd__(1)

    def get_item_text(self, item):
        return item.text(0)
