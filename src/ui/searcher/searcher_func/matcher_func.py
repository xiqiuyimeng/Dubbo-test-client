# -*- coding: utf-8 -*-
_author_ = 'luwt'
_date_ = '2022/1/20 20:00'


class Matcher:
    """文本搜索匹配，以左边为整词的原则匹配，尽量减少匹配次数"""
    def __init__(self, original_text):
        self.original_text = original_text
        self.match_idx_list = list()
        self.rest_start_idx = 0
        self.match_flag = False

    def smart_match(self, text):
        """匹配文本，首先使用全词匹配，失败后进行拆分匹配"""
        parser = MatchParser(self.original_text)
        if parser.match_parse(text):
            self.match_idx_list = parser.match_idx_list
        else:
            self.split_match(text)
        return self.match_idx_list

    def split_match(self, text, left_text=None):
        """拆分匹配，以左边为整词原则拆分匹配"""
        if self.match_flag:
            return
        # 拆分
        len_text = len(text)
        if len_text > 1:
            for i in range(1, len_text):
                left, right = text[:len_text - i], text[len_text - i:]
                if left_text is not None:
                    # 如果left_text不是none，说明上一层左边有值，应该再追加上当前拆分的left，作为入参传递到一层
                    if isinstance(left_text, list):
                        left = [*left_text, left]
                    else:
                        left = [left_text, left]
                # 拆分结束后，进行匹配，如果匹配成功则返回，否则继续处理
                parser = MatchParser(self.original_text)
                if parser.match_all(left, right):
                    self.match_idx_list = parser.match_idx_list
                    self.match_flag = True
                    return
                if len(right) > 1:
                    # 进一步的拆分 right
                    self.split_match(right, left)


class MatchParser:
    """实际匹配解析类"""
    def __init__(self, original_text):
        # 返回结果为列表，元素是匹配的索引值，前后均是闭区间
        self.match_idx_list = list()
        self.rest_start_idx = 0
        self.original_text = original_text

    def match_all(self, left_text, right_text):
        """根据左右文本匹配，都匹配成功视为成功"""
        # 先匹配左边
        if isinstance(left_text, list):
            for text in left_text:
                if not self.match_parse(text):
                    return
        else:
            if not self.match_parse(left_text):
                return
        # 处理右边
        if not self.match_parse(right_text):
            return
        return True

    def match_parse(self, text):
        match_result = self.match(text)
        if match_result:
            self.match_idx_list.append((match_result[0] + self.rest_start_idx,
                                        match_result[1] + self.rest_start_idx))
            self.original_text = self.original_text[match_result[1] + 1:]
            self.rest_start_idx = self.rest_start_idx + match_result[1] + 1
            return True

    def match(self, text):
        if text.lower() in self.original_text.lower():
            start_idx = self.original_text.lower().index(text.lower())
            return start_idx, start_idx + len(text) - 1
