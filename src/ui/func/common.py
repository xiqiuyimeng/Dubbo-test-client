# -*- coding: utf-8 -*-
from functools import wraps

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

_author_ = 'luwt'
_date_ = '2021/11/1 11:27'


def keep_center(window, screen_rect):
    # 获取当前窗口（window）坐标系
    window_rect = window.geometry()
    # 计算新的位置，使窗体在参照物（screen_rect）中心
    center_left = (screen_rect.width() - window_rect.width()) >> 1
    center_top = (screen_rect.height() - window_rect.height()) >> 1
    # 为了保证在参照物的中心，需要跟随当前参照物的位置移动
    window.move(center_left + screen_rect.x(), center_top + screen_rect.y())


def exception_handler(callback_f, *callback_args):
    """
    捕获异常，并按照callback_f来处理异常
    """
    def wrap(f):
        @wraps(f)
        def handler(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                # kwargs，取出window
                callback_f(f'{callback_args[0]}\n{e}', kwargs.get("window"))
        return handler
    return wrap


def set_up_label(parent: QWidget, text: str, layout: [QVBoxLayout, QHBoxLayout], obj_name: str):
    """建立label"""
    label = QLabel(parent)
    label.setObjectName(obj_name)
    label.setText(text)
    layout.addWidget(label)

