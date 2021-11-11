# -*- coding: utf-8 -*-
import os
import sqlite3
from collections import namedtuple

from src.constant.tab_constant import ARGS_PARAM_TYPE, JSON_PARAM_TYPE, RESULT_DISPLAY_JSON, RESULT_DISPLAY_RAW
from src.function.db.sqlite_abc import SqliteBasic

_author_ = 'luwt'
_date_ = '2021/11/11 10:32'


# 保存tab页信息 tab_id -> tab_id，
# pram_type -> 0:args or 1:json or 2:None, param_values -> input param values, param_desc -> input param desc
# result_display -> 0:RAW or 1:JSON, request_time -> request_time, response_time -> response_time,
# method_cost -> dubbo return elapsed, result -> dubbo call result
TabObj = namedtuple('TabObj', 'id tab_id param_type param_args param_json param_desc '
                              'result_display request_time response_time method_cost result')


tab_sql = {
    'create': '''create table if not exists tab
    (id integer PRIMARY KEY autoincrement,
    tab_id text not null,
    param_type tinyint not null,
    param_args text default null,
    param_json text default null,
    param_desc text default null,
    result_display tinyint not null,
    request_time char(19) default null,
    response_time char(19) default null,
    method_cost int default null,
    result text default null
    );''',
    'insert': 'insert into tab ',
    'update_selective': 'update tab set ',
    'delete': 'delete from tab where id = ?',
    'select': 'select * from tab ',
    'select_by_tab_id': 'select * from tab where tab_id = ?'
}


param_types = (ARGS_PARAM_TYPE, JSON_PARAM_TYPE, None)
result_display_tuple = (RESULT_DISPLAY_RAW, RESULT_DISPLAY_JSON)


def convert_to_str(tab_obj_dict: dict):
    # 转化param_type, 0:args or 1:json or 2:None
    tab_obj_dict['param_type'] = param_types[tab_obj_dict.get('param_type')]
    # 转化result_display, 0:raw or 1:json
    tab_obj_dict['result_display'] = result_display_tuple[tab_obj_dict.get('result_display')]
    return TabObj(**tab_obj_dict)


def convert_to_tinyint(tab_obj_dict: dict):
    # 转化param_type, 0:args or 1:json or 2:None
    tab_obj_dict['param_type'] = param_types.index(tab_obj_dict.get('param_type'))
    # 转化result_display, 0:raw or 1:json
    tab_obj_dict['result_display'] = result_display_tuple.index(tab_obj_dict.get('result_display'))
    return TabObj(**tab_obj_dict)


class TabSqlite(SqliteBasic):

    def __new__(cls, *args, **kwargs):
        # 控制单例，只连接一次库，避免多次无用的连接
        if not hasattr(TabSqlite, 'instance'):
            TabSqlite.instance = object.__new__(cls)
            if not os.path.exists(os.path.dirname(__file__)):
                os.makedirs(os.path.dirname(__file__))
            db = os.path.dirname(__file__) + '/' + 'tab_db'
            TabSqlite.instance.conn = sqlite3.connect(db, check_same_thread=False)
            TabSqlite.instance.cursor = TabSqlite.instance.conn.cursor()
            TabSqlite.instance.cursor.execute(tab_sql.get('create'))
        return TabSqlite.instance

    def __init__(self):
        super().__init__(tab_sql, self.conn, self.cursor)

    def insert(self, tab_obj_dict: dict):
        super().insert(convert_to_tinyint(tab_obj_dict))

    def update_selective(self, tab_obj_dict: dict):
        super().update_selective(convert_to_tinyint(tab_obj_dict))

    def select_by_tab_id(self, tab_id):
        """根据tab_id来查询记录"""
        sql = tab_sql.get('select_by_tab_id')
        self.cursor.execute(sql, (tab_id, ))
        data = self.cursor.fetchone()
        if data:
            return convert_to_str(data[0])
