# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie, QMoveEvent
from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget, QHBoxLayout

_author_ = 'luwt'
_date_ = '2021/11/18 14:48'


class LoadingMask:

    def __init__(self, masked_widget, masked_layout, movie: QMovie):
        self.masked_widget = masked_widget
        self.masked_layout = masked_layout
        self.movie = movie
        self.label = QLabel()
        self.label.setMovie(self.movie)
        # 尽可能的占满布局
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setScaledContents(True)
        self.masked_layout.addWidget(self.label)

    def start(self):
        self.movie.start()
        self.masked_widget.hide()

    def stop(self):
        self.movie.stop()
        self.label.hide()
        self.masked_widget.show()


class LoadingMaskWidget(QWidget):

    def __init__(self, parent, movie):
        super().__init__(parent)
        # 将遮罩层作为过滤器安装到调用者身上，也就实现了对于调用者的动作的监听
        parent.installEventFilter(self)
        self.parent_widget = parent
        self.set_size()
        self.label = QLabel()

        self.movie = movie
        self.label.setMovie(self.movie)
        self.label.setScaledContents(True)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowOpacity(0.8)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def start(self):
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.close()

    def eventFilter(self, widget, event):
        """过滤移动事件，让遮罩层跟随父窗口移动"""
        if widget == self.parent() and type(event) == QMoveEvent:
            self.move_with_parent()
            # 返回true，说明事件已处理，其他控件不会再处理
            return True
        # 交由其他控件处理
        return super().eventFilter(widget, event)

    def move_with_parent(self):
        """跟随父窗口移动，大小跟随父窗口大小"""
        self.move(self.parent().geometry().x(), self.parent().geometry().y())
        self.set_size()

    def set_size(self):
        self.setFixedSize(QSize(self.parent().geometry().width(),
                                self.parent().geometry().height()))
