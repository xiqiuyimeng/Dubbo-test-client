# -*- coding: utf-8 -*-
import json
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPlainTextEdit, QLabel, QTabWidget, QWidget, QVBoxLayout, QPushButton, \
    QHBoxLayout, QGridLayout, QComboBox, QFormLayout, QSplitter

from src.constant.main_constant import OPEN_METHOD_MENU
from src.constant.tab_constant import SEND_BUTTON, SENDING_BUTTON, ARGS_TAB_TITLE, JSON_TAB_TITLE, \
    RESULT_DISPLAY, REQUEST_TIME, RESPONSE_TIME, COST_TIME, REQUEST_FAIL, RESULT_DISPLAY_RAW, RESULT_DISPLAY_JSON, \
    AUTO_SAVE_CHANGE
from src.function.db.tab_sqlite import TabObj
from src.ui.async_func.async_tab import AsyncSendRequestManager, AsyncReadTabObjManager, AsyncDisplayTextBrowserManager
from src.ui.func.common import set_up_label
from src.ui.scrollable_widget.scrollable_widget import MyTextBrowser
from src.ui.tab.tab_widget import ParamTabWidget
from src.ui.table.table_widget import ParamTableWidget

_author_ = 'luwt'
_date_ = '2021/11/4 19:38'


class TabUI:

    def __init__(
            self,
            window,
            title: str,
            service_path: str,
            method_dict: dict,
            conn_dict: dict,
            tab_id: str,
    ):
        """
        tab页
        :param window: 主窗口
        :param title: tab页的标题
        :param service_path: 服务路径，为了在下面去拼接完整方法名，调用
        :param method_dict: 方法详情的字典 {
                                    "method_name": "",
                                    "param_type": "",
                                    "result_type": ""
                                    }
                            展示方法详细信息
                            'id name host port timeout'
        :param conn_dict: 连接详情的字典 {
                                    "id": "",
                                    "name": "",
                                    "host": "",
                                    "port": "",
                                    "timeout": ""
                                    }
        :param tab_id: tab id, conn_id + service + method_name
        """
        self.window = window
        self.parent = window.tab_widget
        self.title = title
        self.service_path = service_path
        self.method_dict = method_dict
        self.conn_dict = conn_dict
        self.tab_id = tab_id
        # 预定义
        self.tab: QWidget = ...
        self.send_button: QPushButton = ...
        self.param_edit_tab_widget: ParamTabWidget = ...
        self.json_edit_area: QPlainTextEdit = ...
        self.request_time_label_value: QLabel = ...
        self.response_time_label_value: QLabel = ...
        self.result_count_label_value: QLabel = ...
        self.result_browser: MyTextBrowser = ...
        self.result_display_combo_box: QComboBox = ...
        self.args_edit_tab: QWidget = ...
        self.table_widget: ParamTableWidget = ...
        self.json_edit_tab: QWidget = ...
        self.method_param_list = self.get_param_list()
        self.rpc_result = None
        self.conn_name = f"连接名称：{self.conn_dict.get('name')}"
        self.service_path_name = f"服务路径：{self.service_path}"
        self.method_name = f"方法名称：{self.method_dict.get('method_name')}"
        self.method_param = f"参数详情：{self.method_dict.get('param_type')}"
        self.method_result = f"返回类型：{self.method_dict.get('result_type')}"
        # 维护的当前页数据
        self.tab_obj_dict: dict = ...
        # 是否正在回显数据
        self.filling_flag = False
        # 标识是否在发送请求中
        self.sending_flag = False
        self.read_tab_manager = ...
        self.request_manager = ...

    def set_up_tab(self, tab_order=None):
        self.tab = QWidget()
        # 将tab_id 写入到所属tab页中
        self.tab.setProperty("tab_id", self.tab_id)
        # 将气泡提示需要的文案提前放入tab属性中
        tool_tip = f'{self.title}\n{self.conn_name}\n{self.service_path_name}\n' \
                   f'{self.method_name}\n{self.method_param}\n{self.method_result}'
        self.tab.setProperty("tool_tip", tool_tip)
        # tab页，垂直布局
        tab_vertical_layout = QVBoxLayout(self.tab)
        tab_vertical_layout.setObjectName("tab_vertical_layout")
        # 间距为0
        tab_vertical_layout.setSpacing(0)
        tab_vertical_layout.setContentsMargins(0, 0, 0, 0)
        # 方法展示区
        self.set_up_method_display_area(self.tab, tab_vertical_layout)
        # 发送参数编辑区和结果展示区放在同一个区下，加上垂直的分割器，方便滑动
        param_result_widget = QWidget(self.tab)
        tab_vertical_layout.addWidget(param_result_widget)
        param_result_layout = QVBoxLayout(param_result_widget)
        param_result_splitter = QSplitter()
        param_result_splitter.setOrientation(Qt.Vertical)
        param_result_splitter.setObjectName("param_result_splitter")
        param_result_layout.addWidget(param_result_splitter)
        param_result_layout.setSpacing(0)
        param_result_layout.setContentsMargins(0, 0, 0, 0)
        # 发送参数编辑区
        self.set_up_param_edit_area(param_result_splitter)
        # 结果展示区
        self.set_up_result_display_area(param_result_splitter)
        tab_vertical_layout.setStretch(0, 1)
        tab_vertical_layout.setStretch(1, 8)
        param_result_splitter.setStretchFactor(0, 3)
        param_result_splitter.setStretchFactor(1, 5)

        # 处理tab obj
        self.read_tab_manager = AsyncReadTabObjManager(self.tab_id, self.set_up_tab_obj,
                                                       self.tab, self.window, OPEN_METHOD_MENU)
        self.read_tab_manager.start()
        if tab_order:
            # 按顺序插入到 parent temp_tab_list 中
            self.parent.temp_tab_list.append((tab_order, self.tab, self.title))
        else:
            # 添加tab，设置tab标题
            self.parent.addTab(self.tab, self.title)
            self.parent.setCurrentWidget(self.tab)

    def get_param_list(self):
        return self.method_dict.get("param_type").split(",") \
            if self.method_dict.get("param_type") else list()

    def set_up_method_display_area(self, tab: QWidget, layout: QVBoxLayout):
        """方法展示区，主要是：方法名称，方法参数类型，方法返回类型，发送请求按钮"""
        method_display_widget = QWidget(tab)
        method_display_widget.setObjectName("method_display_widget")
        layout.addWidget(method_display_widget)
        # 整体水平布局
        method_display_layout = QHBoxLayout(method_display_widget)
        method_display_layout.setObjectName("method_display_layout")
        # 间距为0
        method_display_layout.setContentsMargins(0, 0, 0, 0)
        # 展示区，垂直布局
        display_layout = QVBoxLayout()
        display_layout.setObjectName("display_layout")
        method_display_layout.addLayout(display_layout)
        # 连接名称展示区
        conn_name_label = set_up_label(method_display_widget, self.conn_name, "conn_name_label")
        display_layout.addWidget(conn_name_label)
        # 服务路径展示区
        service_path_label = set_up_label(method_display_widget, self.service_path_name, "service_path_label")
        display_layout.addWidget(service_path_label)
        # 方法名称展示区
        method_name_label = set_up_label(method_display_widget, self.method_name, "method_name_label")
        display_layout.addWidget(method_name_label)
        # 方法参数类型展示区
        method_param_label = set_up_label(method_display_widget, self.method_param, "method_param_label")
        display_layout.addWidget(method_param_label)
        # 方法返回结果类型展示区
        result_type_label = set_up_label(method_display_widget, self.method_result, "result_type_label")
        display_layout.addWidget(result_type_label)
        # 按钮区布局
        button_layout = QVBoxLayout()
        button_layout.setObjectName("button_layout")
        method_display_layout.addLayout(button_layout)
        # 发送请求按钮区
        self.set_up_send_button(method_display_widget, button_layout)

        method_display_layout.setStretch(0, 4)
        method_display_layout.setStretch(1, 1)

    def set_up_param_edit_area(self, parent: QSplitter):
        """发送参数编辑区，作为一个tab区，第一个tab为args类型，第二个tab为json类型"""
        self.param_edit_tab_widget = ParamTabWidget(parent)
        self.param_edit_tab_widget.setObjectName("param_edit_tab_widget")
        # 第一个tab，args类型
        self.set_up_param_args_edit_tab(self.param_edit_tab_widget)
        # 第二个tab，json类型
        self.set_up_param_json_edit_tab(self.param_edit_tab_widget)
        # 决定哪个标签页置顶
        self.param_edit_tab_widget.decide_current_tab(self.method_param_list)
        # 当参数tab页切换时，触发保存
        self.param_edit_tab_widget.currentChanged.connect(self.save_param_type)

    def set_up_result_display_area(self, parent: QSplitter):
        """返回结果展示区，包括耗时统计区，下拉框, 结果打印区"""
        result_display_widget = QWidget(parent)
        result_display_widget.setObjectName("result_display_widget")
        # 布局
        result_display_layout = QVBoxLayout(result_display_widget)
        result_display_layout.setObjectName("result_display_layout")
        result_display_layout.setSpacing(0)
        result_display_layout.setContentsMargins(0, 0, 0, 0)
        # 耗时统计,返回结果展示样式选择区
        self.set_up_result_count(result_display_widget, result_display_layout)
        # 结果展示区
        self.set_up_result_browser(result_display_widget, result_display_layout)

    def set_up_send_button(self, parent: QWidget, layout: QVBoxLayout):
        """发送按钮区"""
        self.send_button = QPushButton(parent)
        self.send_button.setObjectName("send_button")
        self.enable_send_button()
        layout.addWidget(self.send_button)
        # 按钮事件
        self.send_button.clicked.connect(lambda: self.send_func())

    def set_up_param_args_edit_tab(self, tab: QTabWidget):
        """args参数输入区，表格形式"""
        self.args_edit_tab = QWidget(tab)
        self.args_edit_tab.setObjectName("args_edit_tab")
        tab.addTab(self.args_edit_tab, ARGS_TAB_TITLE)
        # 布局
        args_edit_layout = QVBoxLayout(self.args_edit_tab)
        args_edit_layout.setObjectName("args_edit_layout")
        args_edit_layout.setSpacing(0)
        args_edit_layout.setContentsMargins(0, 0, 0, 0)
        # 表格区
        self.table_widget = ParamTableWidget(self)
        self.table_widget.setObjectName("table_widget")
        args_edit_layout.addWidget(self.table_widget)
        # 按参数列表初始化表格
        self.table_widget.init_table(self.method_param_list)
        # args 表格区输入时，触发保存
        self.table_widget.item_data_changed.connect(lambda row, col, text:
                                                    self.save_args_table_col(row, col, text))

    def set_up_param_json_edit_tab(self, tab: QTabWidget):
        """json参数输入区"""
        self.json_edit_tab = QWidget(tab)
        self.json_edit_tab.setObjectName("json_edit_tab")
        tab.addTab(self.json_edit_tab, JSON_TAB_TITLE)
        # 布局
        json_edit_layout = QVBoxLayout(self.json_edit_tab)
        json_edit_layout.setObjectName("json_edit_layout")
        json_edit_layout.setSpacing(0)
        json_edit_layout.setContentsMargins(0, 0, 0, 0)
        # 文本编辑区
        self.json_edit_area = QPlainTextEdit(self.json_edit_tab)
        self.json_edit_area.setObjectName("json_edit_area")
        json_edit_layout.addWidget(self.json_edit_area)
        # json参数区输入时，触发保存
        self.json_edit_area.textChanged.connect(self.save_json_area)

    def set_up_result_count(self, parent: QWidget, layout: QVBoxLayout):
        """统计耗时，下拉框决定返回结果展示样式"""
        result_count_widget = QWidget(parent)
        result_count_widget.setObjectName("result_count_widget")
        layout.addWidget(result_count_widget)
        # 表格布局
        result_count_layout = QGridLayout(result_count_widget)
        result_count_layout.setObjectName("result_count_layout")
        result_count_layout.setSpacing(0)
        result_count_layout.setContentsMargins(0, 0, 0, 0)
        # 表格使用第一行
        result_display_widget = QWidget(result_count_widget)
        result_count_layout.addWidget(result_display_widget, 0, 0, 1, 1)
        result_display_layout = QHBoxLayout(result_display_widget)
        # result_display_label
        result_display_label = set_up_label(result_display_widget, RESULT_DISPLAY, "result_display_label")
        result_display_layout.addWidget(result_display_label)
        result_display_layout.setSpacing(0)
        result_display_layout.setContentsMargins(0, 0, 0, 0)
        # combo box
        self.result_display_combo_box = QComboBox(result_display_widget)
        self.result_display_combo_box.setObjectName("result_display_combo_box")
        self.result_display_combo_box.addItem(RESULT_DISPLAY_RAW)
        self.result_display_combo_box.addItem(RESULT_DISPLAY_JSON)
        self.result_display_combo_box.setCurrentIndex(1)
        self.result_display_combo_box.currentIndexChanged.connect(lambda: self.combo_box_change_func())
        result_display_layout.addWidget(self.result_display_combo_box)
        # 时间统计
        request_time_widget = QWidget(result_count_widget)
        request_time_layout = QFormLayout(request_time_widget)
        request_time_label = set_up_label(request_time_widget, REQUEST_TIME, "request_time_label")
        self.request_time_label_value = set_up_label(request_time_widget, "", "request_time_label_value")
        request_time_layout.addRow(request_time_label, self.request_time_label_value)
        result_count_layout.addWidget(request_time_widget, 0, 1, 1, 1)
        response_time_widget = QWidget(result_count_widget)
        response_time_layout = QFormLayout(response_time_widget)
        response_time_label = set_up_label(result_count_widget, RESPONSE_TIME, "response_time_label")
        self.response_time_label_value = set_up_label(result_count_widget, "", "response_time_label_value")
        response_time_layout.addRow(response_time_label, self.response_time_label_value)
        result_count_layout.addWidget(response_time_widget, 0, 2, 1, 1)
        result_cost_widget = QWidget(result_count_widget)
        result_cost_layout = QFormLayout(result_cost_widget)
        result_count_label = set_up_label(result_count_widget, COST_TIME, "result_count_label")
        self.result_count_label_value = set_up_label(result_count_widget, "", "result_count_label_value")
        result_cost_layout.addRow(result_count_label, self.result_count_label_value)
        result_count_layout.addWidget(result_cost_widget, 0, 3, 1, 1)

    def set_up_result_browser(self, parent: QWidget, layout: QVBoxLayout):
        """返回结果展示区"""
        self.result_browser = MyTextBrowser(parent)
        self.result_browser.setObjectName("result_browser")
        layout.addWidget(self.result_browser)

    def get_param(self):
        """获取入参"""
        # 如果参数tab页可见，那么说明有参数
        if self.param_edit_tab_widget.isVisible():
            # args参数
            if self.param_edit_tab_widget.currentIndex() == 0:
                param_args = list()
                for row in range(len(self.method_param_list)):
                    args = self.table_widget.cellWidget(row, 1).text().strip()
                    param_args.append(args)
                return ",".join(param_args)
            else:
                return self.json_edit_area.toPlainText().strip()

    def send_func(self):
        """发送请求"""
        # 点击发送后，首先将按钮置为不可用，文案显示：发送中
        self.disable_send_button()
        self.request_time_label_value.setText(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # 清空结果区
        self.result_browser.clear()
        self.rpc_result = ""
        method = self.method_dict.get("method_name")
        request_param = self.get_param()
        if request_param:
            invoke_method = f'{self.service_path}.{method}({request_param})'
        else:
            invoke_method = f'{self.service_path}.{method}()'
        # 异步发送请求
        self.request_manager = AsyncSendRequestManager(self.request_fail, self.request_success,
                                                       self.result_browser, self.window, REQUEST_FAIL,
                                                       invoke_method, *list(self.conn_dict.values())[2:])
        self.request_manager.start()

    def request_success(self, result):
        self.parse_result(result)
        self.response_time_label_value.setText(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # 恢复发送按钮
        self.enable_send_button()
        # 保存结果信息
        self.save_result()

    def request_fail(self):
        # 恢复发送按钮
        self.enable_send_button()
        # 保存结果信息
        self.save_result()

    def disable_send_button(self):
        # 设置按钮不可用
        self.send_button.setDisabled(True)
        self.send_button.setText(SENDING_BUTTON)
        self.sending_flag = True

    def enable_send_button(self):
        # 恢复发送按钮
        self.send_button.setDisabled(False)
        self.send_button.setText(SEND_BUTTON)
        self.sending_flag = False

    def parse_result(self, result):
        """解析结果，展示"""
        result_list = result.strip().split("\r\n")
        # 如果接口响应正常，再解析结果数据
        if len(result_list) == 3:
            time_count = result_list[2].lstrip('elapsed: ').rstrip('.')
            self.result_count_label_value.setText(time_count)
            self.rpc_result = result_list[1].lstrip('result: ')
        elif len(result_list) == 2:
            # 如果分割完只有两个元素，第二个为异常语句
            self.rpc_result = result_list[1]
        elif len(result_list) == 1:
            # 如果只有一个元素，应该是服务返回的错误，应该展示到结果区
            self.rpc_result = result_list[0]
        self.display_result_browser()

    def combo_box_change_func(self):
        # 如果在发送请求阶段，发送请求最后会触发保存，这里不需要触发
        if not self.sending_flag:
            # 保存combo box状态
            self.save_result_display()
            original_text = self.result_browser.toPlainText()
            # 如果之前有值再操作
            if original_text:
                self.result_browser.clear()
                self.display_result_browser()

    def display_result_browser(self):
        if self.result_display_combo_box.currentText() == RESULT_DISPLAY_JSON:
            # 如果解析出错，应该用原生展示
            try:
                json_format_result = json.dumps(json.loads(self.rpc_result), indent=4, ensure_ascii=False)
                self.result_browser.set_text(json_format_result)
            except:
                self.result_browser.set_text(self.rpc_result)
                self.result_display_combo_box.setCurrentIndex(0)
        else:
            self.result_browser.set_text(self.rpc_result)

    def set_up_tab_obj(self, tab_obj):
        """如果之前没有保存过，初始化一个新的tab_obj_dict，按当前tab页的属性进行构造"""
        if tab_obj.id is not None:
            self.tab_obj_dict = dict(zip(tab_obj._fields, tab_obj))
            # 处理下两个dict
            self.tab_obj_dict['param_args_dict'] = eval(tab_obj.param_args_dict)
            self.tab_obj_dict['param_desc_dict'] = eval(tab_obj.param_desc_dict)
            # 如果保存过，回显数据
            self.fill_data(tab_obj)
        else:
            self.tab_obj_dict = dict()
            # id conn_id tab_id param_type param_args_dict param_json param_desc_dict
            # result_display request_time response_time method_cost result
            self.tab_obj_dict['conn_id'] = self.conn_dict.get("id")
            self.tab_obj_dict['tab_id'] = self.tab_id
            self.tab_obj_dict['param_type'] = self.param_edit_tab_widget.currentIndex()
            self.tab_obj_dict['param_args_dict'] = dict()
            self.tab_obj_dict['param_desc_dict'] = dict()
            self.tab_obj_dict['result_display'] = self.result_display_combo_box.currentIndex()

    def fill_data(self, tab_obj):
        self.filling_flag = True
        # 处理参数类型
        param_type = tab_obj.param_type
        self.param_edit_tab_widget.decide_current_tab(self.method_param_list, param_type)
        # 填充param表格区
        param_args_dict = eval(tab_obj.param_args_dict)
        if param_args_dict:
            self.table_widget.fill_table_column(list(param_args_dict.values()), 1)
        param_desc_dict = eval(tab_obj.param_desc_dict)
        if param_desc_dict:
            self.table_widget.fill_table_column(list(param_desc_dict.values()), 2)
        # 填充param json区
        self.json_edit_area.setPlainText(tab_obj.param_json)
        # combo box
        self.result_display_combo_box.setCurrentIndex(tab_obj.result_display)
        # 请求时间
        self.request_time_label_value.setText(tab_obj.request_time)
        # 响应时间
        self.response_time_label_value.setText(tab_obj.response_time)
        # 耗时
        self.result_count_label_value.setText(tab_obj.method_cost)
        # 结果
        self.rpc_result = tab_obj.result
        self.display_result_browser()
        # 重置标志位
        self.filling_flag = False

    # ---------------------------- save tab func ---------------------------- #
    def save_param_type(self, index):
        """保存当前的param_type"""
        if not self.filling_flag:
            self.tab_obj_dict['param_type'] = index
            self.save_tab_change()

    def save_args_table_col(self, row, col, text):
        """保存当前的args参数表格内容"""
        if not self.filling_flag:
            if col == 1:
                # 字典保存形式
                self.tab_obj_dict['param_args_dict'][row] = text
            else:
                self.tab_obj_dict['param_desc_dict'][row] = text
            self.save_tab_change()

    def save_json_area(self):
        """保存当前的json编辑区"""
        if not self.filling_flag:
            self.tab_obj_dict['param_json'] = self.json_edit_area.toPlainText()
            self.save_tab_change()

    def save_result_display(self):
        """保存当前combo box状态"""
        if not self.filling_flag:
            self.tab_obj_dict['result_display'] = self.result_display_combo_box.currentIndex()
            self.save_tab_change()

    def save_result(self):
        """保存和结果相关内容，请求时间，响应时间，耗时，结果"""
        if not self.filling_flag:
            self.tab_obj_dict['request_time'] = self.request_time_label_value.text()
            self.tab_obj_dict['response_time'] = self.response_time_label_value.text()
            self.tab_obj_dict['method_cost'] = self.result_count_label_value.text()
            self.tab_obj_dict['result'] = self.rpc_result
            self.save_tab_change()

    def save_tab_change(self):
        """保存tab页信息"""
        self.tab_obj_dict['param_args_dict'] = str(self.tab_obj_dict.get('param_args_dict'))
        self.tab_obj_dict['param_desc_dict'] = str(self.tab_obj_dict.get('param_desc_dict'))
        for field in TabObj._fields:
            self.tab_obj_dict[field] = self.tab_obj_dict.get(field)
        tab_obj = TabObj(**self.tab_obj_dict)
        self.parent.async_save_manager.save_tab_obj(tab_obj, self.save_post_process)

    def save_post_process(self, tab_obj_id):
        if tab_obj_id > 0:
            self.tab_obj_dict['id'] = tab_obj_id
        # 保存结束后，将两个dict转回字典
        self.tab_obj_dict['param_args_dict'] = eval(self.tab_obj_dict.get('param_args_dict'))
        self.tab_obj_dict['param_desc_dict'] = eval(self.tab_obj_dict.get('param_desc_dict'))
        self.window.setStatusTip(f"{AUTO_SAVE_CHANGE} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
