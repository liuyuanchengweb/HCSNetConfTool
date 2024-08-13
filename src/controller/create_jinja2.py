import re
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from src.config.app_config_loader import app_config


class CreateJinja2:
    def __init__(self):
        self.templates_dir = app_config.templates_dir
        self.templates_path = self.get_templates_path()

    @staticmethod
    def stp_root_filter(value):
        """
        :param value:
        :return:
        过滤器，根据设备名称判断是否配置stp根桥
        """
        cs_or_spine = re.search(r'(cs|spine|core)', value)
        if cs_or_spine:
            logging.debug(f"找到 'cs|spine|core' 在 {value} 中")
            return True
        return False

    @staticmethod
    def unique_by_eth_trunk(data):
        """
        :param data:
        :return:
        过滤器，用于生成唯一eth-trunk接口，数据源是按照物理口进行采集的，如果不过滤，则会导致渲染出多个相同eth-trunk接口
        """
        seen_eth_trunks = set()
        unique_data = []
        for item in data:
            if item['eth_trunk'] not in seen_eth_trunks:
                unique_data.append(item)
                seen_eth_trunks.add(item['eth_trunk'])
                logging.debug(f"已添加 eth_trunk {item['eth_trunk']} 到唯一数据")
        return unique_data

    @staticmethod
    def split_and_return_first_part(value):
        """
        Split the string by '_' and return the first part.
        过滤器，用于生成eth口的接口描述，实现功能，把对端设置接口号分割了
        """
        logging.debug(f"提取字符串 '{value}' 的第一部分: {value.split('_')[0]}")
        return value.split('_')[0]

    def get_templates_path(self):
        """
        获取模板文件路径

        通过将当前文件的父级目录的父级目录与预定义的模板目录名拼接，来获取模板文件的绝对路径。
        此方法确保无论代码在何处执行，都能正确地找到模板文件的位置。

        Returns:
            str: 模板文件的路径字符串
        """
        path = Path(__file__).parent.parent.parent.joinpath(self.templates_dir)
        logging.debug(f"模板路径: {str(path)}")
        return str(path)

    def create_jinja2(self):
        """
        :return: env
        创建一个jinja2对象
        """
        file_loader = FileSystemLoader(self.templates_path)
        env = Environment(loader=file_loader)
        env.filters['stp_root_filter'] = self.stp_root_filter
        env.filters['unique_by_eth_trunk'] = self.unique_by_eth_trunk
        env.filters['first_part'] = self.split_and_return_first_part
        logging.info("创建 Jinja2 环境完成")
        return env

