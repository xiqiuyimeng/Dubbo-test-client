# -*- coding: utf-8 -*-
from telnetlib import Telnet
import re
_author_ = 'luwt'
_date_ = '2021/10/29 09:35'


# 默认超时时间3秒
DEFAULT_TIMEOUT = 3000
# 提示符
PROMPT = 'dubbo>'
# 匹配方法名和参数的正则
METHOD_PATTERN = r"(?P<result_type>.+) (?P<method_name>.+)\((?P<param_type>.*)\)"


class DubboConn:

    def __init__(self, host, port, timeout=DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.conn = self.connect()

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            raise exc_tb
        self.conn.close()

    def connect(self):
        conn = Telnet(self.host, self.port, int(self.timeout))
        return conn


class DubboClient:

    def __init__(self, host, port, timeout=DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout

    def execute(self, cmd):
        with DubboConn(self.host, self.port, self.timeout) as conn:
            conn.write(f'{cmd}\n'.encode())
            response = conn.read_until(PROMPT.encode()).decode()
            return response.split(PROMPT)[0]

    def test_connection(self):
        self.execute("")

    def get_service_list(self):
        cmd = 'ls'
        service_str = self.execute(cmd)
        # 去除consumer信息
        return (service_str.strip().split("\r\nCONSUMER")[0]).split("\r\n")[1:]

    def get_method_list(self, target):
        cmd = 'ls -l' if target is None else f'ls -l {target}'
        method_str = self.execute(cmd)
        method_list = method_str.strip().split("\r\n")
        if f'{target} (as consumer):' in method_list:
            idx = method_list.index(f'{target} (as consumer):')
            provider_list = method_list[1:idx]
        else:
            provider_list = method_list[1:]
        # 获取到提供服务的方法信息
        provider_method_list = list(map(lambda x: x.lstrip('\t'), provider_list))
        # 返回数据 [{"method_name": "", "param_type": "", "result_type": ""}]
        return list(map(lambda x: parse_method(x), provider_method_list))

    def invoke(self, method):
        cmd = f'invoke {method}'
        return self.execute(cmd)


def parse_method(method_str):
    method_res = re.match(METHOD_PATTERN, method_str)
    return {
        "method_name": method_res.group("method_name"),
        "result_type": method_res.group("result_type"),
        "param_type": method_res.group("param_type")
    }
