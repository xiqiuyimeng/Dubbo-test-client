# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

from static import image_rc
from src.ui.main_window import MainWindow
_author_ = 'luwt'
_date_ = '2021/10/31 17:49'


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # 设置任务栏图标
    app.setWindowIcon(QIcon(":/icon/exec.png"))
    # 获取当前屏幕分辨率
    desktop = QtWidgets.QApplication.desktop()
    screen_rect = desktop.screenGeometry()
    # 主窗口
    ui = MainWindow(screen_rect)
    ui.show()
    app.exec_()
    sys.exit()
