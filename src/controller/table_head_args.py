import logging
from src.data_processing.net_device_data_extractor import NetDeviceDataExtractor
from src.config.app_config_loader import app_config
from src.models.table_structure import (TableArg, Filter,
                                        NetDevSNMPTableHead,
                                        NetDevL2IntTableHead,
                                        NetDevDownlinkIntfTableHead, NetDevMLAGTableHead,
                                        NetDevNetConfProTableHead, NetDevLocalL2IntTableHead,
                                        NetDevRemoteL2IntTableHead,
                                        NetDevLocalL3IntTableHead, NetDevRemoteL3IntTableHead, NetDevL3IntTableHead,
                                        NetLookBackupTableHead,
                                        NetVrfTableHead, NetDevGWTableHead, NetDevBasicTableHead,
                                        NetDevStaticRouteTableHead, NetDevBFDTableHead,
                                        NetDevGlobalVlanTableHead)
from src.data_processing.device_config_collector import DeviceConfigCollector
from functools import lru_cache

DATA_DIR = app_config.data_dir


def initialize_device_config_collector():
    """
    初始化设备配置收集器。

    该函数负责初始化设备配置收集器实例，用于后续提取和处理网络设备的数据。

    Returns:
        DeviceConfigCollector: 返回一个设备配置收集器实例，用于提取设备的详细配置数据。
    """
    logging.debug("开始初始化设备配置收集器")
    # 从应用配置中获取设备清单文件路径
    lld_file = app_config.lld_file
    # 使用LLD文件初始化网络设备数据提取器
    hcs830lld = NetDeviceDataExtractor(lld_file)
    # 使用网络设备数据提取器初始化设备配置收集器
    dc = DeviceConfigCollector(net_device_data_extractor=hcs830lld)
    logging.debug("设备配置收集器初始化完成")
    return dc


@lru_cache(maxsize=128)
def create_basic():
    """
    创建基本设备信息表格。

    该函数负责创建一个包含基本设备信息的表格，包括设备名称、IP、用户名等信息。
    使用lru_cache装饰器来缓存结果，以提高重复调用的性能。

    Returns:
        Table: 返回包含基本设备信息的表格。
    """
    # 初始化基本设备信息表格的头部信息
    basic_head = NetDevBasicTableHead(
        device_name='设备名称',
        manage_ip='BMC IP',
        manage_pass='登录密码',
        manage_pro='登录协议',
        manage_user='登录账号',
        manage_vlan='BMC VLAN'
    )
    # 定义表格参数，包括工作表名称、起始ID、结束ID和数据路径等
    basic_table_arg = TableArg(sheet_name='4.1 设备初始化配置',
                               start_id='2、网络&存储设备管理信息',
                               end_id='3、分布式存储设备管理信息',
                               data_path=DATA_DIR,
                               slice_index=1)
    # 定义过滤器，仅选择使用ssh协议的设备
    sw_filter = Filter(key='登录协议',
                       value='ssh')
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取基本设备信息表格
    basic = dc.get_basic(table_arg=basic_table_arg, table_head=basic_head, sw_filter=sw_filter)
    return basic.get_basic()


@lru_cache(maxsize=128)
def create_snmp():
    """
    创建SNMP配置。

    Returns:
        SNMP配置数据。
    """
    # 初始化SNMP表头信息
    snmp_head = NetDevSNMPTableHead(
        version='SNMP版本',
        user='用户名',
        authentication_protocol='认证协议',
        authentication_pass='认证密码',
        encryption_protocol='数据加密协议',
        encryption_pass='加密密码',
        port='端口',
        read_community='读团体字',
        write_community='写团体字')

    # 定义表格参数
    snmp_table_arg = TableArg(sheet_name='4.1 设备初始化配置',
                              start_id='2、网络&存储设备管理信息',
                              end_id='3、分布式存储设备管理信息',
                              data_path=DATA_DIR,
                              slice_index=1)
    # 创建过滤器
    sw_filter = Filter(key='登录协议',
                       value='ssh')
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取SNMP配置
    snmp = dc.get_snmp(table_arg=snmp_table_arg, table_head=snmp_head, sw_filter=sw_filter)
    return snmp.get_snmp()


@lru_cache(maxsize=128)
def create_mlag():
    """
    创建MLAG配置。

    Returns:
        MLAG配置数据。
    """
    # 初始化MLAG表头信息
    m_lag_head = NetDevMLAGTableHead(
        ci_name='CI NAME',
        dad_ip='DAD互联IP',
        dad_mask='DAD子网掩码',
        dad_phy='DAD链路',
        dad_vrf='DAD VRF',
        dev_group_id='设备组ID',
        dfs_group='DFS-Group ID',
        eth_trunk_id='Eth-Trunk ID',
        peer_Link='Peer-Link',
        peer_Link_phy='Peer-Link物理口',
        priority='priority',
        v_stp_br_add_mac='Stp-bridge-address MAC'
    )
    # 定义表格参数
    net_m_lag_table_arg = TableArg(sheet_name='3.2.1 M-lag规划',
                                   start_id=None,
                                   end_id=None,
                                   data_path=DATA_DIR,
                                   slice_index=0)
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取MLAG配置
    mlag = dc.get_m_lag(table_arg=net_m_lag_table_arg, table_head=m_lag_head)
    return mlag.get_m_lag()


@lru_cache(maxsize=128)
def create_vrf():
    """
    创建VRF配置。

    Returns:
        VRF配置数据。
    """
    # 初始化VRF表头信息
    vrf_head = NetVrfTableHead(
        ci_name='CI NAME',
        vrf_name='VRF',
        vrf_rd='route-distinguisher',
        vrf_v6='VRFv6',
        vrf_rt='vpn-target',
    )
    # 定义表格参数
    vrf_table_arg = TableArg(sheet_name='3.5 VRF规划',
                             start_id=None,
                             end_id=None,
                             data_path=DATA_DIR,
                             slice_index=0)
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取VRF配置
    vrf = dc.get_vrf(table_arg=vrf_table_arg, table_head=vrf_head)
    return vrf.get_vrf()


@lru_cache(maxsize=128)
def create_global_vlan():
    """
    创建全局VLAN配置。

    Returns:
        全局VLAN配置数据。
    """
    # 初始化全局VLAN表头信息
    global_vlan_head = NetDevGlobalVlanTableHead(
        dev_ci_name='网关设备CI NAME',
        gw_ip='网关',
        gw_local_ip='local ip',
        gw_mac='VLAN MAC',
        gw_mask='网段/掩码',
        gw_type='网关类型',
        gw_vrf='VRF',
        net_plane='网络平面名称',
        vlan_id='VLAN ID'
    )
    # 定义表格参数
    global_vlan_table_arg = TableArg(sheet_name='3.1.1 IP&VLAN规划(二层组网)',
                                     start_id=None,
                                     end_id=None,
                                     data_path=DATA_DIR,
                                     slice_index=0)
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取全局VLAN配置
    global_vlan = dc.get_global_vlan(table_arg=global_vlan_table_arg, table_head=global_vlan_head)
    return global_vlan.get_global_vlan()


@lru_cache(maxsize=128)
def create_gw():
    """
    创建并初始化网关信息。

    本函数通过初始化网关设备配置信息收集器，根据提供的表格参数和头部信息，
    获取网关设备的详细信息并返回其网关地址。

    Returns:
        网关设备的网关地址。
    """
    # 初始化网关设备表格头部信息
    gw_head = NetDevGWTableHead(
        dev_ci_name='网关设备CI NAME',
        gw_ip='网关',
        gw_local_ip='local ip',
        gw_mac='VLAN MAC',
        gw_mask='网段/掩码',
        gw_type='网关类型',
        gw_vrf='VRF',
        net_plane='网络平面名称',
        vlan_id='VLAN ID'
    )
    # 设置表格参数
    gw_table_arg = TableArg(sheet_name='3.1.1 IP&VLAN规划(二层组网)',
                            start_id=None,
                            end_id=None,
                            data_path=DATA_DIR,
                            slice_index=0)
    # 初始化设备配置信息收集器
    dc = initialize_device_config_collector()
    # 获取网关信息
    gw = dc.get_gw(table_arg=gw_table_arg, table_head=gw_head)
    # 返回网关地址
    return gw.get_gw()


@lru_cache(maxsize=128)
def create_ndi_l3_int():
    """
    创建并初始化三层接口信息。

    本函数通过初始化网络设备本地与远端三层接口信息的表格头部，根据提供的
    表格参数，获取网络设备的三层接口详细信息并返回。

    Returns:
        网络设备的三层接口信息。
    """
    # 初始化本地三层接口表格头部信息
    local_l3_int_head = NetDevLocalL3IntTableHead(
        local_ci_name='本端CI NAME',
        local_ip_address='本端IP',
        local_logical_port='本端逻辑端口',
        local_vrf='本端VRF'
    )
    # 初始化远端三层接口表格头部信息
    remote_l3_int_head = NetDevRemoteL3IntTableHead(
        remote_ci_name='对端CI NAME',
        remote_ip_address='对端IP',
        remote_logical_port='对端逻辑端口',
        remote_vrf='对端VRF'
    )
    # 从子头部构造三层接口表格头部
    ndi_l3_int_head = NetDevL3IntTableHead.from_sub_heads(local_head=local_l3_int_head, remote_head=remote_l3_int_head)
    # 设置表格参数
    ndi_l3_info_table_arg = TableArg(sheet_name='3.9 网络设备对接信息规划_三层',
                                     start_id=None,
                                     end_id=None,
                                     data_path=DATA_DIR,
                                     slice_index=0)
    # 初始化设备配置信息收集器
    dc = initialize_device_config_collector()
    # 获取三层接口信息
    ndi_l3 = dc.get_l3_intf_info(table_arg=ndi_l3_info_table_arg, table_head=ndi_l3_int_head)
    # 返回三层接口信息
    return ndi_l3.get_l3_intf_info()


@lru_cache(maxsize=128)
def create_ndi_l2_int():
    """
    创建并初始化二层接口信息。

    本函数通过初始化网络设备本地与远端二层接口信息的表格头部，根据提供的
    表格参数，获取网络设备的二层接口详细信息并返回。

    Returns:
        网络设备的二层接口信息。
    """
    # 初始化本地二层接口表格头部信息
    local_ndi_l2_head = NetDevLocalL2IntTableHead(
        local_eth='本端Eth-Trunk ID',
        local_int_type='本端端口模式',
        local_m_lag_id='本端M-lag ID',
        local_phy='本端物理端口',
        local_trunk_vlan='本端透传VLAN',
        local_ci_name='本端CI NAME'
    )
    # 初始化远端二层接口表格头部信息
    remote_ndi_l2_head = NetDevRemoteL2IntTableHead(
        remote_phy='对端物理端口',
        remote_ci_name='对端CI NAME',
        remote_eth='对端Eth-Trunk ID',
        remote_int_type='对端端口模式',
        remote_m_lag_id='对端M-lag ID',
        remote_trunk_vlan='对端透传VLAN'
    )
    # 从子头部构造二层接口表格头部
    ndi_l2_head = NetDevL2IntTableHead.from_sub_heads(local_head=local_ndi_l2_head, remote_head=remote_ndi_l2_head)
    # 设置表格参数
    ndi_l2_info_table_arg = TableArg(sheet_name='3.8 网络设备对接信息规划_二层',
                                     start_id=None,
                                     end_id=None,
                                     data_path=DATA_DIR,
                                     slice_index=0)
    # 初始化设备配置信息收集器
    dc = initialize_device_config_collector()
    # 获取二层接口信息
    l2 = dc.get_l2_intf_info(table_arg=ndi_l2_info_table_arg, table_head=ndi_l2_head)
    # 返回二层接口信息
    return l2.get_l2_intf_info()


@lru_cache(maxsize=128)
def create_downlink_intf():
    """
    创建下联接口配置信息。

    本函数通过设备配置收集器初始化并获取下联接口信息，包括但不限于本端和对端的端口、VLAN等配置。

    Returns:
        NetDownlinkInterface: 下联接口配置信息对象。
    """
    # 定义下联接口数据表参数
    downlink_table_arg = TableArg(sheet_name='3.13 服务器对接信息规划',
                                  start_id=None,
                                  end_id=None,
                                  data_path=DATA_DIR,
                                  slice_index=0)

    # 定义下联接口表头信息
    downlink_head = NetDevDownlinkIntfTableHead(
        force_up='是否force-up',
        int_type='本端端口模式',
        lacp_mode='lacp mode',
        lacp_timeout_mode='lacp timeout mode',
        local_ci_name='本端CI NAME',
        local_logical_port='本端逻辑端口',
        local_m_lag_id='M-lag ID',
        local_phy='本端物理端口',
        pvid='PVID',
        remote_ci_name='对端CI NAME',
        remote_phy='对端物理端口',
        trunk_vlan='Trunk Vlan',
        untag_vlan='UNTAG VLAN'
    )
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取下联接口信息
    downlink = dc.get_downlink_interface(table_arg=downlink_table_arg, table_head=downlink_head)
    return downlink.get_net_downlink_interface()


@lru_cache(maxsize=128)
def create_look_back():
    """
    创建Loopback配置信息。

    本函数通过设备配置收集器初始化并获取Loopback信息，包括Loopback ID、IP和掩码等配置。

    Returns:
        LookBack: Loopback配置信息对象。
    """
    # 定义Loopback表头信息
    look_backup_head = NetLookBackupTableHead(
        ci_name='CI NAME',
        id='Loopback ID',
        ip='Loopback IP',
        mask='掩码'
    )
    # 定义Loopback数据表参数
    look_backup_table_arg = TableArg(sheet_name='3.4 Loopback规划',
                                     start_id=None,
                                     end_id=None,
                                     data_path=DATA_DIR,
                                     slice_index=0, )
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取Loopback信息
    look_back = dc.get_lookback(table_arg=look_backup_table_arg, table_head=look_backup_head)
    return look_back.get_lookback()


@lru_cache(maxsize=128)
def create_netconf():
    """
    创建Netconf配置信息。

    本函数通过设备配置收集器初始化并获取Netconf配置，包括设备名称、用户名和密码等。

    Returns:
        NetConf: Netconf配置信息对象。
    """
    # 定义Netconf数据表参数
    net_conf_table_arg = TableArg(sheet_name='4.1 设备初始化配置',
                                  start_id='4、netconf协议',
                                  end_id='5、对接openstack',
                                  data_path=DATA_DIR,
                                  slice_index=0)
    # 定义Netconf表头信息
    netconf_table_head = NetDevNetConfProTableHead(
        net_conf_dev_name='设备名称',
        net_conf_user='用户名',
        net_conf_pass='密码'
    )
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取Netconf配置信息
    netconf = dc.get_netconf(table_arg=net_conf_table_arg, table_head=netconf_table_head)
    return netconf.get_netconf()


@lru_cache(maxsize=128)
def create_static_route():
    """
    创建静态路由配置信息。

    本函数通过设备配置收集器初始化并获取静态路由信息，包括目的网络、下一跳和优先级等配置。

    Returns:
        StaticRoute: 静态路由配置信息对象。
    """
    # 定义静态路由表头信息
    static_route_head = NetDevStaticRouteTableHead(
        ci_name='CI NAME',
        destination_net='目的网络/掩码',
        local_vrf='VRF/安全域',
        next_hop='下一跳地址',
        bfd='关联',
        priority='路由优先级'
    )
    # 定义静态路由数据表参数
    static_route_args = TableArg(sheet_name='3.12 静态路由规划',
                                 start_id=None,
                                 end_id=None,
                                 data_path=DATA_DIR,
                                 slice_index=0)
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取静态路由信息
    static_route = dc.get_static_route(table_arg=static_route_args, table_head=static_route_head)
    return static_route.get_static_route()


@lru_cache(maxsize=128)
def create_bfd():
    """
    创建BFD配置信息。

    本函数通过设备配置收集器初始化并获取BFD信息，包括BFD ID、接口和目的IP等配置。

    Returns:
        BFD: BFD配置信息对象。
    """
    # 定义BFD表头信息
    bfd_head = NetDevBFDTableHead(
        ci_name='CI NAME',
        discriminator_local='BFD ID',
        interface='BFD单臂接口',
        local_vrf='VRF/安全域',
        peer_ip='NQA/BFD探测IP（目的IP）'
    )
    # 定义BFD数据表参数
    bfd_args = TableArg(sheet_name='3.12 静态路由规划',
                        start_id=None,
                        end_id=None,
                        data_path=DATA_DIR,
                        slice_index=0)
    # 初始化设备配置收集器
    dc = initialize_device_config_collector()
    # 获取BFD信息
    bfd = dc.get_bfd(table_arg=bfd_args, table_head=bfd_head)
    return bfd.get_bfd()
