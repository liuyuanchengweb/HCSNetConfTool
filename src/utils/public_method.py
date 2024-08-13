import re
from enum import Enum
from typing import Any, Union, Dict, List
from dataclasses import asdict, is_dataclass
from pydantic import BaseModel


class NumberFormatter:
    def __init__(self, input_str):
        self.input_str = input_str
        self.numbers = []

    def expand_ranges(self):
        """从输入字符串中提取数字和连续范围，并返回一个整数列表。"""
        numbers_list = []
        try:
            for segment in self.input_str.split(","):
                if '-' in segment:
                    start, end = map(int, segment.split('-'))
                    numbers_list.extend(list(range(start, end + 1)))
                else:
                    # 添加对单个数字的处理
                    numbers_list.append(int(segment.strip()))
        except ValueError:
            # 捕获 ValueError 异常，将 input_str 设置为 None
            self.input_str = None
            return
        self.numbers = numbers_list

    def sort_numbers(self):
        """对数字列表进行排序。"""
        self.numbers = sorted(self.numbers)

    def format_consecutive_numbers(self):
        """将连续的数字序列转换为 'x to y' 的形式。"""
        formatted = []
        start = self.numbers[0]
        for i in range(1, len(self.numbers)):
            if self.numbers[i] - self.numbers[i - 1] > 1:
                if start == self.numbers[i - 1]:
                    formatted.append(str(start))
                else:
                    formatted.append(f"{start} to {self.numbers[i - 1]}")
                start = self.numbers[i]
        if start == self.numbers[-1]:
            formatted.append(str(start))
        else:
            formatted.append(f"{start} to {self.numbers[-1]}")
        return formatted

    @staticmethod
    def join_results(results):
        """将格式化后的结果转换为一个用空格分隔的字符串。"""
        return " ".join(results)

    def process_input(self):
        """处理输入字符串，返回格式化的结果。"""
        # 如果 input_str 为 None，直接返回 None
        if self.input_str is None:
            return None

        # 直接返回包含 'to' 的字符串或由空格分隔的单个数字组成的字符串
        if 'to' in self.input_str or re.match(r'^\d+(\s+\d+)*$', self.input_str):
            return self.input_str

        self.expand_ranges()
        # 如果在 expand_ranges 中捕获到 ValueError，则返回 None
        if self.input_str is None:
            return None
        self.sort_numbers()
        formatted_numbers = self.format_consecutive_numbers()
        result_str = self.join_results(formatted_numbers)
        return result_str


def is_valid_eth_trunk(value: Any) -> bool:
    """
            检查 eth_trunk 值是否为有效的整数.

            Parameters:
                value (Any): 需要检查的 eth_trunk 值.

            Returns:
                bool: eth_trunk 值是否为有效的整数.
            """
    try:
        int(value)
        return True
    except (TypeError, ValueError):
        return False


def object_to_dict(obj: Any) -> Union[Dict, List, Any]:
    """Convert an object to a dictionary, handling nested objects and lists."""

    if isinstance(obj, BaseModel):
        # For Pydantic models
        obj_dict = obj.dict()

    elif is_dataclass(obj):
        # For dataclasses
        obj_dict = asdict(obj)

    elif isinstance(obj, dict):
        obj_dict = obj

    else:
        # For other objects, use __dict__ if available
        obj_dict = obj.__dict__

    result = {}
    for key, value in obj_dict.items():
        if isinstance(value, BaseModel):
            result[key] = object_to_dict(value)
        elif is_dataclass(value):
            result[key] = object_to_dict(value)
        elif isinstance(value, list):
            result[key] = [object_to_dict(item) if isinstance(item, (BaseModel, dict)) or is_dataclass(item) else item
                           for item in value]
        elif isinstance(value, Enum):
            result[key] = value.name  # Convert Enum to its name (string)
        else:
            result[key] = value

    return result
