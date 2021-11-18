# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal, QObject

_author_ = 'luwt'
_date_ = '2021/11/16 11:23'


class ConnectionWorker(QObject):

    connect_result = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        print(111)
        self.connect_result.emit("11")


class AsyncConnection(QObject):

    start_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        # 自定义线程工作对象
        self.worker = ConnectionWorker()
        # 初始化子线程
        self.thread = QThread()
        # 将自定义线程工作对象加入到子线程中
        self.worker.moveToThread(self.thread)
        # 通过信号槽启动线程处理函数
        self.start_signal.connect(self.worker.run)
        # 接收线程信号
        self.worker.connect_result.connect(self.call_back)

    def call_back(self, a):
        print(a)

    def start(self):
        # 子线程启动
        self.thread.start()
        # 发送信号，启动子线程处理函数
        self.start_signal.emit()

    def stop(self):
        # 停止子线程
        self.thread.quit()
        # 回收资源
        self.thread.wait()




