# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from PyQt5.QtGui import QIcon

from src.constant.main_constant import CLOSE_CONN_MENU, OPEN_CONN_MENU, TEST_CONN_MENU, ADD_CONN_MENU, EDIT_CONN_MENU, \
    DEL_CONN_MENU, OPEN_SERVICE_MENU, CLOSE_SERVICE_MENU, EDIT_CONN_PROMPT, CLOSE_METHOD_MENU, OPEN_METHOD_MENU, \
    DEL_CONN_PROMPT
from src.function.db.conn_sqlite import Connection
from src.ui.async_func.async_conn import AsyncSimpleTestConnManager, AsyncOpenConnManager, AsyncOpenServiceManager, AsyncOpenMethodManager
from src.ui.async_func.async_conn_db import AsyncCloseConnDBManager, AsyncDelConnDBManager, AsyncCloseDelConnDBManager
from src.ui.box.message_box import pop_question
from src.ui.tab.tab_ui import TabUI
from src.ui.tree_item.my_tree_item import MyTreeWidgetItem

_author_ = 'luwt'
_date_ = '2021/11/3 22:36'


def add_conn_tree_item(tree_widget, conn, first_col_text=None):
    # item属性：id name host port timeout
    # 根节点，展示连接的列表，将连接信息写入隐藏列
    return make_tree_item(tree_widget, conn.name, QIcon(":/icon/mysql_conn_icon.png"),
                          first_col_text=first_col_text, second_col_text=dict(zip(conn._fields, conn)))


def make_tree_item(parent, text, icon, checkbox=None, first_col_text=None, second_col_text=None):
    """
    构造树的子项
    :param parent: 要构造子项的父节点元素
    :param text: 构造的子节点信息
    :param icon: 图标，该元素的展示图标对象
    :param checkbox: 构造的子节点的复选框，可无。若存在，将当前状态写入第三列中
    :param first_col_text: 第一列隐藏信息
    :param second_col_text: 第二列隐藏信息
    """
    item = MyTreeWidgetItem(parent)
    item.setIcon(0, icon)
    item.setText(0, text)
    if first_col_text:
        # 作为隐藏属性，写于指定列
        item.setText(1, first_col_text)
    if second_col_text:
        item.setText(2, second_col_text)
    if checkbox is not None:
        item.setCheckState(0, checkbox)
    return item


def tree_node_factory(item):
    """
    获取树节点对应的实例化对象。
    树结构：
        树的根：树的顶层
            连接：第一级，父节点为根
                service：第二级，父节点为连接
                    method：第三级，父节点为service
    目前树的根节点为空，所以可以根据这一特性发现当前节点的层级，
    从而返回相应的实例
    :param item: 当前的元素
    """
    # 如果父级为空，那么则为连接
    if item.parent() is None:
        return TreeNodeConn()
    elif item.parent().parent() is None:
        return TreeNodeService()
    elif item.parent().parent().parent() is None:
        return TreeNodeMethod()


def get_conn_info(text):
    conn_info = eval(text)
    host = conn_info.get("host")
    port = conn_info.get("port")
    timeout = conn_info.get("timeout")
    return host, port, timeout


def close_item_ui(tab_order, item, tab_widget):
    if tab_order:
        # 将order从大到小排序，然后关闭对应的tab
        sorted_order = sorted(tab_order, reverse=True)
        for order in sorted_order:
            tab_widget.removeTab(order)
    item.takeChildren()


class Context:

    def __init__(self, tree_node):
        self.tree_node = tree_node

    def open_item(self, item, window):
        return self.tree_node.open_item(item, window=window)

    def reopen_item(self, item, children_data, item_dict, expanded, tab_widget):
        return self.tree_node.reopen_item(item, children_data, item_dict, expanded, tab_widget)

    def close_item(self, item, window):
        return self.tree_node.close_item(item, window)

    def get_menu_names(self, item, window):
        return self.tree_node.get_menu_names(item, window)

    def handle_menu_func(self, item, func, window):
        return self.tree_node.handle_menu_func(item, func, window)


class TreeNodeAbstract(ABC):

    @abstractmethod
    def open_item(self, item, window): ...

    @abstractmethod
    def open_item_ui(self, *args): ...

    @abstractmethod
    def reopen_item(self, item, children_data, item_dict, expanded=None, window=None): ...

    @abstractmethod
    def close_item(self, item, window): ...

    @abstractmethod
    def get_menu_names(self, item, window): ...

    @abstractmethod
    def handle_menu_func(self, item, func, window): ...


class TreeNodeConn(TreeNodeAbstract):

    def open_item(self, item: MyTreeWidgetItem, window):
        """
        打开连接，展示连接下的所有service列表
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        # 仅当子元素不存在时，获取子元素并填充
        if item.childCount() == 0:
            # 连接的id，连接名称
            conn_info = get_conn_info(item.text(2))
            # 在opened item中保存的连接id
            saved_conn_id = item.text(1)
            AsyncOpenConnManager(conn_info, saved_conn_id, self.open_item_ui, item, window).start()

    def open_item_ui(self, result, item):
        if result:
            for service, saved_service_id in result:
                make_tree_item(item, service, QIcon(":/icon/mysql_conn_icon.png"),
                               first_col_text=saved_service_id)
            item.setExpanded(True)

    def reopen_item(self, item, children_data, item_dict, expanded=None, window=None):
        """重新打开连接下的服务列表，展开已保存的服务列表"""
        for child_service in children_data:
            service_item = make_tree_item(item, child_service.item_name, QIcon(":/icon/mysql_conn_icon.png"),
                                          first_col_text=child_service.id)
            item_dict[child_service.id] = (service_item, child_service.expanded)
        # 设置展开状态
        item.setExpanded(expanded)

    def close_item(self, item, window):
        """
        关闭树的某项，将其下所有子项移除，并将扩展状态置为false
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        AsyncCloseConnDBManager(item.text(1), 1, close_item_ui, item, window, CLOSE_CONN_MENU).start()

    def get_menu_names(self, item, window):
        """
        获取树中，第一级连接项的右键菜单名字列表
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        menu_names = list()
        if item.childCount():
            menu_names.append(CLOSE_CONN_MENU)
        else:
            menu_names.append(OPEN_CONN_MENU)
        menu_names.append(TEST_CONN_MENU)
        menu_names.append(ADD_CONN_MENU)
        menu_names.append(EDIT_CONN_MENU)
        menu_names.append(DEL_CONN_MENU)
        return menu_names

    def handle_menu_func(self, item, func, window):
        """
        在连接层，右键菜单的功能实现
        :param item: 当前点击树节点元素
        :param func: 右键菜单中功能名称
        :param window: 启动的主窗口界面对象
        """
        # 获取当前选中的连接id，连接名称
        # conn_id, conn_name = self.get_node_info(item)
        # 打开连接
        if func == OPEN_CONN_MENU:
            self.open_item(item, window=window)
        # 关闭连接
        elif func == CLOSE_CONN_MENU:
            self.close_item(item, window)
        # 测试连接
        elif func == TEST_CONN_MENU:
            conn_info = eval(item.text(2))
            AsyncSimpleTestConnManager(item, list(conn_info.values()), window).start()
        # 添加连接
        elif func == ADD_CONN_MENU:
            window.add_conn()
        # 编辑连接
        elif func == EDIT_CONN_MENU:
            self.edit_conn(window, item)
        # 删除连接
        elif func == DEL_CONN_MENU:
            self.del_conn(window, eval(item.text(2)).get("id"), item)

    def edit_conn(self, window, item):
        """
        编辑连接，首先需要判断连接是否打开，
        如果打开，则弹窗需要关闭连接。
        否则直接弹编辑窗口
        :param window: 启动的主窗口界面对象
        :param item: 当前点击树节点元素
        """
        # 先判断是否打开
        if item.childCount() > 0:
            if pop_question(EDIT_CONN_MENU, EDIT_CONN_PROMPT):
                # 开始关闭连接
                self.close_item(item, window)
            else:
                return
        window.edit_conn(Connection(**eval(item.text(2))), item)

    def del_conn(self, window, conn_id, item):
        """
        删除连接，如果连接已经打开，弹窗是否删除连接
        :param window: 启动的主窗口界面对象
        :param conn_id: 连接id
        :param item: 当前点击树节点元素
        """
        # 先判断是否打开
        if item.childCount() > 0:
            if pop_question(DEL_CONN_MENU, DEL_CONN_PROMPT):
                # 开始关闭并删除连接
                AsyncCloseDelConnDBManager(conn_id, self.close_del_conn_item, item, window, DEL_CONN_MENU).start()
        else:
            AsyncDelConnDBManager(conn_id, self.del_conn_item, window.tree_widget, item, window, DEL_CONN_MENU).start()

    def del_conn_item(self, item, tree_widget):
        tree_widget.takeTopLevelItem(tree_widget.indexOfTopLevelItem(item))

    def close_del_conn_item(self, item, tab_widget, tree_widget, tab_order):
        if tab_order:
            # 将order从大到小排序，然后关闭对应的tab
            sorted_order = sorted(tab_order, reverse=True)
            for order in sorted_order:
                tab_widget.removeTab(order)
        self.del_conn_item(item, tree_widget)


class TreeNodeService(TreeNodeAbstract):

    def open_item(self, item, window):
        """
        展示该服务下的所有方法，
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        # 仅当子元素不存在时，获取子元素并填充
        if item.childCount() == 0:
            # 获取连接id和名称
            conn_info = get_conn_info(item.parent().text(2))
            AsyncOpenServiceManager(conn_info, item.text(0), item.text(1), self.open_item_ui, item, window).start()

    def open_item_ui(self, result, item):
        if result:
            for method_dict, saved_method_id in result:
                method_name = method_dict.get("method_name")
                # 将方法详细信息写入隐藏列
                make_tree_item(item, method_name, QIcon(":/icon/mysql_conn_icon.png"),
                               first_col_text=saved_method_id, second_col_text=method_dict)
            item.setExpanded(True)

    def reopen_item(self, item, children_data, item_dict, expanded=None, window=None):
        """重新打开service节点，获取下一级保存的数据"""
        for child_method in children_data:
            method_item = make_tree_item(item, child_method.item_name, QIcon(":/icon/mysql_conn_icon.png"),
                                         first_col_text=child_method.id, second_col_text=child_method.ext_info)
            item_dict[child_method.id] = (method_item, child_method.expanded)
        item.setExpanded(expanded)

    def close_item(self, item, window):
        """
        关闭树的某项，将其下所有子项移除，并将扩展状态置为false
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        AsyncCloseConnDBManager(item.text(1), 2, close_item_ui, item, window, CLOSE_SERVICE_MENU).start()

    def get_menu_names(self, item, window):
        """
        获取树中，服务接口项的右键菜单名字列表
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        menu_list = list()
        if item.childCount():
            menu_list.append(CLOSE_SERVICE_MENU)
        else:
            menu_list.append(OPEN_SERVICE_MENU)
        return menu_list

    def handle_menu_func(self, item, func, window):
        """
         服务，右键菜单的功能实现
        :param item: 当前点击树节点元素
        :param func: 右键菜单中功能名称
        :param window: 启动的主窗口界面对象
        """
        # 打开数据库
        if func == OPEN_SERVICE_MENU:
            self.open_item(item, window)
        # 关闭数据库
        elif func == CLOSE_SERVICE_MENU:
            self.close_item(item, window)


class TreeNodeMethod(TreeNodeAbstract):

    def open_item(self, item, window):
        """
        打开方法节点，右侧添加一个tab页
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        conn_dict = eval(item.parent().parent().text(2))
        service_path = item.parent().text(0)
        method_name = item.text(0)
        # 首先构造tab的id：conn_id + service + method_name
        tab_id = f'{conn_dict.get("id")}-{service_path}-{method_name}'
        AsyncOpenMethodManager(item, window, tab_id, item.text(1), self.open_item_ui).start()

    def open_item_ui(self, item_order, item, window, tab_id):
        if item_order >= 0:
            window.tab_widget.setCurrentIndex(item_order)
        else:
            method_name = item.text(0)
            service_path = item.parent().text(0)
            method_dict = eval(item.text(2))
            conn_dict = eval(item.parent().parent().text(2))
            tab_ui = TabUI(window,
                           method_name,
                           service_path,
                           method_dict,
                           conn_dict,
                           tab_id)
            tab_ui.set_up_tab()

    def reopen_item(self, item, children_data, item_dict, expanded=None, window=None):
        opened_tab = children_data[0]
        conn_dict = eval(item.parent().parent().text(2))
        method_dict = eval(item.text(2))
        service_path = item.parent().text(0)
        method_name = item.text(0)
        tab_ui = TabUI(window,
                       method_name,
                       service_path,
                       method_dict,
                       conn_dict,
                       opened_tab.item_name)
        # 直接按order insert插入不可取，应该先添加后排序
        tab_ui.set_up_tab(opened_tab.item_order)
        if opened_tab.is_current:
            window.tab_widget.current = opened_tab.item_order

    def close_item(self, item, window):
        """
        关闭右侧对应的tab页
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        AsyncCloseConnDBManager(item.text(1), 3, self.close_item_ui, item, window, CLOSE_METHOD_MENU).start()

    def close_item_ui(self, tab_order, item, tab_widget):
        if tab_order:
            # 关闭对应tab
            tab_widget.removeTab(tab_order[0])

    def get_menu_names(self, item, window):
        """
        获取树中，方法的右键菜单名字列表
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        return [OPEN_METHOD_MENU, CLOSE_METHOD_MENU]

    def handle_menu_func(self, item, func, window):
        """
        在表层，右键菜单的功能实现
        :param item: 当前点击树节点元素
        :param func: 右键菜单中功能名称
        :param window: 启动的主窗口界面对象
        """
        # 打开方法详情tab页
        if func == OPEN_METHOD_MENU:
            self.open_item(item, window)
        # 关闭方法详情tab页
        elif func == CLOSE_METHOD_MENU:
            self.close_item(item, window)
