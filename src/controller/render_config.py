import re
import logging
from pathlib import Path
from typing import List, Type
from src.utils.ConfigModel import BasicCon, SnmpCon,OptionCon
from src.controller.create_jinja2 import CreateJinja2
from src.controller.device_conf_data import DeviceConfData
from src.utils.public_method import object_to_dict


class RenderConfig:
    """
    渲染配置类，用于生成设备配置文件。

    参数:
    - jinja2_env: Jinja2环境的类型。
    - dev_config: 设备配置数据的类型。
    - basic: 基本配置数据的对象。
    - snmp: SNMP配置数据的对象。
    - ci_name: 设备名称列表。
    - save_file_path: 保存配置文件的路径。
    - template_name: 模板名称字典。
    - model_mapping: 设备型号映射字典。

    该类使用Jinja2模板和设备配置数据生成配置文件，并保存到指定路径。
    """
    def __init__(self, jinja2_env: Type[CreateJinja2],
                 dev_config: Type[DeviceConfData],
                 basic: BasicCon,
                 snmp: SnmpCon,
                 options:OptionCon,
                 ci_name: List,
                 save_file_path: str,
                 template_name: dict,
                 model_mapping: dict):
        self.jinja2_env = jinja2_env()
        self.dev_config = dev_config
        self.ci_name = ci_name
        self.save_file_path = save_file_path
        self.template_name = template_name
        self.model_mapping = model_mapping
        self.basic = basic
        self.snmp = snmp
        self.options=options

    def __split_ci_name_return_model(self, value, default='default'):
        """
        从设备名称中提取型号，并返回对应的型号名称。

        参数:
        - value: 设备名称。
        - default: 默认型号名称。

        返回:
        - 设备型号名称。
        """
        pattern = r"(?<=-)[A-Za-z]{1,2}\d{4,5}(?:\(G\))?(?=-)"
        match = re.search(pattern, value)

        if match:
            result = re.sub(r'\(G\)', '', match.group())

            for key in self.model_mapping:
                if result.startswith(key):
                    logging.debug(f"找到型号 {key} 对应设备 {value}")
                    return self.model_mapping[key]
            logging.warning(f"没有找到设备型号 {result} 的映射，直接使用型号。")
            return result
        else:
            logging.warning(f"在设备名称 {value} 中未找到型号，使用默认型号。")
            return default

    def __set_template_name(self, ci_name):
        """
        根据设备名称设置模板名称。

        参数:
        - ci_name: 设备名称。

        返回:
        - 设备对应的模板名称。
        """
        model = self.__split_ci_name_return_model(ci_name)
        template_name = self.template_name.get(model, 'base.jinja2')
        logging.debug(f"为设备 {ci_name} 使用模板 {template_name}")
        return template_name

    def __set_57xx_config(self, ci_name, data):
        """
        特殊处理S57XX型号设备的配置数据。

        参数:
        - ci_name: 设备名称。
        - data: 设备配置数据字典。

        返回:
        - 更新后的设备配置数据字典。
        """
        model = self.__split_ci_name_return_model(ci_name)
        if model == 'S57XX':
            data['option_global_vlan'] = False
            data['basic']['manage_int'] = 'MEth0/0/1'
            logging.debug(f"为 S57XX 型号应用特殊配置: {data}")
            return data
        logging.debug(f"型号 {model} 不需要特殊配置")
        return data

    def save_file(self, data, file_name):
        """
        保存配置数据到文件。

        参数:
        - data: 配置数据字符串。
        - file_name: 文件名。
        """
        path = Path(self.save_file_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        save_file = path.joinpath(file_name)
        save_file.write_text(data)
        logging.debug(f"配置文件 {file_name} 已保存到{path}目录下。")

    def build_config(self):
        """
        构建设备配置并保存。

        该方法为每个设备名称生成配置数据，使用Jinja2模板渲染配置，并保存为文本文件。
        """
        jinja2_env = self.jinja2_env.create_jinja2()
        for ci in self.ci_name:
            dev_config = self.dev_config(ci_name=ci,
                                         manage_gw_ip=self.basic.manage_gw_ip,
                                         manage_vrf_name=self.basic.manage_vrf_name,
                                         option_manage_mode=self.basic.option_manage_mode,
                                         sftp=self.basic.sftp,
                                         target_host=self.snmp.target_host,
                                         target_host_host_name=self.snmp.target_host_host_name,
                                         udp_port=self.snmp.udp_port,
                                         option_vrf=self.options.option_vrf,
                                         option_snmp=self.options.option_snmp,
                                         option_mlag=self.options.option_mlag,
                                         option_batch_vlan=self.options.option_batch_vlan,
                                         option_global_vlan=self.options.option_global_vlan,
                                         option_gw=self.options.option_gw,
                                         option_l3_vlan=self.options.option_l3_vlan,
                                         option_l3_phy=self.options.option_l3_phy,
                                         option_ndi_l2=self.options.option_ndi_l2,
                                         option_server_int=self.options.option_server_int,
                                         option_netconf=self.options.option_netconf,
                                         option_look_back=self.options.option_look_back,
                                         option_static_route=self.options.option_static_route,
                                         option_bfd=self.options.option_bfd,
                                         )
            dev_config_dict = object_to_dict(dev_config)
            dev_data = self.__set_57xx_config(ci, dev_config_dict)
            templates_name = self.__set_template_name(ci)
            template = jinja2_env.get_template(templates_name)
            config = template.render(dev_data)
            self.save_file(config, f'{ci}.txt')
            logging.info(f"设备 {ci} 的配置已保存")

