# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPalette, QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QStyledItemDelegate, QStyle, QApplication

_author_ = 'luwt'
_date_ = '2021/12/10 16:59'


class Header(QtWidgets.QHeaderView):
    def __init__(self, orientation, parent=None):
        super(Header, self).__init__(orientation, parent)
        self.button = QtWidgets.QPushButton('按钮', self)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.button)


class TreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super(TreeWidget, self).__init__(parent)
        item0 = QtWidgets.QTreeWidgetItem(self)
        item0.setText(0, "dev")
        item0.setText(1, "hidden_dev")
        item1 = QtWidgets.QTreeWidgetItem(item0)
        item1.setText(0, "sub")
        item1 = QtWidgets.QTreeWidgetItem(self)
        item1.setText(0, "stall")
        item1 = QtWidgets.QTreeWidgetItem(self)
        item1.setText(0, "test")
        item1 = QtWidgets.QTreeWidgetItem(self)
        item1.setText(0, "uc")
        self.headerItem().setHidden(True)

        self.search_items = list()
        self.search_text = list()

    def paintEvent(self, e: QtGui.QPaintEvent):
        super().paintEvent(e)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        self.setItemDelegate(MyDelegate(self, self.search_items))
        if event.text() == Qt.Key_Escape:
            pass
        else:
            self.search_text.append(event.text())
            iterator = QtWidgets.QTreeWidgetItemIterator(self)
            while iterator.value():
                item = iterator.value()
                if item.text(0).__contains__(event.text()):
                    print(item.text(0))
                    self.search_items.append(item)
                iterator = iterator.__iadd__(1)

    def createHeader(self):
        header = Header(Qt.Horizontal, self)
        self.setHeader(header)


class MyDelegate(QStyledItemDelegate):

    def __init__(self, parent: QtWidgets.QTreeWidget, search_items: list):
        self.items = search_items
        self.parent = parent
        super().__init__(parent)

    def paint(self, painter, option, index):
        # 将当前的painter暂存
        painter.save()
        widget = option.widget
        # 获取当前style
        style = widget.style()
        # 获取当前painter像素
        font_metrics = painter.fontMetrics()
        idx_str = index.model().data(index, Qt.DisplayRole)
        print(idx_str)

        item = self.parent.itemFromIndex(index)
        if item not in self.items:
            super(MyDelegate, self).paint(painter, option, index)
        else:
            # 获取item的rect
            item_rect = style.subElementRect(QStyle.SE_ItemViewItemText, option, widget)
            opt_h = option.rect.height()
            painter.translate(option.rect.x() / 4, option.rect.y() / 2)
            painter.setFont(QApplication.font(widget))
            original_color = option.palette.brush(QPalette.Text).color()
            self.text = self.parent.search_text[0]
            # # 找到搜索的文本在文本中的位置
            text_idx = idx_str.index(self.text) if self.text in idx_str else 0
            # # 获取搜索文本的像素宽度
            text_width = font_metrics.width(self.text)
            # 整体文本的像素宽度
            option_text_width = font_metrics.width(option.text)
            # 匹配到文字的左边像素宽度
            left_text_width = font_metrics.width(idx_str[:text_idx])
            painter.setPen(Qt.blue)
            painter.drawText(option.rect.x(), option.rect.y(), self.text)
            painter.setPen(original_color)
            painter.drawText(option.rect.x() + left_text_width, option.rect.y(), idx_str[:text_idx])
            painter.drawText(option.rect.x() + left_text_width, option.rect.y(), idx_str[text_idx + 1:])
            # 处理第一列
            # if index.column() == 0:
            #
            # painter.setBackground(QBrush(Qt.green))
            # # 不透明模式OpaqueMode，默认为透明
            # painter.setBackgroundMode(Qt.OpaqueMode)
            # super(MyDelegate, self).paint(painter, option, index)
            # 弹出刚才保存的painter
        painter.restore()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = TreeWidget()
    w.show()
    sys.exit(app.exec_())
