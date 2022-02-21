# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt

from src.ui.searcher.dock.dock_widget import SearcherDockWidget
from src.ui.searcher.searcher_func.matcher_func import SmartMatcher
from src.ui.searcher.style_item_delegate.search_style_delegate import SearchStyledItemDelegate

_author_ = 'luwt'
_date_ = '2022/1/20 20:14'


letter_keys = [eval("Qt.Key_" + chr(i)) for i in range(65, 91)]
num_keys = [eval(f'Qt.Key_{i}') for i in range(10)]


def is_legal_key(key):
    return key in letter_keys or key in num_keys


class Searcher:
    """
    搜索功能，在树或者列表中搜索
    :param target 要搜索的目标，比如树，或者列表
    :param main_widget 主部件，用于停留dock窗口
    """
    def __init__(self, target, main_widget):
        self.target = target
        # dock 窗口
        self.dock_widget = SearcherDockWidget(main_widget)
        self.dock_widget.hide()
        self.search_item_dict = dict()
        self.match_item_records = list()
        # 给target设置视图代理对象
        self.target.setItemDelegate(SearchStyledItemDelegate(self.target,
                                                             self.search_item_dict,
                                                             self.match_item_records,
                                                             self.get_item_text))

    def handle_search(self, key, text, original_func, *args):
        # 如果是esc，清空相关容器
        if key == Qt.Key_Escape:
            self.clear_search()
        # 如果是正常输入的按键，进行搜索
        elif is_legal_key(key):
            self.search(text)
        elif key == Qt.Key_Backspace:
            self.backspace_search()
        else:
            # 处理不了的情况，交由调用方处理
            original_func(*args)
        # 设置焦点
        self.set_selected_focus()
        # 给子类一个处理特有逻辑的机会
        self.search_post_processor()
        # 渲染，触发界面绘制刷新
        self.target.viewport().update()

    def search_post_processor(self): ...

    def clear_search(self):
        # 容器清空
        self.search_item_dict.clear()
        self.match_item_records.clear()
        # 隐藏dock窗口
        self.dock_widget.hide()
        # 重置line edit
        self.dock_widget.line_edit.setText("")

    def backspace_search(self):
        if self.match_item_records:
            # 退格，删除字符，弹出容器最后一个元素
            self.dock_widget.line_edit.sub_text()
            pop_items = self.match_item_records.pop()
            # 弹出匹配到的元素索引
            [v.pop() for k, v in self.search_item_dict.items()
             for item in pop_items if k == id(item)]
            # 如果已经删除了所有字符，或者能匹配到，将输入框文本变为正常颜色
            if not self.match_item_records or self.match_item_records[-1]:
                self.dock_widget.line_edit.paint_right_color()

    def search(self, cur_text):
        match_items = list()
        # 当前搜索的文本，加上前面输入的
        text = self.dock_widget.line_edit.text() + cur_text
        # 如果搜索过，在当前的小范围内搜索
        if self.match_item_records:
            self.smart_match_text(text, match_items)
        else:
            # 如果还没搜索过，用迭代器，在所有节点中搜寻
            self.iterate_search(text, match_items)
        self.match_item_records.append(match_items)
        # 展示dock窗口
        self.dock_widget.show()
        self.dock_widget.line_edit.setText(text)
        # 如果匹配不到，把输入框文本变为错误颜色
        if not match_items:
            self.dock_widget.line_edit.paint_wrong_color()

    def simple_match_text(self, text, item, match_items):
        smart_matcher = SmartMatcher(text)
        result = smart_matcher.match(self.get_item_text(item))
        if result:
            # 将匹配成功的信息放入列表
            match_items.append(item)
            self.search_item_dict[id(item)] = [result]

    def smart_match_text(self, text, match_items):
        last_match_items = self.match_item_records[-1]
        # 构建搜索器
        smart_matcher = SmartMatcher(text)
        for item in last_match_items:
            match_result = smart_matcher.match(self.get_item_text(item))
            if match_result:
                # 匹配成功，添加匹配成功的元素
                match_items.append(item)
                self.search_item_dict.get(id(item)).append(match_result)

    def set_selected_focus(self):
        if self.match_item_records and self.match_item_records[-1]:
            self.target.set_selected_focus(self.match_item_records[-1][0])

    def expand_selected_items(self):
        """展开选中的元素"""
        if self.match_item_records and self.match_item_records[-1]:
            [item.setExpanded(True) for item in self.match_item_records[-1] if item.childCount()]

    def iterate_search(self, text, match_items): ...

    def get_item_text(self, item) -> str: ...


