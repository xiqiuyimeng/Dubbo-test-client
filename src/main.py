# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from ui.main_window import MainWindow
_author_ = 'luwt'
_date_ = '2021/10/31 17:49'


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # 获取当前屏幕分辨率
    desktop = QtWidgets.QApplication.desktop()
    screen_rect = desktop.screenGeometry()
    # 主窗口
    ui = MainWindow(screen_rect)
    ui.show()
    app.exec_()
    sys.exit()
