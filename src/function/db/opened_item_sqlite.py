# -*- coding: utf-8 -*-
import os
import sqlite3
from collections import namedtuple

from src.function.db.sqlite_abc import SqliteBasic

_author_ = 'luwt'
_date_ = '2021/11/12 16:56'

# item_name：打开的项目名称，在树结构中展示的名称，ext_info：一些其他信息，item_order：展示顺序，is_current：是否是当前项
# expanded：是否展开，parent_id：父id，level：在树结构中的级别，树结构：（0，1，2），tab页：3
OpenedItem = namedtuple('OpenedItem', 'id item_name ext_info item_order is_current expanded parent_id level')

opened_item_sql = {
    'create': '''create table if not exists opened_item
    (id integer PRIMARY KEY autoincrement,
    item_name text default null,
    ext_info text default null,
    item_order int default null,
    is_current int not null,
    expanded int not null,
    parent_id int not null,
    level int not null
    );''',
    'insert': 'insert into opened_item ',
    'update_selective': 'update opened_item set ',
    'delete': 'delete from opened_item where id = ?',
    'delete_by_name': 'delete from opened_item where item_name = ?',
    'select': 'select * from opened_item',
    'select_insert_id': 'select id from opened_item order by id desc limit 1',
    'select_children': 'select * from opened_item where level = ? and parent_id in ',
    'select_by_name': 'select * from opened_item where item_name = ?',
    'reset_current': 'update opened_item set is_current = 0 where is_current = 1',
    'set_current': 'update opened_item set is_current = 1 where item_name = ?',
    'batch_delete': 'delete from opened_item where id in ',
    'delete_by_parent': 'delete from opened_item where parent_id = ?',
    'batch_update_order': 'update opened_item set item_order = case item_name {} end where item_name in ({})',
}


class OpenedItemSqlite(SqliteBasic):

    def __new__(cls, *args, **kwargs):
        # 控制单例，只连接一次库，避免多次无用的连接
        if not hasattr(OpenedItemSqlite, 'instance'):
            OpenedItemSqlite.instance = object.__new__(cls)
            if not os.path.exists(os.path.dirname(__file__)):
                os.makedirs(os.path.dirname(__file__))
            db = os.path.dirname(__file__) + '/' + 'opened_item_db'
            OpenedItemSqlite.instance.conn = sqlite3.connect(db, check_same_thread=False)
            OpenedItemSqlite.instance.cursor = OpenedItemSqlite.instance.conn.cursor()
            OpenedItemSqlite.instance.cursor.execute(opened_item_sql.get('create'))
        return OpenedItemSqlite.instance

    def __init__(self):
        super().__init__(opened_item_sql, self.conn, self.cursor)

    def add_tab(self, mapping_obj):
        self.reset_current()
        super().insert(mapping_obj)

    def select_children(self, parent_id, level):
        self.cursor.execute(f"{opened_item_sql.get('select_children')}(?)", (level, parent_id))
        data = self.cursor.fetchall()
        result = list()
        [result.append(OpenedItem(*row)) for row in data]
        return result

    def select_by_name(self, item_name):
        """根据名称查询"""
        sql = opened_item_sql.get('select_by_name')
        self.cursor.execute(sql, (item_name,))
        data = self.cursor.fetchone()
        return OpenedItem(*data) if data else None

    def update_expanded(self, item_id, expanded):
        """更改expanded状态"""
        sql = f"{opened_item_sql.get('update_selective')}expanded = ? where id = ?"
        self.cursor.execute(sql, (1 if expanded else 0, item_id))
        self.conn.commit()

    def reset_current(self):
        reset_sql = opened_item_sql.get('reset_current')
        self.cursor.execute(reset_sql)

    def update_current(self, item_name):
        """更新is current"""
        # 首先重置当前项
        self.reset_current()
        # 将当前项置为当前
        set_sql = opened_item_sql.get('set_current')
        self.cursor.execute(set_sql, (item_name,))
        self.conn.commit()

    def update_order(self, item_names: list):
        """更新order"""
        when_clause = 'when ? then ? ' * len(item_names)
        sql = opened_item_sql.get('batch_update_order').format(when_clause, ','.join('?' * len(item_names)))
        param = list()
        for order, item_name in enumerate(item_names):
            param.append(item_name)
            param.append(order)
        param.extend(item_names)
        self.cursor.execute(sql, param)
        self.conn.commit()

    def delete_by_name(self, item_name):
        sql = opened_item_sql.get('delete_by_name')
        self.cursor.execute(sql, (item_name,))
        self.conn.commit()

    def recursive_delete(self, parent_id, level=0):
        # 递归删除
        if level <= 3:
            self.cursor.execute(f"{opened_item_sql.get('select_children')}(?)", (level, parent_id))
            data = self.cursor.fetchall()
            if data:
                children_ids = tuple(map(lambda x: x[0], data))
                sql = f"{opened_item_sql.get('batch_delete')}({', '.join('?' * (len(children_ids)))})"
                self.cursor.execute(sql, children_ids)
                self.conn.commit()
                level += 1
                [self.recursive_delete(child_id, level) for child_id in children_ids]

    def get_tab_orders(self, parent_ids, level=0):
        sql = f"{opened_item_sql.get('select_children')}({','.join('?' * len(parent_ids))})"
        self.cursor.execute(sql, (level, *parent_ids))
        data = self.cursor.fetchall()
        if data:
            if level == 3:
                return list(map(lambda x: x[3], data))
            else:
                return self.get_tab_orders(list(map(lambda x: x[0], data)), level + 1)

    def delete_by_parent(self, parent_id):
        sql = opened_item_sql.get('delete_by_parent')
        self.cursor.execute(sql, (parent_id, ))
        self.conn.commit()
