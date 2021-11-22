# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QDialog

from src.constant.conn_dialog_constant import EDIT_CONN_MENU, ADD_CONN_MENU, SAVE_CONN_SUCCESS_PROMPT
from src.function.db.conn_sqlite import Connection
from src.ui.async_func.async_conn import AsyncTestConn
from src.ui.async_func.async_conn_db import AsyncAddConnDB, AsyncEditConnDB, \
    AsyncCheckNameConnDB
from src.ui.func.common import keep_center
from src.ui.func.tree import add_conn_tree_item

_author_ = 'luwt'
_date_ = '2021/10/31 21:42'


class ConnDialog(QDialog):

    def __init__(self, connection, dialog_title, screen_rect, tree_widget=None, tree_item=None):
        super().__init__()
        self.dialog_title = dialog_title
        self.connection = connection
        self._translate = QCoreApplication.translate
        self.main_screen_rect = screen_rect
        self.tree_widget = tree_widget
        self.tree_item = tree_item
        self.name_available = False

        self.setObjectName("conn_dialog")
        # 垂直布局的frame
        self.verticalLayout_frame = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_frame.setObjectName("verticalLayout_frame")
        self.conn_frame = QtWidgets.QFrame(self)
        self.conn_frame.setObjectName("conn_frame")
        self.conn_verticalLayout = QtWidgets.QVBoxLayout(self.conn_frame)
        self.conn_verticalLayout.setObjectName("conn_verticalLayout")
        # 表格布局
        self.conn_gridLayout = QtWidgets.QGridLayout()
        self.conn_gridLayout.setObjectName("conn_gridLayout")
        # 连接名称
        self.conn_name = QtWidgets.QLabel(self.conn_frame)
        self.conn_name.setObjectName("conn_name")
        self.conn_gridLayout.addWidget(self.conn_name, 0, 0, 1, 1)
        self.grid_layout_blank = QtWidgets.QLabel(self.conn_frame)
        self.grid_layout_blank.setObjectName("grid_layout_blank")
        self.conn_gridLayout.addWidget(self.grid_layout_blank, 0, 1, 1, 1)
        self.conn_name_value = QtWidgets.QLineEdit(self.conn_frame)
        self.conn_name_value.setObjectName("conn_name_value")
        self.conn_gridLayout.addWidget(self.conn_name_value, 0, 2, 1, 1)
        # 检查名称是否可用的提示行
        self.name_check_blank = QtWidgets.QLabel(self.conn_frame)
        self.name_check_blank.setObjectName("name_check_blank")
        self.conn_gridLayout.addWidget(self.name_check_blank, 1, 0, 1, 2)
        self.name_check_prompt = QtWidgets.QLabel(self.conn_frame)
        self.name_check_prompt.setObjectName("name_check_prompt")
        self.conn_gridLayout.addWidget(self.name_check_prompt, 1, 2, 1, 1)
        # host
        self.host = QtWidgets.QLabel(self.conn_frame)
        self.host.setObjectName("host")
        self.conn_gridLayout.addWidget(self.host, 2, 0, 1, 1)
        self.host_value = QtWidgets.QLineEdit(self.conn_frame)
        self.host_value.setObjectName("host_value")
        self.conn_gridLayout.addWidget(self.host_value, 2, 2, 1, 1)
        # port
        self.port = QtWidgets.QLabel(self.conn_frame)
        self.port.setObjectName("port")
        self.conn_gridLayout.addWidget(self.port, 3, 0, 1, 1)
        self.port_value = QtWidgets.QLineEdit(self.conn_frame)
        self.port_value.setObjectName("port_value")
        self.conn_gridLayout.addWidget(self.port_value, 3, 2, 1, 1)
        # timeout
        self.timeout = QtWidgets.QLabel(self.conn_frame)
        self.timeout.setObjectName("timeout")
        self.conn_gridLayout.addWidget(self.timeout, 5, 0, 1, 1)
        self.timeout_value = QtWidgets.QLineEdit(self.conn_frame)
        self.timeout_value.setObjectName("timeout_value")
        self.conn_gridLayout.addWidget(self.timeout_value, 5, 2, 1, 1)

        # 按钮布局
        self.conn_btn_gridLayout = QtWidgets.QGridLayout()
        self.conn_btn_gridLayout.setObjectName("conn_btn_gridLayout")
        # 测试连接按钮
        self.test_conn_btn = QtWidgets.QPushButton(self.conn_frame)
        self.test_conn_btn.setObjectName("test_conn_btn")
        self.conn_btn_gridLayout.addWidget(self.test_conn_btn, 0, 0, 1, 1)

        self.btn_blank = QtWidgets.QLabel(self.conn_frame)
        self.conn_btn_gridLayout.addWidget(self.btn_blank, 0, 1, 1, 1)
        # 确定按钮
        self.ok_btn = QtWidgets.QPushButton(self.conn_frame)
        self.ok_btn.setObjectName("ok_btn")
        self.conn_btn_gridLayout.addWidget(self.ok_btn, 0, 2, 1, 1)
        # 取消按钮
        self.cancel_btn = QtWidgets.QPushButton(self.conn_frame)
        self.cancel_btn.setObjectName("cancel_btn")
        self.conn_btn_gridLayout.addWidget(self.cancel_btn, 0, 3, 1, 1)

        self.setup_ui()
        self.bind_action()
        self.translate_ui()

        self.add_conn_worker: AsyncAddConnDB = ...
        self.edit_conn_worker: AsyncEditConnDB = ...
        self.async_check_name = AsyncCheckNameConnDB(self.connection.id,
                                                     self.check_name_available, self, self.dialog_title)
        self.async_check_name.start()

    def setup_ui(self):
        # 当前窗口大小根据主窗口大小计算
        self.resize(self.main_screen_rect.width() * 0.3, self.main_screen_rect.height() * 0.3)
        # 对话框相对主窗口居中
        keep_center(self, self.main_screen_rect)
        self.conn_verticalLayout.addLayout(self.conn_gridLayout)
        self.conn_verticalLayout.addLayout(self.conn_btn_gridLayout)
        self.verticalLayout_frame.addWidget(self.conn_frame)

        # 设置tab键的顺序
        self.setTabOrder(self.conn_name_value, self.host_value)
        self.setTabOrder(self.host_value, self.port_value)
        self.setTabOrder(self.port_value, self.timeout_value)
        # 设置端口号只能输入数字
        self.port_value.setValidator(QtGui.QIntValidator())
        # 设置最多可输入字符数
        self.conn_name_value.setMaxLength(50)
        self.host_value.setMaxLength(100)
        self.timeout_value.setMaxLength(20)

    def bind_action(self):
        # 输入框事件绑定
        self.conn_name_value.textEdited.connect(lambda conn_name:
                                                self.async_check_name.check_name_available(conn_name))
        self.conn_name_value.textEdited.connect(self.check_input)
        self.host_value.textEdited.connect(self.check_input)
        self.port_value.textEdited.connect(self.check_input)
        self.timeout_value.textEdited.connect(self.check_input)

        # 测试连接按钮：点击触发测试连接功能
        self.test_conn_btn.clicked.connect(self.test_connection)
        # 确定按钮：点击触发添加连接记录到系统库中，并增加到展示界面
        self.ok_btn.clicked.connect(self.add_or_edit)
        # 确定、测试连接按钮默认不可用，只有当输入框都有值才可用
        self.ok_btn.setDisabled(True)
        self.test_conn_btn.setDisabled(True)
        # 取消按钮：点击则关闭对话框
        self.cancel_btn.clicked.connect(self.close)

    def translate_ui(self):
        self.setWindowTitle(self._translate("conn_dialog", self.dialog_title))
        self.conn_name.setText("连接名")
        self.host.setText("主机")
        self.port.setText("端口号")
        self.timeout.setText("超时时间")

        self.test_conn_btn.setText("测试连接")
        self.ok_btn.setText("确定")
        self.cancel_btn.setText("取消")
        # 设置默认超时时间
        self.timeout_value.setText('3000')

        # 回显
        if self.connection.id:
            self.conn_name_value.setText(self._translate("Dialog", self.connection.name))
            self.host_value.setText(self._translate("Dialog", self.connection.host))
            port = str(self.connection.port) if self.connection.port else None
            self.port_value.setText(self._translate("Dialog", port))
            timeout = str(self.connection.timeout) if self.connection.timeout else '3000'
            self.timeout_value.setText(self._translate("Dialog", timeout))
            self.ok_btn.setDisabled(False)
            self.test_conn_btn.setDisabled(False)
            self.name_available = True

    def check_name_available(self, name_available, conn_name):
        if conn_name:
            if name_available:
                prompt = f"连接名称 {conn_name} 可用"
                self.name_check_prompt.setText(self.get_elided_text_by_width(prompt))
                self.name_check_prompt.setStyleSheet("color:green")
            else:
                prompt = f"连接名称 {conn_name} 不可用"
                self.name_check_prompt.setText(self.get_elided_text_by_width(prompt))
                self.name_check_prompt.setStyleSheet("color:red")
            self.name_available = name_available
        else:
            self.name_check_prompt.clear()

    def get_elided_text_by_width(self, prompt):
        """根据label的长度，将文本自动缩减，并以省略号形式展示，当前省略模式为中间的文本缩减，替换为省略号"""
        font_width = QFontMetrics(self.name_check_prompt.font())
        if font_width.width(prompt) > self.name_check_prompt.width():
            prompt = font_width.elidedText(prompt, Qt.ElideMiddle, self.name_check_prompt.width())
        return prompt

    def check_input(self):
        # 检查是否都有值
        conn = self.get_input()
        # 如果输入框都有值，那么就开放按钮，否则关闭
        if all(conn) and self.name_available:
            self.ok_btn.setDisabled(False)
            self.test_conn_btn.setDisabled(False)
        else:
            self.ok_btn.setDisabled(True)
            self.test_conn_btn.setDisabled(True)

    def get_input(self):
        conn_name = self.conn_name_value.text()
        host = self.host_value.text()
        port = int(self.port_value.text()) if self.port_value.text() else ''
        timeout = self.timeout_value.text()
        return conn_name, host, port, timeout

    def test_connection(self):
        conn_info = self.get_input_connection()
        AsyncTestConn(self, conn_info).start()

    def get_input_connection(self):
        return Connection(self.connection.id, *self.get_input())

    def add_or_edit(self):
        new_conn = self.get_input_connection()
        if self.dialog_title == EDIT_CONN_MENU:
            # 比较下是否有改动，如果有修改再更新库
            if set(new_conn[1:]) - set(self.connection[1:]):
                self.edit_conn_worker = AsyncEditConnDB(new_conn, self.tree_item, self, self.dialog_title,
                                                        SAVE_CONN_SUCCESS_PROMPT).start()
        elif self.dialog_title == ADD_CONN_MENU:
            self.add_conn_worker = AsyncAddConnDB(new_conn, self.tree_widget, add_conn_tree_item, self,
                                                  self.dialog_title, SAVE_CONN_SUCCESS_PROMPT).start()

    def close(self):
        self.async_check_name.quit()
        super().close()

