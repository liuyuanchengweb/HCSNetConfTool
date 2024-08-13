import yaml
import logging
from src.controller import DeviceConfData
from src.utils.ConfigModel import BasicCon, SnmpCon, OptionCon
from src.utils.dev_con_file_path import CONFIG_FILE
from src.utils.public_method import object_to_dict


class InitConfig:

    def __init__(self):
        self.basic_config = self.create_basic_config()
        self.snmp_config = self.create_snmp_config()
        self.option_config = self.create_option_config()
        self.ci_name_list = DeviceConfData.get_device_data()

    @staticmethod
    def create_basic_config():
        basic = BasicCon()
        return basic.model_dump()

    @staticmethod
    def create_snmp_config():
        snmp = SnmpCon()
        return snmp.model_dump()

    @staticmethod
    def create_option_config():
        option = OptionCon()
        return option.model_dump()

    def to_dict(self):
        return object_to_dict(self)

    def to_yaml(self) -> str:
        return f"""
# 该配置文件主要用于补充LLD内没有的数据，以下是配置项的说明，以及用法。
# basic配置项说明
# manage_gw_ip：设备地址的网关
# manage_vrf_name：设备管理地址所绑定的VRF
# option_manage_mode：设备管理模式，false是带外管理，管理IP配置在Meth接口，如果是true,则使用LLD中的vlan_id生成vlanif接口，配置在vlanif接口下面。
# sftp：是否开启sftp功能，false不开启。

{self.create_basic_yaml()}
#
# snmp配置项说明
# target_host：esight主机地址，或者运维平台地址
# target_host_host_name：host name 字符串形式，不支持空格，区分大小写，长度范围是1～32。当输入的字符串两端使用双引号时，可在字符串中输入空格。可以使用默认，则使用ip地址计算出来字符串填充。
# udp_port： 运维主机端口号

{self.create_snmp_yaml()}
# ci_name_list: 该配置项是通过LLD解析出来可以生成配置的设备，可以通过该配置项生成指定设备的配置，只能从该列表内进行选择，默认解析除FW外的所有网络设备。

{self.create_ci_name_yaml()}

# option配置项说明
{self.create_option_yaml()}
        """

    def create_basic_yaml(self):
        basic_dict = {'basic_config': object_to_dict(self.basic_config)}
        return yaml.dump(basic_dict, default_flow_style=False)

    def create_snmp_yaml(self):
        snmp_dict = {'snmp_config': object_to_dict(self.snmp_config)}
        return yaml.dump(snmp_dict, default_flow_style=False)

    def create_ci_name_yaml(self):
        device_dict = {'ci_name_list': self.ci_name_list}
        return yaml.dump(device_dict, default_flow_style=False)

    def create_option_yaml(self):
        option_dict = {'option_config': object_to_dict(self.option_config)}
        return yaml.dump(option_dict, default_flow_style=False)

    def init(self):
        """Initialize the configuration by writing YAML data to a file."""
        try:
            data = self.to_yaml()
            CONFIG_FILE.write_text(data, encoding='utf-8')
            logging.info(f"初始化完成，请查看修改{CONFIG_FILE}配置文件，修改完成后使用 run执行生成配置文件")
        except Exception as e:
            logging.info(f"初始化配置失败: {e}")


