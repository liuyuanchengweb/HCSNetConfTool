import logging
from src.data_processing.net_device_data_extractor import NetDeviceDataExtractor
from src.data_processing.netdev_conf import (create_instance,
                                             NetDevBasic,
                                             NetDevSNMP,
                                             NetDevL2IntfInfoConfig,
                                             NetDevL3IntfInfo,
                                             NetDevDownlinkInterface,
                                             NetDevMlag,
                                             NetDevConf,
                                             NetDveLookback,
                                             NetDevVrf,
                                             NetDevGW, T,
                                             NetDevStaticRoute,
                                             NetDevBFD,
                                             NetDevGlobalVlan
                                             )
from src.models.table_structure import (TableArg,
                                        Filter,
                                        NetDevBasicTableHead,
                                        NetDevSNMPTableHead,
                                        NetDevL2IntTableHead,
                                        NetDevL3IntTableHead,
                                        NetDevDownlinkIntfTableHead,
                                        NetDevMLAGTableHead,
                                        NetDevNetConfProTableHead,
                                        NetLookBackupTableHead,
                                        NetVrfTableHead,
                                        NetDevGWTableHead,
                                        NetDevStaticRouteTableHead,
                                        NetDevBFDTableHead,
                                        NetDevGlobalVlanTableHead
                                        )


class DeviceConfigCollector:
    """
    设备配置收集器类，用于从网络设备中加载和过滤数据。

    该类主要通过NetDeviceDataExtractor实例来提取和处理网络设备数据，并提供过滤功能以满足用户特定的需求。
    """

    def __init__(self, net_device_data_extractor: NetDeviceDataExtractor):
        """
        初始化DeviceConfigCollector实例。

        参数:
        - net_device_data_extractor: NetDeviceDataExtractor的实例，用于提取和处理网络设备数据。
        """
        self.net_device_data_extractor = net_device_data_extractor

    def _load_and_filter_data(self, table_arg: TableArg, sw_filter=None, table_head=None) -> T:
        """
        从Excel中加载数据并根据提供的过滤条件进行过滤。

        参数:
        - table_arg: TableArg类型，指定Excel表格参数。
        - sw_filter: 可选的过滤条件实例，用于对加载的数据进行过滤。
        - table_head: 表头信息，用于创建结果实例时的表头。

        返回:
        - 根据过滤后的数据和表头信息创建的实例。

        抛出:
        - ValueError: 如果过滤条件的键不是“登录协议”。

        该方法尝试从Excel中加载数据，如果提供了过滤条件sw_filter，则按照过滤条件进行数据过滤。
        最后，根据过滤后的数据和提供的表头信息创建并返回一个实例。
        如果在处理过程中发生异常，将捕获并打印异常信息。
        """
        logging.debug(f"开始加载和过滤数据。{table_head}")
        try:
            # 从Excel加载并处理数据
            result = self.net_device_data_extractor.load_processed_df_from_excel(table_arg=table_arg)
            logging.debug(f"数据已成功加载。{result}")
            # 如果提供了过滤条件
            if sw_filter:
                # 目前只支持对“登录协议”这一列进行过滤
                if sw_filter.key in ['登录协议']:
                    result = result.loc[result[sw_filter.key] == sw_filter.value]
                    logging.debug(f"按登录协议过滤数据。{result}")
                else:
                    raise ValueError("Invalid filter key")

            # 根据处理后的数据和表头信息创建实例并返回
            instance = create_instance(result, table_head)
            logging.debug(f"数据已处理完毕，实例已创建。{instance}")
            return instance

        except Exception as e:
            # 捕获并打印异常信息
            logging.error(f"发生错误：{e}")

    def get_basic(self, table_arg: TableArg, sw_filter: Filter,
                  table_head: NetDevBasicTableHead) -> NetDevBasic:
        """
        获取网络设备基本数据。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param sw_filter: 过滤条件，用于对数据进行筛选。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevBasic对象，包含筛选后的网络设备基本数据。
        """
        return self._load_and_filter_data(table_arg, sw_filter, table_head)

    def get_snmp(self, table_arg: TableArg, sw_filter: Filter,
                 table_head: NetDevSNMPTableHead) -> NetDevSNMP:
        """
        获取SNMP相关的网络设备数据。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param sw_filter: 过滤条件，用于对数据进行筛选。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevSNMP对象，包含筛选后的SNMP相关数据。
        """
        return self._load_and_filter_data(table_arg, sw_filter, table_head)

    def get_l2_intf_info(self, table_arg: TableArg,
                         table_head: NetDevL2IntTableHead) -> NetDevL2IntfInfoConfig:
        """
        获取网络设备的二层接口信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevInterconnectionInterface对象，包含网络设备的二层接口信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_l3_intf_info(self, table_arg: TableArg,
                         table_head: NetDevL3IntTableHead) -> NetDevL3IntfInfo:
        """
        获取网络设备的三层接口信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevL3IntfInfo对象，包含网络设备的三层接口信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_downlink_interface(self, table_arg: TableArg,
                               table_head: NetDevDownlinkIntfTableHead) -> NetDevDownlinkInterface:
        """
        获取网络设备的下联接口信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevDownlinkInterface对象，包含网络设备的下联接口信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_m_lag(self, table_arg: TableArg,
                  table_head: NetDevMLAGTableHead) -> NetDevMlag:
        """
        获取网络设备的MLAG（多链路聚合组）信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevMlag对象，包含网络设备的MLAG信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_netconf(self, table_arg: TableArg,
                    table_head: NetDevNetConfProTableHead) -> NetDevConf:
        """
        获取网络设备的NetConf协议相关信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevConf对象，包含网络设备的NetConf协议相关信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_lookback(self, table_arg: TableArg,
                     table_head: NetLookBackupTableHead) -> NetDveLookback:
        """
        获取网络设备的Loopback接口信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDveLookback对象，包含网络设备的Loopback接口信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_vrf(self, table_arg: TableArg,
                table_head: NetVrfTableHead) -> NetDevVrf:
        """
        获取网络设备的VRF（虚拟路由转发实例）信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevVrf对象，包含网络设备的VRF信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_gw(self, table_arg: TableArg,
               table_head: NetDevGWTableHead) -> NetDevGW:
        """
        获取网络设备的网关信息。

        :param table_arg: 表格参数，用于指定数据表的配置和上下文。
        :param table_head: 表头信息，用于指定表格的列名和属性。
        :return: 返回一个NetDevGW对象，包含网络设备的网关信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_static_route(self, table_arg: TableArg,
                         table_head: NetDevStaticRouteTableHead) -> NetDevStaticRoute:
        """
        获取静态路由信息

        该方法用于从网络设备中获取静态路由表的信息。它通过加载和筛选数据来生成一个静态路由对象。

        参数:
        - table_arg: TableArg类型，包含检索静态路由表所需的参数。
        - table_head: NetDevStaticRouteTableHead类型，静态路由表的表头信息，用于数据筛选。

        返回:
        - NetDevStaticRoute类型，表示网络设备的静态路由信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_bfd(self, table_arg: TableArg,
                table_head: NetDevBFDTableHead) -> NetDevBFD:
        """
        获取BFD（双向转发检测）信息

        该方法用于从网络设备中获取BFD会话表的信息。它通过加载和筛选数据来生成一个BFD对象。

        参数:
        - table_arg: TableArg类型，包含检索BFD会话表所需的参数。
        - table_head: NetDevBFDTableHead类型，BFD会话表的表头信息，用于数据筛选。

        返回:
        - NetDevBFD类型，表示网络设备的BFD会话信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)

    def get_global_vlan(self, table_arg: TableArg,
                        table_head: NetDevGlobalVlanTableHead) -> NetDevGlobalVlan:
        """
        获取全局VLAN信息

        该方法用于从网络设备中获取全局VLAN表的信息。它通过加载和筛选数据来生成一个全局VLAN对象。

        参数:
        - table_arg: TableArg类型，包含检索全局VLAN表所需的参数。
        - table_head: NetDevGlobalVlanTableHead类型，全局VLAN表的表头信息，用于数据筛选。

        返回:
        - NetDevGlobalVlan类型，表示网络设备的全局VLAN信息。
        """
        return self._load_and_filter_data(table_arg, table_head=table_head)
