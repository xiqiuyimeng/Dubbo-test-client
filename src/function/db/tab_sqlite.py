# -*- coding: utf-8 -*-
import os
import sqlite3
from collections import namedtuple

from src.function.db.sqlite_abc import SqliteBasic

_author_ = 'luwt'
_date_ = '2021/11/11 10:32'


# 保存tab页信息 conn_id -> connection id, tab_id -> tab_id，
# pram_type -> 0:args or 1:json, param_args_dict -> input param values, param_json -> input param json,
# param_desc_dict -> input param desc, result_display -> 0:RAW or 1:JSON, request_time -> request_time,
# response_time -> response_time, method_cost -> dubbo return elapsed, result -> dubbo call result
TabObj = namedtuple('TabObj', 'id conn_id tab_id param_type param_args_dict param_json param_desc_dict '
                              'result_display request_time response_time method_cost result')


tab_sql = {
    'create': '''create table if not exists tab
    (id integer PRIMARY KEY autoincrement,
    conn_id int not null,
    tab_id text not null,
    param_type tinyint not null,
    param_args_dict text default null,
    param_json text default null,
    param_desc_dict text default null,
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
    'select_insert_id': 'select id from tab order by id desc limit 1',
    'select_by_tab_id': 'select * from tab where tab_id = ?',
    'delete_by_conn_id': 'delete from tab where conn_id = ?',
}


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

    def select_by_tab_id(self, tab_id):
        """根据tab_id来查询记录"""
        sql = tab_sql.get('select_by_tab_id')
        self.cursor.execute(sql, (tab_id, ))
        data = self.cursor.fetchone()
        return TabObj(*data) if data else TabObj(*((None,) * len(TabObj._fields)))

    def delete_by_conn_id(self, conn_id):
        sql = tab_sql.get('delete_by_conn_id')
        self.cursor.execute(sql, (conn_id,))
        self.conn.commit()
