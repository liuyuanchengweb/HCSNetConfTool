import logging
import ipaddress
import itertools
import json
import re
from dataclasses import asdict
from pydantic import BaseModel
import pandas as pd
from typing import TypeVar, Dict, List, Any, Callable
from src.models import map
from src.models.dev_Config import (DeviceBasicsConfig,
                                   DeviceSNMPConfig,
                                   DeviceInterfaceConfig,
                                   DevMLAGConfig,
                                   DevNetConf,
                                   DeviceL3IntConfig,
                                   LookbackConfig,
                                   VrfConfig,
                                   DeviceGWConfig,
                                   DevStaticRouteConfig,
                                   DevBFDConfig,
                                   GlobalVlan)


class DevicesConfigDict(dict):
    def __convert_to_dict(self, data: Any) -> Any:
        """
        将数据类实例、Pydantic模型或其他对象转换为字典，以支持JSON序列化。
        :param data: 可能是列表、字典、数据类实例或Pydantic模型的任意数据。
        :return: 转换后的数据。
        """
        if isinstance(data, list):
            return [self.__convert_to_dict(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.__convert_to_dict(value) for key, value in data.items()}
        elif hasattr(data, '__dict__'):
            if isinstance(data, BaseModel):
                return self.__convert_to_dict(data.dict())
            return self.__convert_to_dict(asdict(data))
        else:
            return data

    def to_json(self) -> str:
        """
        将DevicesConfigDict实例转换为JSON字符串。
        """
        try:
            device_dict = {key: self.__convert_to_dict(value) for key, value in self.items()}
            return json.dumps(device_dict, indent=4)
        except Exception as e:
            logging.error(f"Error converting to JSON: {e}")
            return ""

    def to_dict(self) -> dict:
        """
        将DevicesConfigDict实例转换为普通的字典。
        """
        try:
            return self.__convert_to_dict(self)
        except Exception as e:
            logging.error(f"Error converting to dict: {e}")
            return {}


class NetDevBase:
    """
    网络设备基类，用于处理网络设备的相关信息。
    """

    def __init__(self, data_frame: pd.DataFrame, table_head):
        """
        初始化方法，接受一个DataFrame和表头信息作为参数。

        参数:
        data_frame: pandas.DataFrame, 包含设备信息的数据框。
        table_head: 表头信息，用于识别数据框中的列。
        """
        if data_frame.empty:
            raise ValueError("提供的DataFrame为空，请提供一个非空的DataFrame以初始化对象。")
        self.__df = data_frame
        self.__table_head = table_head

    def __set_table_head_attribute(self, attr_name, attr_value):
        """
        内部方法，用于设置表头属性。

        参数:
        - attr_name: 要设置的属性名称
        - attr_value: 要设置的属性值

        该方法尝试使用setattr函数动态设置表头对象的属性，如果设置失败会捕获AttributeError异常并打印错误信息。
        """
        try:
            setattr(self.__table_head, attr_name, attr_value)
            logging.debug(f"设置属性成功: {attr_name} = {attr_value}")
        except AttributeError as e:
            logging.error(f"设置属性时出现错误: {e}，尝试设置的属性名为: {attr_name}，属性值为: {attr_value}")

    def set_table_head(self, table_head: dict):
        """
        设置表头属性的方法，接受一个字典类型的参数。

        参数:
        - table_head: 包含表头属性名和属性值的字典

        该方法遍历table_head字典中的每一项，使用__set_table_head_attribute方法设置表头的各个属性。
        """
        for k, v in table_head.items():
            self.__set_table_head_attribute(k, v)

    def get_table_head(self):
        """
        获取表头信息。

        返回:
        表头信息。
        """
        return self.__table_head

    def df_to_dict(self):
        """
        将DataFrame转换为字典格式。

        返回:
        dict, 数据框转换后的字典，以索引为键。
        """
        return self.__df.to_dict(orient='index')

    @staticmethod
    def split_ip_mask(ip_or_mask):
        """
        分割IP和子网掩码。

        参数:
        ip_or_mask: str, 格式为IP/掩码的字符串。

        返回:
        tuple, 包含IP和掩码的元组。

        异常:
        ValueError, 如果输入的格式不正确。
        """
        if '/' in ip_or_mask:
            ip = ip_or_mask.split('/')[0]
            mask = ip_or_mask.split('/')[1]
            return ip, mask
        else:
            raise ValueError('ip_or_mask格式错误')

    @staticmethod
    def split_ci_name(ci_name):
        """
        分割CI名称。

        参数:
        ci_name: str, 以逗号分隔的CI名称字符串。

        返回:
        tuple, 包含两个CI名称的元组。

        异常:
        ValueError, 如果输入的字符串不包含逗号。
        """
        if ',' not in ci_name:
            raise ValueError(f"ci_name格式错误: {ci_name}")
        ci1, ci2 = ci_name.split(',')
        logging.debug(f"分隔Ci_name：ci1: {ci1}, ci2: {ci2}")
        return ci1, ci2

    @staticmethod
    def generate_bfd_name(device_info: dict) -> str:
        """
        生成BFD名称。

        参数:
            device_info (dict): 设备信息字典。

        返回:
            str: 生成的BFD名称。
        """
        bfd_name = f'{device_info.get("关联服务/网元", "")}_{device_info.get("NQA/BFD探测IP（目的IP）", "")}'
        logging.debug(f"生成BFD名称：{bfd_name}")
        return bfd_name

    @staticmethod
    def __update_dev_int_info(dev_info: Dict[str, List[Any]], dev_key: str,
                              field_mapping: Dict[str, str], cls, **kwargs):
        """
        更新设备接口信息。

        参数:
        dev_info: dict, 存储设备信息的字典。
        dev_key: str, 设备键。
        field_mapping: dict, 字段映射关系。
        cls: 设备接口信息的类。
        **kwargs: 其他关键字参数，用于创建设备接口实例。

        异常:
        ValueError, 如果设备键已存在且不是列表形式。
        """
        if dev_key not in dev_info:
            dev_info[dev_key] = []
        elif not isinstance(dev_info[dev_key], list):
            raise ValueError(f"Key '{dev_key}' already exists and is not a list.")

        mapped_kwargs = {field_mapping.get(k, k): v for k, v in kwargs.items()}

        int_value = cls(**mapped_kwargs)
        dev_info[dev_key].append(int_value)

    def process_device_info(self, table_head_mapping: Dict[str, List[str]], field_mapping: Dict[str, str], cls,
                            device_dict: dict, ) -> DevicesConfigDict[str, List[Any]]:
        """
        处理设备信息。

        参数:
        table_head_mapping: dict, 表头映射关系。
        field_mapping: dict, 字段映射关系。
        cls: 设备接口信息的类。
        device_dict: dict, 设备信息字典。

        返回:
        DevicesConfigDict, 处理后的设备配置信息。
        """
        dev_int_info = DevicesConfigDict()
        for _, v in device_dict.items():
            for dev_key, fields in table_head_mapping.items():
                key = v[getattr(self.get_table_head(), dev_key)]
                logging.debug(f"设备CI_NAME是 {key}")
                field_values = {field: v[getattr(self.get_table_head(), field)] for field in fields}
                logging.debug(f"字段值是 {field_values}")
                self.__update_dev_int_info(dev_int_info, key, field_mapping, cls, **field_values)
        return dev_int_info

    @staticmethod
    def get_description(v, ci_name, int_name):
        """
        获取描述信息。

        参数:
        v: 设备信息字典的值。
        ci_name: CI名称。
        int_name: 接口名称。

        返回:
        str, 组合后的描述信息。
        """
        remote_ci_name = v[ci_name]
        remote_phy = v[int_name]
        return f'{remote_ci_name}_{remote_phy}'

    @staticmethod
    def get_ci_name(v):
        """
        获取CI名称。

        参数:
        v: 设备信息字典的值。

        返回:
        str, 组合后的CI名称。
        """
        dev_name = v['设备名称'][:-2]
        ip = v['BMC IP']
        return f'{dev_name}{ip}'

    @property
    def get_df(self):
        """
        获取DataFrame。

        返回:
        pandas.DataFrame, 设备信息的DataFrame。
        """
        return self.__df

    def get_snmp(self) -> DevicesConfigDict:
        """
        获取SNMP配置信息。


        返回:
        DevicesConfigDict, SNMP配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_l2_intf_info(self) -> DevicesConfigDict:
        """
        获取二层接口信息。

        返回:
        DevicesConfigDict, 二层接口配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_l3_intf_info(self) -> DevicesConfigDict:
        """
        获取三层接口信息。

        返回:
        DevicesConfigDict, 三层接口配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_net_downlink_interface(self) -> DevicesConfigDict:
        """
        获取网络下联接口信息。

        返回:
        DevicesConfigDict, 网络下联接口配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_m_lag(self) -> DevicesConfigDict:
        """
        获取M-LAG配置信息。

        返回:
        DevicesConfigDict, M-LAG配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_netconf(self) -> DevicesConfigDict:
        """
        获取NetConf配置信息。

        返回:
        DevicesConfigDict, NetConf配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_lookback(self) -> DevicesConfigDict:
        """
        获取Loopback接口信息。

        返回:
        DevicesConfigDict, Loopback接口配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_vrf(self) -> DevicesConfigDict:
        """
        获取VRF配置信息。

        返回:
        DevicesConfigDict, VRF配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_gw(self) -> DevicesConfigDict:
        """
        获取网关信息。

        返回:
        DevicesConfigDict, 网关配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_basic(self) -> DevicesConfigDict[str, List[DeviceBasicsConfig]]:
        """
        获取基本配置信息。
        返回:
        DevicesConfigDict, 基本配置信息。

        异常:
        NotImplementedError, 如果子类未实现此方法。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_static_route(self) -> DevicesConfigDict:
        """
        获取静态路由配置。

        此方法应该由具体的子类实现，用于获取设备的静态路由配置。

        返回:
            DevicesConfigDict: 包含设备静态路由配置的字典。

        异常:
            NotImplementedError: 如果子类未实现此方法，则会抛出此异常。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")

    def get_global_vlan(self) -> DevicesConfigDict[str, List[GlobalVlan]]:
        """
        获取全局VLAN配置。

        此方法应该由具体的子类实现，用于获取设备的全局VLAN配置。

        返回:
            DevicesConfigDict[str, List[GlobalVlan]]: 包含设备全局VLAN配置的字典，键为VLAN名称，值为GlobalVlan对象列表。

        异常:
            NotImplementedError: 如果子类未实现此方法，则会抛出此异常。
        """
        raise NotImplementedError(f"{self.__class__.__name__} should implement this method.")


# 定义一个泛型变量T，它绑定到NetDevBase类或其子类
T = TypeVar('T', bound=NetDevBase)


class NetDevL2IntfInfoConfig(NetDevBase):
    add_field = {'local_description': 'local_description', 'remote_description': 'remote_description'}

    def get_l2_intf_info(self) -> DevicesConfigDict[str, List[DeviceInterfaceConfig]]:
        """
        获取二层接口信息。

        返回:
            DevicesConfigDict[str, List[DeviceInterfaceConfig]]: 包含所有处理过的设备接口信息的字典。
        """

        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        processed_devices = self.__process_devices(devices)
        table_head_mapping = map.get_l2_intf_field_group_map()
        field_mapping = map.get_l2_intf_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DeviceInterfaceConfig, processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        处理设备信息，添加本地和远端的描述字段。

        参数:
            devices (dict): 原始设备信息字典。

        返回:
            dict: 处理后的设备信息字典，包含新增的描述字段。
        """
        for device_id, device_info in devices.items():
            device_info['local_description'] = self.get_description(device_info, '对端CI NAME', '对端物理端口')
            device_info['remote_description'] = self.get_description(device_info, '本端CI NAME', '本端物理端口')
            devices[device_id] = device_info
        return devices


class NetDevL3IntfInfo(NetDevBase):
    add_field = {'local_mask': 'local_mask', 'remote_mask': 'remote_mask', 'vid': 'vid'}

    def get_l3_intf_info(self) -> DevicesConfigDict[str, List[DeviceL3IntConfig]]:
        """
        获取三层接口信息。

        Returns:
            DevicesConfigDict[str, List[DeviceL3IntConfig]]: 包含所有设备三层接口配置信息的字典。
        """
        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        processed_devices = self.__process_devices(devices)
        table_head_mapping = map.get_l3_intf_field_group_map()
        field_mapping = map.get_l3_intf_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DeviceL3IntConfig, processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        处理设备信息，分离IP和子网掩码。

        Parameters:
            devices (dict): 待处理的设备信息字典。

        Returns:
            dict: 处理后的设备信息字典，包含分离后的IP和掩码信息。
        """
        pattern = r'\.\d+'
        for device_id, device_info in devices.items():
            local_ip, local_mask = self.split_ip_mask(device_info['本端IP'])
            device_info['本端IP'] = local_ip
            device_info['local_mask'] = local_mask
            remote_ip, remote_mask = self.split_ip_mask(device_info['对端IP'])
            device_info['对端IP'] = remote_ip
            device_info['remote_mask'] = remote_mask
            match = re.search(pattern, device_info['本端逻辑端口'])
            if match:
                vid = int(match.group().split('.')[1]) + 99
                device_info['vid'] = vid
            else:
                device_info['vid'] = None
            devices[device_id] = device_info
        return devices


class NetDevDownlinkInterface(NetDevBase):
    add_field = {'description': 'description', }

    def get_net_downlink_interface(self) -> DevicesConfigDict[str, List[DeviceInterfaceConfig]]:
        """
        获取网络设备的下行链路接口配置信息。

        返回:
            设备配置字典，键为设备标识，值为设备接口配置列表。

        方法工作流程:
            1. 设置表格头部为 add_field 定义的字段。
            2. 从 DataFrame 中提取设备信息。
            3. 处理提取的设备信息。
            4. 根据预定义的映射关系，进一步加工设备信息。
            5. 返回加工后的设备接口配置信息。
        """
        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        processed_devices = self.__process_devices(devices)
        table_head_mapping = map.get_downlink_int_table_map()
        field_mapping = map.get_downlink_int_map()
        return self.process_device_info(table_head_mapping, field_mapping, DeviceInterfaceConfig,
                                        device_dict=processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        处理设备信息，对特定字段进行转换。

        参数:
            devices: 待处理的设备信息字典。

        返回:
            处理后的设备信息字典。

        该方法对设备信息中的描述、是否 force-up 以及 lacp 超时模式等字段进行解析和转换。
        """
        for device_id, device_info in devices.items():
            device_info['description'] = self.get_description(device_info, '对端CI NAME', '对端物理端口')
            # 将 force-up 字段从字符串转换为布尔值
            force_up = device_info['是否force-up']
            if force_up == '是':
                device_info['是否force-up'] = True
            else:
                device_info['是否force-up'] = False
            # 将 lacp timeout mode 字段从 'slow'/'fast' 转换为布尔值

            lacp_timeout_mode = device_info['lacp timeout mode']
            if lacp_timeout_mode == 'slow':
                device_info['lacp timeout mode'] = True
            else:
                device_info['lacp timeout mode'] = False

            devices[device_id] = device_info
        return devices


class NetDevMlag(NetDevBase):
    """
    网络设备MLAG（多链路聚合组）信息获取类。
    继承自NetDevBase基类，提供特定于MLAG配置的设备信息查询功能。
    """

    def get_m_lag(self) -> DevicesConfigDict[str, List[DevMLAGConfig]]:
        """
        获取设备的MLAG配置信息。

        将设备状态数据框转换为字典格式，然后根据MLAG字段分组和别名映射，
        处理并返回每个设备的MLAG配置信息。

        Returns:
            DevicesConfigDict[str, List[DevMLAGConfig]]: 包含所有设备MLAG配置的字典。
        """
        devices = self.df_to_dict()
        table_head_mapping = map.get_m_lag_field_group_map()
        field_mapping = map.get_m_lag_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DevMLAGConfig, devices)


class NetDevConf(NetDevBase):
    """
    网络设备运行配置获取类。
    继承自NetDevBase基类，提供特定于设备运行配置的查询功能。
    """

    def get_netconf(self):
        """
        获取设备的运行配置信息。

        将设备状态数据框转换为字典格式，然后根据NETCONF字段分组和别名映射，
        处理并返回每个设备的运行配置信息。

        Returns:
            DevicesConfigDict[str, List[DevNetConf]]: 包含所有设备运行配置的字典。
        """
        devices = self.df_to_dict()
        table_head_mapping = map.get_netconf_table_map()
        field_mapping = map.get_netconf_map()
        return self.process_device_info(table_head_mapping, field_mapping, DevNetConf, devices)


class NetDveLookback(NetDevBase):
    """
    网络设备Loopback信息获取类。
    继承自NetDevBase基类，提供特定于Loopback配置的设备信息查询功能。
    """

    def get_lookback(self) -> DevicesConfigDict[str, List[LookbackConfig]]:
        """
        获取设备的Loopback配置信息。

        将设备状态数据框转换为字典格式，然后根据Loopback字段分组和别名映射，
        处理并返回每个设备的Loopback配置信息。

        Returns:
            DevicesConfigDict[str, List[LookbackConfig]]: 包含所有设备Loopback配置的字典。
        """
        devices = self.df_to_dict()
        table_head_mapping = map.get_lookback_field_group_map()
        field_mapping = map.get_lookback_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, LookbackConfig, devices)


class NetDevVrf(NetDevBase):
    """
    网络设备VRF（虚拟路由转发）信息获取类。
    继承自NetDevBase基类，提供特定于VRF配置的设备信息查询功能。
    """

    def get_vrf(self) -> DevicesConfigDict[str, List[VrfConfig]]:
        """
        获取设备的VRF配置信息。

        将设备状态数据框转换为字典格式，然后根据VRF字段分组和别名映射，
        处理并返回每个设备的VRF配置信息。

        Returns:
            DevicesConfigDict[str, List[VrfConfig]]: 包含所有设备VRF配置的字典。
        """
        devices = self.df_to_dict()
        table_head_mapping = map.get_vrf_field_group_map()
        field_mapping = map.get_vrf_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, VrfConfig, devices)


class NetDevGW(NetDevBase):
    add_field = {'ci_name': 'ci_name', 'gw_mask': 'gw_mask', 'vrrp_vrid': 'vrrp_vrid'}

    def get_gw(self) -> DevicesConfigDict[str, List[DeviceGWConfig]]:
        """
        获取网关设备配置信息。

        返回:
            设备配置字典，其中包含网关相关信息。

        """
        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        processed_devices = self.__process_devices(devices)
        table_head_mapping = map.get_gw_field_group_map()
        field_mapping = map.get_gw_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DeviceGWConfig, processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        处理设备信息，为每个设备添加网关掩码和网关设备CI名称信息。

        参数:
            devices: 包含设备信息的字典。

        返回:
            包含处理后设备信息的字典。
        """
        # 创建两个计数器，分别用于分配ci1和ci2的键值
        ci1_key = itertools.count(start=0, step=2)
        ci2_key = itertools.count(start=1, step=2)
        new_devices = {}
        vrrp_vrid = 0
        for device_id, device_info in devices.items():
            # 检查设备是否有网关信息
            if device_info['网关'] != '-' and device_info['网关设备CI NAME'] != '-':
                # 分离IP和掩码
                _, mask = self.split_ip_mask(device_info['网段/掩码'])
                # 添加掩码信息到设备信息中
                device_info['gw_mask'] = mask
                local_ip = device_info['local ip']
                if local_ip != '-':
                    local_ip1, local_ip2 = local_ip.split(',')
                else:
                    local_ip1, local_ip2 = '-', '-'
                if device_info['网关类型'] == 'vrrp':
                    vrrp_vrid += 1
                    device_info['vrrp_vrid'] = vrrp_vrid
                else:
                    device_info['vrrp_vrid'] = None
                ci1, ci2 = self.split_ci_name(device_info['网关设备CI NAME'])
                # 对两个CI名称分别处理
                for ci, ci_key, local_ip in zip([ci1, ci2], [ci1_key, ci2_key], [local_ip1, local_ip2]):
                    # 复制设备信息以保留原始信息
                    ci_dict = device_info.copy()
                    # 添加CI名称信息
                    ci_dict['ci_name'] = ci
                    ci_dict['local ip'] = local_ip
                    # 将处理后的设备信息添加到新字典中
                    new_devices[next(ci_key)] = ci_dict
        return new_devices


class NetDevBasic(NetDevBase):
    add_field = {'ci_name': 'ci_name', 'manage_int': 'manage_int'}

    def get_basic(self) -> DevicesConfigDict[str, List[DeviceBasicsConfig]]:
        """
        获取基本设备信息。
        :return: 返回处理后的设备配置信息字典。
        """
        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        processed_devices = self.__process_devices(devices)
        table_head_mapping = map.get_basic_field_group_map()
        field_mapping = map.get_basic_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DeviceBasicsConfig, processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        处理设备信息，为每个设备添加管理接口和VRF信息。

        :param devices: 设备信息字典。
        :return: 返回处理后的设备信息字典。
        """
        for device_id, device_info in devices.items():
            # 获取设备的CI名称
            device_info['ci_name'] = self.get_ci_name(v=device_info)
        return devices


class NetDevSNMP(NetDevBase):
    add_field = {'ci_name': 'ci_name', 'target_host': 'target_host', 'udp_port': 'udp_port'}

    def get_snmp(self) -> DevicesConfigDict[str, List[DeviceSNMPConfig]]:
        """
        获取SNMP设备配置信息。

        本方法用于从目标主机获取SNMP设备的配置信息，并将其转换为指定格式返回。

        :return: 返回一个字典，包含设备的SNMP配置信息。
        """
        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        processed_devices = self.__process_devices(devices)
        table_head_mapping = map.get_snmp_field_group_map()
        field_mapping = map.get_snmp_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DeviceSNMPConfig, processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        处理设备信息，添加或更新ci_name, target_host, udp_port字段。

        本方法遍历设备信息字典，为每个设备添加或更新指定字段。

        :param devices: 设备信息字典。
        :return: 更新后的设备信息字典。
        """
        # 遍历设备信息，更新每个设备的字段
        for k, v in devices.items():
            v['ci_name'] = self.get_ci_name(v=v)
        return devices


class NetDevStaticRoute(NetDevBase):
    add_field = {'destination_mask': 'destination_mask', 'bfd_name': 'bfd_name', 'destination_net': 'destination_net'}
    # 用于记录错误的设备列表
    error_devices = []

    def get_static_route(self) -> DevicesConfigDict[str, List[DevStaticRouteConfig]]:
        """
        获取静态路由配置信息。

        返回:
            DevicesConfigDict[str, List[DevStaticRouteConfig]]: 包含设备静态路由配置的字典。
        """
        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        processed_devices = self.__process_devices(devices)
        table_head_mapping = map.get_static_route_field_group_map()
        field_mapping = map.get_static_route_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DevStaticRouteConfig, processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        处理设备信息，验证和转换必要的字段。

        参数:
            devices (dict): 设备信息字典。

        返回:
            dict: 处理后的设备信息字典。
        """
        # 存储需要删除的键集合
        del_key_set = set()
        # 遍历设备信息
        for device_id, device_info in devices.items():
            # 检查设备信息是否包含必要的字段
            if '下一跳地址' not in device_info or '目的网络/掩码' not in device_info:
                self.error_devices.append((device_id, "Missing required fields"))
                continue

            try:
                # 验证下一跳地址是否为有效的IP地址
                ipaddress.ip_address(device_info['下一跳地址'])
                net, mask = self.split_ip_mask(device_info['目的网络/掩码'])
                # 如果网络和掩码有效，则进行转换并计算BFD名称
                if net is not None and mask is not None:
                    device_info['destination_net'] = net
                    device_info['destination_mask'] = mask
                    device_info['bfd_name'] = self.generate_bfd_name(device_info)
                    device_info['关联'] = device_info['关联'] == 'BFD'
                else:
                    raise ValueError("Invalid network or mask")
            except ValueError as e:
                # 如果设备信息不合法，记录错误信息并标记删除
                self.error_devices.append((device_id, str(e)))
                del_key_set.add(device_id)
                continue
        # 删除标记的设备信息
        for i in del_key_set:
            del devices[i]
        return devices


class NetDevBFD(NetDevBase):
    BFD_ASSOCIATION = 'BFD'
    add_field = {'bfd_name': 'bfd_name'}

    def get_bfd(self) -> DevicesConfigDict[str, List[DevBFDConfig]]:
        """
        根据源IP获取BFD设备配置信息。

        :return: 返回包含BFD设备配置的字典。
        """
        self.set_table_head(self.add_field)
        devices = self.df_to_dict()
        try:
            processed_devices = self.__process_devices(devices)
        except Exception as e:
            print(f"Error processing devices: {e}")
            return DevicesConfigDict()
        table_head_mapping = map.get_bfd_field_group_map()
        field_mapping = map.get_bfd_alias_map()
        return self.process_device_info(table_head_mapping, field_mapping, DevBFDConfig, processed_devices)

    def __process_devices(self, devices: dict) -> dict:
        """
        筛选并处理与BFD关联的设备信息。

        :param devices: 待处理的设备信息字典。
        :return: 返回与BFD关联的设备信息字典。
        """
        bfd_devices = {}
        for device_id, device_info in devices.items():
            if '关联' in device_info and device_info['关联'] == self.BFD_ASSOCIATION:
                try:
                    bfd_name = self.generate_bfd_name(device_info)
                except Exception as e:
                    print(f"Error generating bfd_name for device {device_id}: {e}")
                    continue
                device_info['bfd_name'] = bfd_name
                bfd_devices[device_id] = device_info
        return bfd_devices


class NetDevGlobalVlan(NetDevBase):

    @staticmethod
    def simplify_and_chunk(lists):
        # 合并所有列表到一个集合中去重，并将所有元素转换为整数
        unique_numbers = set()
        for sublist in lists:
            for item in sublist:
                # 确保 item 是整数，如果是字符串则转换为整数
                if isinstance(item, str):
                    try:
                        item = int(item)
                    except ValueError:
                        continue
                unique_numbers.add(item)

        # 转换为排序列表
        sorted_numbers = sorted(unique_numbers)

        # 将连续数字简化为范围表示
        def simplify_numbers(nums):
            if not nums:
                return []

            ranges = []
            start = nums[0]
            end = nums[0]

            for num in nums[1:]:
                if num == end + 1:
                    end = num
                else:
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(f"{start} to {end}")
                    start = num
                    end = num

            # Add the last range
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start} to {end}")

            return ranges

        simplified_numbers = simplify_numbers(sorted_numbers)

        # 分割简化后的数字，每个子列表最多包含 15 个项目
        chunked_lists = []
        chunk = []
        for item in simplified_numbers:
            chunk.append(item)
            if len(chunk) == 15:
                chunked_lists.append(chunk)
                chunk = []
        if chunk:
            chunk = ','.join(chunk)
            result_str = chunk.replace(',', ' ')
            chunked_lists.append(result_str)
        return chunked_lists

    def get_global_vlan(self) -> List[GlobalVlan]:
        devices = self.df_to_dict()
        global_vlan_list = []
        batch_vlan = []
        for _, v in devices.items():
            vlan_id = v['VLAN ID']
            if vlan_id != '-':
                vlan_id = vlan_id.split('-')
                if len(vlan_id) > 1:
                    vlan_id = list(range(int(vlan_id[0]), int(vlan_id[-1]) + 1))
                description = v['网络平面名称']
                global_vlan_list.append(GlobalVlan(vlan_id=vlan_id, description=description))
                batch_vlan.append(vlan_id)
        batch_vlan = self.simplify_and_chunk(batch_vlan)
        for i in global_vlan_list:
            i.batch_vlan = batch_vlan
        return global_vlan_list


# 定义一个映射关系，将不同的表头类型映射到对应的实例化方法
HEAD_MAP: Dict[str, Callable[[pd.DataFrame, object], T]] = {
    'NetDevL2IntTableHead': NetDevL2IntfInfoConfig,
    'NetDevDownlinkIntfTableHead': NetDevDownlinkInterface,
    'NetDevMLAGTableHead': NetDevMlag,
    'NetDevNetConfProTableHead': NetDevConf,
    'NetDevL3IntTableHead': NetDevL3IntfInfo,
    'NetLookBackupTableHead': NetDveLookback,
    'NetVrfTableHead': NetDevVrf,
    'NetDevGWTableHead': NetDevGW,
    'NetDevBasicTableHead': NetDevBasic,
    'NetDevSNMPTableHead': NetDevSNMP,
    'NetDevStaticRouteTableHead': NetDevStaticRoute,
    'NetDevBFDTableHead': NetDevBFD,
    'NetDevGlobalVlanTableHead': NetDevGlobalVlan
}


def create_instance(df: pd.DataFrame, table_head: object) -> T:
    """
    根据提供的DataFrame和表头对象创建并返回一个NetDevBase子类的实例。

    参数:
    df: pd.DataFrame - 用于实例化的数据框架。
    table_head: object - 表头对象，用于确定实例的具体类型。

    返回:
    T - 一个NetDevBase子类的实例。

    抛出:
    ValueError - 如果提供的DataFrame无效或找不到对应的实例化方法。
    """
    # 检查提供的DataFrame是否有效
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("Invalid DataFrame provided.")

    # 获取表头对象的类名
    table_head_class_name = table_head.__class__.__name__

    # 如果表头类名存在于映射中，则调用相应的实例化方法
    if table_head_class_name in HEAD_MAP:
        return HEAD_MAP[table_head_class_name](df, table_head)
    else:
        # 如果找不到对应的实例化方法，抛出异常
        raise ValueError(f"No creation method found for table head type: {table_head_class_name}")
