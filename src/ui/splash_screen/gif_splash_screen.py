# -*- coding: utf-8 -*-
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QSplashScreen

_author_ = 'luwt'
_date_ = '2021/12/5 17:07'


class GifSplashScreen(QSplashScreen):

    def __init__(self, movie):
        self.movie = QMovie(movie)
        self.timer = QTimer()
        super().__init__()

    def update_pixmap(self):
        self.setPixmap(self.movie.currentPixmap().scaled(600, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setMask(self.pixmap().mask())
        self.repaint()

    def show(self):
        self.timer.setInterval(100)
        self.timer.timeout.connect(lambda: self.update_pixmap())
        self.movie.start()
        self.timer.start()
        super().show()

    def finish(self, w):
        self.timer.stop()
        self.movie.stop()
        super().finish(w)
