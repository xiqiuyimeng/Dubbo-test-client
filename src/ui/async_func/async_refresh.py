# -*- coding: utf-8 -*-
"""
刷新页面：由于保存了工作状态，在重新打开时，会从本地库中读取保存的工作状态，此时可能由于连接的目标服务停止等原因导致数据变化，
        目标服务连接不上，导致无法刷新到数据，则会清除原工作状态，这应该交由用户来决定刷新哪个连接，而不应该直接刷新所有连接，
        导致某些重要工作状态丢失。
        所以在刷新时，务必有选中的连接，当然也应该支持更细粒度的刷新
    刷新 连接：重新连接dubbo服务，
    刷新 服务：重新连接dubbo服务，获取当前服务下所有方法信息，更新叶子节点并保存
    刷新 方法：由于支持删除保存的操作记录，刷新方法时，应该读取最新的tab表记录
"""
_author_ = 'luwt'
_date_ = '2021/12/7 11:50'


