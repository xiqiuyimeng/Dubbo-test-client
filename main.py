# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from src.ui.splash_screen.gif_splash_screen import GifSplashScreen
from static import image_rc
from src.ui.main_window import MainWindow
_author_ = 'luwt'
_date_ = '2021/10/31 17:49'


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    splash = GifSplashScreen(":/gif/loading.gif")
    splash.showMessage("加载中...", Qt.AlignHCenter | Qt.AlignBottom)
    # 显示启动界面
    splash.show()
    QtWidgets.qApp.processEvents()
    # 设置任务栏图标
    app.setWindowIcon(QIcon(":/icon/exec.png"))
    # 获取当前屏幕分辨率
    desktop = QtWidgets.QApplication.desktop()
    screen_rect = desktop.screenGeometry()
    # 主窗口
    ui = MainWindow(screen_rect)
    ui.show()
    splash.finish(ui)
    app.exec_()
    sys.exit()
