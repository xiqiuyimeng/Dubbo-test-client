# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

from PyQt5.QtGui import QIcon

from src.constant.main_constant import CLOSE_CONN_MENU, OPEN_CONN_MENU, TEST_CONN_MENU, ADD_CONN_MENU, EDIT_CONN_MENU, \
    DEL_CONN_MENU, OPEN_SERVICE_MENU, CLOSE_SERVICE_MENU
from src.function.dubbo.dubbo_client import DubboClient
from src.ui.box.message_box import pop_fail, pop_ok
from src.ui.func.common import exception_handler
from src.ui.tab.tab_ui import TabUI
from src.ui.tree_item.my_tree_item import MyTreeWidgetItem

_author_ = 'luwt'
_date_ = '2021/11/3 22:36'


def add_conn_item(window, conn):
    """添加连接树节点"""
    # item属性：id name host port timeout
    # 根节点，展示连接的列表，将连接信息写入隐藏列
    make_tree_item(window.tree_widget, conn.name, QIcon(":/icon/mysql_conn_icon.png"),
                   hidden_text=dict(zip(conn._fields, conn)))


def make_tree_item(parent, text, icon, checkbox=None, hidden_text=None):
    """
    构造树的子项
    :param parent: 要构造子项的父节点元素
    :param text: 构造的子节点信息
    :param icon: 图标，该元素的展示图标对象
    :param checkbox: 构造的子节点的复选框，可无。若存在，将当前状态写入第三列中
    :param hidden_text: 隐藏信息
    """
    item = MyTreeWidgetItem(parent)
    item.setIcon(0, icon)
    item.setText(0, text)
    if hidden_text:
        #  作为隐藏属性，写于第二列
        item.setText(1, hidden_text)
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


class Context:

    def __init__(self, tree_node):
        self.tree_node = tree_node

    def open_item(self, item, window):
        return self.tree_node.open_item(item, window=window)

    def close_item(self, item, window):
        return self.tree_node.close_item(item, window)

    def change_check_box(self, item, check_state, window):
        return self.tree_node.change_check_box(item, check_state, window)

    def get_menu_names(self, item, window):
        return self.tree_node.get_menu_names(item, window)

    def handle_menu_func(self, item, func, window):
        return self.tree_node.handle_menu_func(item, func, window)


class TreeNodeAbstract(ABC):

    @abstractmethod
    def open_item(self, item, window): ...

    @abstractmethod
    def close_item(self, item, window): ...

    @abstractmethod
    def change_check_box(self, item, check_state, window): ...

    @abstractmethod
    def get_menu_names(self, item, window): ...

    @abstractmethod
    def handle_menu_func(self, item, func, window): ...


class TreeNodeConn(TreeNodeAbstract, ABC):

    @exception_handler(pop_fail, "打开连接失败")
    def open_item(self, item, window):
        """
        打开连接，展示连接下的所有service列表
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        # 仅当子元素不存在时，获取子元素并填充
        if item.childCount() == 0:
            # 连接的id，连接名称
            conn_info = eval(item.text(1))
            client = DubboClient(conn_info.get("host"), conn_info.get("port"), conn_info.get("timeout"))
            service_list = client.get_service_list()
            for service in service_list:
                make_tree_item(item, service, QIcon(":/icon/mysql_conn_icon.png"))

    def close_item(self, item, window):
        """
        关闭树的某项，将其下所有子项移除，并将扩展状态置为false
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        TreeNodeDB().close_item(item, window)
        item.setExpanded(False)

    def change_check_box(self, item, check_state, window): ...

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
            item.setExpanded(True)
        # 关闭连接
        elif func == CLOSE_CONN_MENU:
            if self.close_conn(conn_name, func, window):
                self.close_item(item, window)
        # 测试连接
        elif func == TEST_CONN_MENU:
            self.test_conn(eval(item.text(1)), window=window)
        # 添加连接
        elif func == ADD_CONN_MENU:
            window.add_conn()
        # 编辑连接
        elif func == EDIT_CONN_MENU:
            self.edit_conn(func, window, conn_name, conn_id, item)
        # 删除连接
        elif func == DEL_CONN_MENU:
            self.del_conn(func, window, conn_name, conn_id, item)

    @exception_handler(pop_fail, "测试连接失败")
    def test_conn(self, conn_info, window):
        DubboClient(conn_info.get("host"), conn_info.get("port"), conn_info.get("timeout")).test_connection()
        pop_ok("测试连接成功", "测试连接", window)

    @staticmethod
    def close_conn(conn_name, func, window):
        """
        关闭数据连接，关闭特定连接，name为标识，
        如果在此连接下已选择了字段。那么弹窗确认是否关闭，
        如果关闭将清空此连接所选的字段
        :param conn_name: 连接名称
        :param func: 功能名称，用于展示在弹窗标题处
        :param window: 启动的主窗口界面对象
        """
        if SelectedData().get_db_dict(conn_name, True):
            reply = pop_question(func, CLOSE_CONN_PROMPT)
            if reply:
                SelectedData().unset_conn(conn_name)
            else:
                return False
        close_connection(window, conn_name)
        return True

    def edit_conn(self, func, window, conn_name, conn_id, item):
        """
        编辑连接，首先需要判断连接是否打开，
        如果打开，进一步判断是否有选中的字段数据，如果有，
        则弹窗提示需要先关闭连接并清空字段。
        如果没有选中字段，则弹窗需要关闭连接。
        否则直接弹编辑窗口
        :param func: 功能名称
        :param window: 启动的主窗口界面对象
        :param conn_name: 连接名称
        :param conn_id: 连接id
        :param item: 当前点击树节点元素
        """
        # 先判断是否打开
        if item.isExpanded():
            # 再判断是否有选中字段
            if SelectedData().get_db_dict(conn_name, True):
                if pop_question(func, EDIT_CONN_WITH_FIELD_PROMPT):
                    SelectedData().unset_conn(conn_name)
                    # 关闭连接
                    close_connection(window, conn_name)
                    self.close_item(item, window)
                else:
                    return
            else:
                if pop_question(func, EDIT_CONN_PROMPT):
                    # 关闭连接
                    close_connection(window, conn_name)
                    self.close_item(item, window)
                else:
                    return
        conn_info = window.display_conn_dict.get(conn_id)
        show_conn_dialog(window, conn_info, func, window.screen_rect)

    def del_conn(self, func, window, conn_name, conn_id, item):
        """
        删除连接，如果连接下有选择字段，弹窗确认是否清空字段并删除连接，
        否则弹窗是否删除连接
        :param func: 功能名称
        :param window: 启动的主窗口界面对象
        :param conn_name: 连接名称
        :param conn_id: 连接id
        :param item: 当前点击树节点元素
        """
        # 判断是否有选择字段
        if SelectedData().get_db_dict(conn_name, True):
            if pop_question(func, DEL_CONN_WITH_FIELD_PROMPT):
                SelectedData().unset_conn(conn_name)
                self.close_and_delete_conn(window, conn_name, conn_id, item)
        else:
            # 弹出关闭连接确认框
            if pop_question(func, DEL_CONN_PROMPT):
                self.close_and_delete_conn(window, conn_name, conn_id, item)

    def close_and_delete_conn(self, window, conn_name, conn_id, item):
        """
        关闭连接，删除连接
        :param window: 启动的主窗口界面对象
        :param conn_name: 连接名称
        :param conn_id: 连接id
        :param item: 当前点击树节点元素
        """
        self.close_item(item, window)
        # 关闭连接
        close_connection(window, conn_name)
        conn_info = window.display_conn_dict[conn_id]
        ConnSqlite().delete(conn_info.id)
        del window.display_conn_dict[conn_id]
        # 删除树元素
        # 树型部件的takeTopLevelItem方法可以从树型部件中删除对应项的节点并返回该项，语法：takeTopLevelItem(index)
        # 通过调用树型部件的indexOfTopLevelItem方法可以获得对应项在顶层项的位置，语法：indexOfTopLevelItem
        #
        # self.treeWidget.removeItemWidget，它从一个项中移除一个小部件，而不是QTreeWidgetItem。它对应于setItemWidget方法
        window.treeWidget.takeTopLevelItem(window.treeWidget.indexOfTopLevelItem(item))

    @staticmethod
    def get_node_info(item):
        """获取连接id和连接名称"""
        conn_id = int(item.text(1))
        conn_name = item.text(0)
        return conn_id, conn_name


class TreeNodeService(TreeNodeAbstract, ABC):

    @exception_handler(pop_fail, "打开连接失败")
    def open_item(self, item, window):
        """
        展示该服务下的所有方法，
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        # 仅当子元素不存在时，获取子元素并填充
        if item.childCount() == 0:
            # 获取连接id和名称
            conn_info = eval(item.parent().text(1))
            client = DubboClient(conn_info.get("host"), conn_info.get("port"), conn_info.get("timeout"))
            method_list = client.get_method_list(item.text(0))
            for method_dict in method_list:
                # 将方法详细信息写入隐藏列
                make_tree_item(item, method_dict.get("method_name"),
                               QIcon(":/icon/mysql_conn_icon.png"), hidden_text=method_dict)

    def close_item(self, item, window):
        """
        关闭树的某项，将其下所有子项移除，并将扩展状态置为false
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        # 关闭表格，由于当前item不是表，所以应该使用当前表对象（如果有的话）
        if hasattr(window, 'table_frame'):
            TreeNodeTable().close_item(window.current_table, window)
        # 移除所有子项目
        item.takeChildren()
        item.setExpanded(False)

    def change_check_box(self, item, check_state, window): ...

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
        在数据库层，右键菜单的功能实现
        :param item: 当前点击树节点元素
        :param func: 右键菜单中功能名称
        :param window: 启动的主窗口界面对象
        """
        conn_id, conn_name, db_name = TreeNodeDB.get_node_info(item)
        # 打开数据库
        if func == OPEN_DB_MENU:
            self.open_item(item, window)
            item.setExpanded(True)
        # 关闭数据库
        elif func == CLOSE_DB_MENU:
            if self.close_db(item, func, conn_name, db_name, window):
                self.close_item(item, window)
        # 全选所有表
        elif func == SELECT_ALL_TB_MENU:
            select_table = AsyncSelectTable(window, item, conn_id, conn_name, db_name)
            select_table.select_table()
        # 取消全选表
        elif func == UNSELECT_TB_MENU:
            # 将子节点都置为未选中状态
            set_children_check_state(item, Qt.Unchecked)
            # 清空容器中的值
            SelectedData().unset_tbs(window, conn_name, db_name)
            if hasattr(window, 'table_frame') and window.current_table.parent() is item:
                change_table_checkbox(window, window.current_table, False)

    @staticmethod
    def close_db(item, func, conn_name, db_name, window):
        """
        关闭数据库，如果此库下已选择了字段，弹窗确认是否关闭，
        如果关闭，将清空此库下所选字段
        :param item: 当前点击树节点元素，也就是库
        :param func: 功能名称，用于展示在弹窗标题处
        :param conn_name: 连接名称
        :param db_name: 库名称
        :param window: 启动的主窗口界面对象
        """
        check_status = check_table_status(item)
        if any(check_status):
            if pop_question(func, CLOSE_DB_PROMPT):
                SelectedData().unset_db(window, conn_name, db_name)
            else:
                return False
        return True

    @staticmethod
    def get_node_info(item):
        """获取连接id、连接名称、数据库名称"""
        conn_id = int(item.parent().text(1))
        conn_name = item.parent().text(0)
        db_name = item.text(0)
        return conn_id, conn_name, db_name


class TreeNodeMethod(TreeNodeAbstract, ABC):

    def open_item(self, item, window):
        """
        打开方法节点，右侧添加一个tab页
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        conn_dict = eval(item.parent().parent().text(1))
        service_path = item.parent().text(0)
        method_dict = eval(item.text(1))
        method_name = item.text(0)
        # 首先构造tab的id：conn_id + service + method_name
        tab_id = f'{conn_dict.get("id")}-{service_path}-{method_name}'
        opened_tab_ids = window.tab_widget.opened_tab_ids
        # 如果当前方法已经打开过了，那么就将它的tab页置顶，如果没有打开过，那么再打开
        if opened_tab_ids.get(tab_id):
            window.tab_widget.setCurrentWidget(opened_tab_ids.get(tab_id))
        else:
            tab_ui = TabUI(window.tab_widget,
                           method_name,
                           service_path,
                           method_dict,
                           conn_dict,
                           tab_id)
            tab_ui.set_up_tab()
            opened_tab_ids[tab_id] = tab_ui.tab

    def close_item(self, item, window):
        """
        关闭右侧表格
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        if check_table_opened(window, item):
            # 关闭表格
            close_table(window)

    def change_check_box(self, item, check_state, window):
        """
        修改复选框状态，当前元素复选框状态应与表格控件中的复选框联动
        :param item: 当前点击树节点元素
        :param check_state: 复选框选中状态：全选、部分选、未选择
        :param window: 启动的主窗口界面对象
        """
        conn_id, conn_name, db_name, tb_name = TreeNodeTable.get_node_info(item)
        # 如果表已经选中，那么右侧表格需全选字段
        if check_state == Qt.Checked:
            select_table = AsyncSelectTable(window, item, conn_id, conn_name, db_name, tb_name)
            select_table.select_table()
        # 如果表未选中，那么右侧表格需清空选择
        elif check_state == Qt.Unchecked:
            # 从容器删除表名
            SelectedData().unset_tbs(window, conn_name, db_name, tb_name)
            change_table_checkbox(window, item, False)

    def get_menu_names(self, item, window):
        """
        获取树中，方法的右键菜单名字列表
        :param item: 当前点击树节点元素
        :param window: 启动的主窗口界面对象
        """
        table_opened = hasattr(window, 'table_frame') \
            and window.table_header.isVisible() \
            and window.current_table is item
        check_state = item.checkState(0)
        return get_table_menu_names(table_opened, check_state)

    def handle_menu_func(self, item, func, window):
        """
        在表层，右键菜单的功能实现
        :param item: 当前点击树节点元素
        :param func: 右键菜单中功能名称
        :param window: 启动的主窗口界面对象
        """
        # 打开表
        if func == OPEN_TABLE_MENU:
            self.open_item(item, window)
        # 关闭表
        elif func == CLOSE_TABLE_MENU:
            close_table(window)
        # 全选字段
        elif func == SELECT_ALL_FIELD_MENU:
            item.setCheckState(0, Qt.Checked)
            self.change_check_box(item, Qt.Checked, window)
        # 取消选择字段
        elif func == UNSELECT_FIELD_MENU:
            item.setCheckState(0, Qt.Unchecked)
            self.change_check_box(item, Qt.Unchecked, window)

    @staticmethod
    def get_node_info(item):
        """获取连接id，连接名称，数据库名，表名"""
        conn_id = int(item.parent().parent().text(1))
        conn_name = item.parent().parent().text(0)
        db_name = item.parent().text(0)
        tb_name = item.text(0)
        return conn_id, conn_name, db_name, tb_name
