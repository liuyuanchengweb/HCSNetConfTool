import ipaddress
import re
import logging
from typing import Dict, List, Any
from src.controller.table_head_args import (create_global_vlan,
                                            create_basic,
                                            create_snmp,
                                            create_mlag,
                                            create_vrf,
                                            create_look_back,
                                            create_netconf, create_static_route, create_bfd, create_gw,
                                            create_ndi_l3_int, create_ndi_l2_int, create_downlink_intf)


class DeviceConfData:
    """
    设备配置数据类，用于生成和管理设备的配置数据。
    """
    # 初始化设备列表
    device_list = []

    def __init__(self, ci_name,
                 manage_gw_ip: str,
                 manage_vrf_name: str,
                 option_manage_mode: bool,
                 sftp: bool,
                 target_host: str,
                 target_host_host_name: str,
                 udp_port: int,
                 option_vrf: bool,
                 option_snmp: bool,
                 option_mlag: bool,
                 option_batch_vlan: bool,
                 option_global_vlan: bool,
                 option_gw: bool,
                 option_l3_vlan: bool,
                 option_l3_phy: bool,
                 option_ndi_l2: bool,
                 option_server_int: bool,
                 option_netconf: bool,
                 option_look_back: bool,
                 option_static_route: bool,
                 option_bfd: bool, ):
        """
        初始化方法，根据不同的配置选项生成相应的设备配置数据。

        参数:
        - ci_name: 设备的CI名称,管理需要生成配置的设备列表
        - manage_gw_ip: 管理网关IP地址
        - manage_vrf_name: 管理VRF名称
        - option_manage_mode: 管理模式选项
        - sftp: SFTP配置选项
        - target_host: 目标主机地址
        - target_host_host_name: 目标主机主机名
        - udp_port: UDP端口号
        - option_vrf: VRF配置选项
        - option_snmp: SNMP配置选项
        - option_mlag: MLag配置选项
        - option_batch_vlan: 批量VLAN配置选项
        - option_global_vlan: 全局VLAN配置选项
        - option_gw: 网关配置选项
        - option_l3_vlan: 三层VLAN配置选项
        - option_l3_phy: 三层物理接口配置选项
        - option_ndi_l2: NDI二层接口配置选项
        - option_server_int: 服务器接口配置选项
        - option_netconf: Netconf配置选项
        - option_look_back: 回视配置选项
        - option_static_route: 静态路由配置选项
        - option_bfd: BFD配置选项
        """
        # 设备CI名称
        self.ci_name = ci_name
        # 各种配置选项
        self.option_vrf = option_vrf
        self.option_snmp = option_snmp
        self.option_mlag = option_mlag
        self.option_batch_vlan = option_batch_vlan
        self.option_global_vlan = option_global_vlan
        self.option_gw = option_gw
        self.option_l3_vlan = option_l3_vlan
        self.option_l3_phy = option_l3_phy
        self.option_ndi_l2 = option_ndi_l2
        self.option_server_int = option_server_int
        self.option_netconf = option_netconf
        self.option_look_back = option_look_back
        self.option_static_route = option_static_route
        self.option_bfd = option_bfd
        # 获取并存储基本配置数据
        self.basic = self.get_basic_data(manage_gw_ip, manage_vrf_name, option_manage_mode, sftp)
        # 获取并存储VRF配置数据
        self.vrf_data = self.get_vrf_data()
        # 获取并存储SNMP配置数据
        self.snmp = self.get_snmp_data(target_host, target_host_host_name, udp_port)
        # 获取并存储MLag配置数据
        self.mlag = self.get_mlag_data()
        # 获取并存储全局VLAN配置数据
        self.global_vlan = self.get_global_vlan()
        # 获取并存储网关配置数据
        self.gw = self.get_gw_data()
        # 获取并存储三层VLAN接口配置数据
        self.l3_vlan = self.get_l3_vlanif()
        # 获取并存储三层物理接口配置数据
        self.l3_phy = self.get_l3_phy()
        # 获取并存储NDI二层接口配置数据
        self.ndi_l2_data = self.get_ndi_l2_int_data()
        # 获取并存储服务器接口配置数据
        self.server_data = self.get_server_int_data()
        # 获取并存储Netconf配置数据
        self.netconf = self.get_netconf_data()
        # 获取并存储回视配置数据
        self.look_back = self.get_look_back_data()
        # 获取并存储静态路由配置数据
        self.static_route = self.get_static_route_data()
        # 获取并存储BFD配置数据
        self.bfd_data = self.get_bfd_data()

    @staticmethod
    def ipv4_to_hex(ip):
        """
        将IPv4地址转换为十六进制字符串。

        参数:
        - ip: 待转换的IPv4地址

        返回值:
        转换后的十六进制字符串。
        """
        logging.debug(f"开始转换IPv4地址: {ip}")
        ip_int = int(ipaddress.IPv4Address(ip))
        hex_str = format(ip_int, '08x')
        logging.debug(f"转换完成。十六进制字符串: host_name{hex_str}")
        return f'host_name{hex_str}'

    @staticmethod
    def if_manage_mode(value):
        """
        检查管理模式值是否符合特定模式。

        参数:
        - value: 待检查的管理模式值

        返回值:
        如果管理模式值符合特定模式，返回True；否则返回False。
        """
        logging.debug(f"开始检查管理模式值: {value}")
        pattern = '^vlan.*'
        match = re.match(pattern, value)
        result = bool(match)
        logging.debug(f"管理模式值检查完成。结果: {result}")
        return result

    @staticmethod
    def __match_usg_or_fw(text):
        """
        检查文本中是否包含USG或fw。

        参数:
        text (str): 待匹配的文本。

        返回:
        bool: 如果文本中包含USG或fw，则返回True，否则返回False。
        """
        logging.debug(f"开始检查文本: {text}")
        pattern = re.compile(r'.*(USG|fw).*')
        result = bool(pattern.match(text))
        logging.debug(f"文本检查完成。结果: {result}")
        return result

    @staticmethod
    def __set_bfd_source_ip(bfd, gw):
        """
        设置BFD会话的源IP地址。

        根据网关（gw）数据设置BFD（bfd）会话的源IP地址。

        参数:
        bfd (list): 包含BFD会话数据的列表。
        gw (list): 包含网关数据的列表。
        """
        logging.debug("开始设置BFD会话的源IP地址")
        for bfd_data in bfd:
            bfd_vlan_id = bfd_data.interface.split()
            remove_spaces = ''.join(bfd_vlan_id)
            bfd_data.interface = remove_spaces
            for gw_data in gw:
                if int(bfd_vlan_id[1]) == int(gw_data.vlan_id):
                    bfd_data.source_ip = gw_data.gw_ip
                    logging.debug(f"为BFD会话 {bfd_data.bfd_name} 设置源IP地址为 {gw_data.gw_ip}")
        logging.debug("完成设置BFD会话的源IP地址")

    @staticmethod
    def __process_device_data(data: dict) -> dict:
        """
        处理设备数据，生成MAC地址映射。

        为每个设备的接口生成MAC地址，并将它们存储在一个映射中。只处理以“Vlanif”开头的物理接口。
        为这些接口分配唯一的MAC地址，并将这些MAC地址添加到数据字典中。

        参数:
        data (Dict[str, List[Dict[str, Any]]]): 包含设备及其接口数据的字典。

        返回:
        Dict[str, List[Dict[str, Any]]]: 更新后的数据字典，包含设备接口的MAC地址。
        """

        def generate_mac(index: int) -> str:
            """
            生成MAC地址。

            根据给定的索引生成一个格式化的MAC地址。

            参数:
            index (int): 用于生成MAC地址的索引。

            返回:
            str: 生成的MAC地址。
            """
            return f"0000-5e00-01{index:02d}"

        logging.debug("开始处理设备数据")
        mac_counter = 1
        ip_mac_mapping = {}

        for device, interfaces in data.items():
            logging.debug(f"处理设备 {device} 的接口数据")
            for interface in interfaces:
                if interface['phy'].startswith('Vlanif'):
                    ip = interface.get('ip')
                    if ip and ip not in ip_mac_mapping:
                        ip_mac_mapping[ip] = generate_mac(mac_counter)
                        mac_counter += 1
                    interface['mac_add'] = ip_mac_mapping.get(ip)
                    interface['option_mac_add'] = True
                    logging.debug(f"为接口 {interface['phy']} 分配MAC地址 {interface['mac_add']}")
                else:
                    interface['mac_add'] = None
                    logging.debug(f"接口 {interface['phy']} 不是Vlanif类型，不分配MAC地址")
        logging.debug("完成处理设备数据")
        return data

    @staticmethod
    def get_global_vlan():
        """
        获取全局VLAN设置

        该方法通过创建全局VLAN来获取当前的VLAN设置。全局VLAN是指在网络中用于提供跨不同子网通信的VLAN设置。
        通过返回这些设置，我们可以确保网络设备之间的通信是按照预定的全局VLAN配置进行的。

        :return: vlan_set 创建的全局VLAN设置
        """
        logging.debug("开始获取全局VLAN设置")
        vlan_set = create_global_vlan()
        logging.debug("完成获取全局VLAN设置")
        return vlan_set

    @staticmethod
    def get_dev_set():
        """
        获取设备集合的基本信息。

        通过调用create_basic()方法获取设备的基本信息，并将其转换为字典格式返回。

        Returns:
            dev_set: 设备信息的字典格式。
        """
        logging.debug("开始获取设备集合的基本信息")
        dev_set = create_basic().to_dict()
        logging.debug("完成获取设备集合的基本信息")
        return dev_set

    @classmethod
    def get_device_data(cls):
        """
        获取设备数据列表。

        从设备集合中筛选出不匹配特定条件（由__match_usg_or_fw方法定义）的设备名称，并将其添加到设备列表中。

        Returns:
            cls.device_list: 更新后的设备列表。
        """
        logging.debug("开始获取设备数据列表")
        device_data = cls.get_dev_set()
        for dev_name, _ in device_data.items():
            if not cls.__match_usg_or_fw(dev_name):
                cls.device_list.append(dev_name)
                logging.debug(f"添加设备 {dev_name} 到设备列表")
        logging.debug("完成获取设备数据列表")
        return cls.device_list

    def get_basic_data(self, manage_gw_ip, manage_vrf_name, option_manage_mode, sftp):
        """
        获取基本配置数据。

        根据提供的参数，准备和格式化基本配置数据。

        参数:
        - manage_gw_ip: 管理网关IP地址，用于确定是否启用管理网关选项。
        - manage_vrf_name: 管理VRF名称，用于确定是否启用管理VRF选项。
        - option_manage_mode: 管理模式选项，指定管理的具体模式。
        - sftp: SFTP配置选项，用于启用或配置SFTP相关设置。

        返回:
        返回格式化后的基本配置字典。
        """
        logging.debug("开始获取基本配置数据")
        basic_datas = create_basic().to_dict()
        basic_config = basic_datas[self.ci_name]
        if manage_gw_ip:
            basic_config[0]['option_manage_gw'] = True
        if manage_vrf_name:
            basic_config[0]['option_manage_vrf'] = True
        basic_config[0]['option_manage_mode'] = option_manage_mode
        basic_config[0]['sftp'] = sftp

        logging.debug("完成获取基本配置数据")
        return basic_config[0]

    def get_snmp_data(self, target_host, target_host_host_name, udp_port):
        """
        获取SNMP配置数据。

        根据提供的目标主机信息，准备和格式化SNMP配置数据。

        参数:
        - target_host: 目标主机地址，用于确定是否启用目标选项。
        - target_host_host_name: 目标主机名称，用于配置目标主机的具体名称。
        - udp_port: UDP端口号，用于配置SNMP的通信端口。

        返回:
        返回格式化后的SNMP配置字典，如果实例名不在SNMP数据中，则返回None。
        """
        logging.debug("开始获取SNMP配置数据")
        snmp_datas = create_snmp().to_dict()
        try:
            snmp_config = snmp_datas[self.ci_name]
            if target_host:
                snmp_config[0]['option_target'] = True
                snmp_config[0]['target_host_host_name'] = target_host_host_name
                snmp_config[0]['udp_port'] = udp_port
            logging.debug("完成获取SNMP配置数据")
            return snmp_config[0]
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有SNMP数据")
            self.option_snmp = False

    def get_mlag_data(self):
        """
        获取MLAG配置数据。

        返回MLAG配置数据，如果实例名不在MLAG数据中，则返回None。

        返回:
        返回格式化后的MLAG配置字典。
        """
        logging.debug("开始获取MLAG配置数据")
        mlag_datas = create_mlag().to_dict()
        try:
            mlag_config = mlag_datas[self.ci_name]
            logging.debug("完成获取MLAG配置数据")
            return mlag_config[0]
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有MLAG数据")
            self.option_mlag = False

    def get_vrf_data(self):
        """
        获取VRF配置数据。

        返回VRF配置数据，如果实例名不在VRF数据中，则返回None。

        返回:
        返回格式化后的VRF配置字典。
        """
        logging.debug("开始获取VRF配置数据")
        vrf_datas = create_vrf().to_dict()
        try:
            vrf_config = vrf_datas[self.ci_name]
            logging.debug("成功获取VRF配置数据")
            return vrf_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有VRF数据")
            self.option_vrf = False

    def get_look_back_data(self):
        """
        获取Loopback配置数据。

        返回Loopback配置数据，如果实例名不在Loopback数据中，则返回None。

        返回:
        返回格式化后的Loopback配置字典。
        """
        logging.debug("开始获取Loopback配置数据")
        look_back_datas = create_look_back().to_dict()
        try:
            look_back_config = look_back_datas[self.ci_name]
            logging.debug("成功获取Loopback配置数据")
            return look_back_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有Loopback数据")
            self.option_look_back = False

    def get_netconf_data(self):
        """
        获取Netconf配置数据。

        :return: 返回Netconf配置数据，如果不存在则将option_netconf设置为False。
        """
        logging.debug("开始获取Netconf配置数据")
        netconf_datas = create_netconf().to_dict()
        try:
            netconf_config = netconf_datas[self.ci_name]
            logging.debug("成功获取Netconf配置数据")
            return netconf_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有Netconf数据")
            self.option_netconf = False

    def get_gw_data(self):
        """
        获取网关数据。

        :return: 返回网关配置数据，如果不存在则将option_gw设置为False。
        """
        logging.debug("开始获取网关配置数据")
        gw_datas = create_gw()
        try:
            gw_config = gw_datas[self.ci_name]
            logging.debug("成功获取网关配置数据")
            return gw_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有网关数据")
            self.option_gw = False

    def get_static_route_data(self):
        """
        获取静态路由数据。

        :return: 返回静态路由配置数据，如果不存在则将option_static_route设置为False。
        """
        logging.debug("开始获取静态路由配置数据")
        static_route_datas = create_static_route().to_dict()
        try:
            static_route_config = static_route_datas[self.ci_name]
            logging.debug("成功获取静态路由配置数据")
            return static_route_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有静态路由数据")
            self.option_static_route = False

    def get_bfd_data(self):
        """
        获取BFD（双向转发检测）数据。

        :return: 返回BFD配置数据，如果不存在则将option_bfd设置为False。
        """
        logging.debug("开始获取BFD配置数据")
        bfd_datas = create_bfd()
        try:
            bfd_config = bfd_datas[self.ci_name]
            self.__set_bfd_source_ip(bfd_config, self.get_gw_data())
            logging.debug("成功获取BFD配置数据")
            return bfd_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有BFD数据")
            self.option_bfd = False

    def get_ndi_l3_int_data(self):
        """
        获取NDI三层接口数据。

        :return: 返回NDI三层接口配置数据，如果不存在则将option_l3_phy设置为False。
        """
        logging.debug("开始获取NDI三层接口配置数据")
        ndi_l3_int_datas = create_ndi_l3_int().to_dict()
        add_l3_mac = self.__process_device_data(ndi_l3_int_datas)
        try:
            ndi_l3_int_config = add_l3_mac[self.ci_name]
            logging.debug("成功获取NDI三层接口配置数据")
            return ndi_l3_int_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有NDI三层接口数据")
            self.option_l3_phy = False

    def get_l3_vlanif(self):
        """
        获取三层VLAN接口数据。

        :return: 返回三层VLAN接口数据列表，如果获取失败则将option_l3_vlan设置为False。
        """
        logging.debug("开始获取三层VLAN接口数据")
        l3_config = self.get_ndi_l3_int_data()
        try:
            vlan_data = [item for item in l3_config if item['phy'].startswith('Vlan')]
            logging.debug("成功获取三层VLAN接口数据")
            return vlan_data
        except TypeError:
            logging.debug(f"设备名 {self.ci_name} 中未获取到三层vlan接口信息")
            self.option_l3_vlan = False

    def get_l3_phy(self):
        """
        获取三层物理接口数据。

        :return: 返回三层物理接口数据列表，如果获取失败则将option_l3_phy设置为False。
        """
        logging.debug("开始获取三层物理接口数据")
        l3_config = self.get_ndi_l3_int_data()
        try:
            # 筛选出Vlan开头的接口
            l3_phy_data = [item for item in l3_config if not item['phy'].startswith('Vlan')]
            logging.debug("成功获取三层物理接口数据")
            return l3_phy_data
        except TypeError:
            logging.debug(f"设备名 {self.ci_name} 中未获取到三层物理接口信息")
            self.option_l3_phy = False

    def get_ndi_l2_int_data(self):
        """
        获取NDI二层接口数据。

        :return: 返回NDI二层接口配置数据，如果不存在则将option_ndi_l2设置为False。
        """
        logging.debug("开始获取NDI二层接口配置数据")
        ndi_l2_int_datas = create_ndi_l2_int().to_dict()
        try:
            ndi_l2_int_config = ndi_l2_int_datas[self.ci_name]
            logging.debug("成功获取NDI二层接口配置数据")
            return ndi_l2_int_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有NDI二层接口数据")
            self.option_ndi_l2 = False

    def get_server_int_data(self):
        """
        获取服务器接口数据。

        :return: 返回服务器接口配置数据，如果不存在则将option_server_int设置为False。
        """
        logging.debug("开始获取服务器接口配置数据")
        server_int_datas = create_downlink_intf().to_dict()
        try:
            server_int_config = server_int_datas[self.ci_name]
            logging.debug("成功获取服务器接口配置数据")
            return server_int_config
        except KeyError:
            logging.debug(f"设备名 {self.ci_name} 中没有服务器接口数据")
            self.option_server_int = False
