# -*- coding: utf-8 -*-
"""
异步刷新连接，需要考虑的是opened item表和tab表数据，以及对应页面展示
根据连接id查询opened item表，查询service，如果能查询到，则调用telnet查出当前所有service
如果查询不到，则结束；telnet出的service list 和 表里的service list进行对比，如果一致，也就是名称一致，继续；
如果不一致，找到不一致的信息，以telnet得到的为准，进行更新；再查询所有的method
"""
_author_ = 'luwt'
_date_ = '2021/11/23 19:27'
