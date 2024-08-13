import ipaddress
import re
from pydantic import BaseModel, model_validator, Field
from typing import Optional, Any, Union, Literal, Dict

from src.utils.public_method import NumberFormatter, is_valid_eth_trunk


class VrfConfig(BaseModel):
    vrf_name: str
    vrf_rd: str
    option_vrf_v6: Optional[bool] = False
    vrf_v6: Optional[str] = None
    option_vrf_rt: Optional[bool] = False
    vrf_rt: Optional[str] = None

    @model_validator(mode='after')
    def post_init(self):
        if self.vrf_rt is not None and self.vrf_rt != '-':
            self.option_vrf_rt = True
        if self.vrf_v6 is not None and self.vrf_v6 != '-':
            self.option_vrf_v6 = True


class DeviceSNMPConfig(BaseModel):
    version: Literal["SNMPV3", "SNMPV2c", "v2c", "v3"]
    user: str
    authentication_protocol: Optional[str] = None
    authentication_pass: Optional[str] = None
    encryption_protocol: Optional[str] = None
    encryption_pass: Optional[str] = None
    port: Optional[int | str] = None
    read_community: Optional[Union[str, bool]] = None
    write_community: Optional[Union[str, bool]] = None
    target_host: Optional[str] = None
    udp_port: Optional[int] = Field(default=10162)
    target_host_host_name: Optional[str] = None
    option_target: Optional[bool] = False

    @staticmethod
    def ipv4_to_hex(ip):
        ip_int = int(ipaddress.IPv4Address(ip))
        hex_str = format(ip_int, '08x')
        return f'host_name{hex_str}'

    @model_validator(mode='after')
    def val_ver(self):
        self.port = str(self.port)
        v2c = re.match('.*2.*', self.version)
        if v2c:
            if not self.read_community and self.write_community != '-':
                self.version = 'v2c'
                raise ValueError('SNMP v2c must have read or write community')
        else:
            if self.authentication_pass != '-' or self.encryption_pass != '-':
                self.version = 'v3'
                self.read_community = False
                self.write_community = False
            else:
                raise ValueError('SNMP v3 must have authentication or encryption')
        if self.target_host is not None:
            self.option_target = True
            self.target_host_host_name = self.ipv4_to_hex(self.target_host)


class DeviceBasicsConfig(BaseModel):
    device_name: str
    manage_ip: str
    manage_pro: str
    manage_user: str
    manage_pass: str
    manage_vlan: Optional[str | int] = None
    manage_mask: Optional[str] = Field(default='255.255.255.0')
    option_manage_mode: Optional[bool] = False
    option_manage_vrf: Optional[bool] = False
    manage_vrf_name: Optional[VrfConfig] = None
    manage_int: Optional[str] = None
    option_manage_gw: Optional[bool] = False
    manage_gw_ip: Optional[str] = None
    sftp: Optional[bool | str] = False

    @model_validator(mode='after')
    def port_init(self):
        self.manage_vlan = str(self.manage_vlan)
        if self.manage_gw_ip is not None:
            self.option_manage_gw = True
        if self.manage_vrf_name is not None:
            self.option_manage_vrf = True


class DeviceInterfaceConfig(BaseModel):
    phy: str
    eth_trunk: Optional[str] = None
    m_lag_id: Optional[str] = None
    int_type: Optional[str] = None
    trunk_vlan: Optional[str] = None
    pvid: Optional[str] = '1'
    untag_vlan: Optional[str] = '1'
    lacp_mode: Literal["static", "dynamic", False] = False
    lacp_timeout_mode: Optional[bool | str] = False
    force_up: Optional[bool | str] = False
    description: Optional[str] = None,
    option_vray: Optional[bool] = True
    option_eth_trunk: Optional[bool] = False
    option_mlag: Optional[bool] = False

    @staticmethod
    def all_keys_valid(values, keys, invalid_values):
        """检查所有给定的键的值是否都在无效值列表中。"""
        return all(values.get(key) in invalid_values for key in keys)

    @model_validator(mode='before')
    @classmethod
    def type_conversion(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        在验证之前对模型字段进行类型转换和有效性检查.

        Parameters:
            values (Dict[str, Any]): 待验证和转换的字段值字典.

        Returns:
            Dict[str, Any]: 转换和验证后的字段值字典.
        """

        def is_valid_int_type(value: str) -> str | None:
            """
            检查 int_type 值是否有效，并返回小写版本.

            Parameters:
                value (str): 需要检查的 int_type 值.

            Returns:
                str | None: 有效且转换为小写后的 int_type 值，或 None.
            """
            valid_types = ['trunk', 'access', 'hybrid']
            value_lower = value.lower()
            return value_lower if value_lower in valid_types else None

        def int_to_str(value):
            """
            检查输入值是否为有效整数，如果是，转换为字符串.

            Parameters:
                value: 需要检查和转换的输入值.

            Returns:
                str: 输入值转换为字符串后的结果，或 False（如果输入值不是有效整数）.
            """
            try:
                int_value = int(value)
                return str(int_value)
            except (ValueError, TypeError):
                return str(1)

        # 如果存在，转换 trunk_vlan
        trunk_vlan = values.get('trunk_vlan')
        if trunk_vlan:
            formatter = NumberFormatter(trunk_vlan)
            values['trunk_vlan'] = formatter.process_input()

        # 根据条件设置 option_vray
        invalid_values = ['-', None, 'NA']
        keys_to_check = ['trunk_vlan', 'pvid', 'untag_vlan']

        if cls.all_keys_valid(values, keys_to_check, invalid_values):
            values['option_vray'] = False

        # 检查并设置 int_type
        int_type = values.get('int_type')
        if int_type:
            lower_int_type = is_valid_int_type(int_type)
            if lower_int_type is None:
                values['option_vray'] = False
            else:
                values['int_type'] = lower_int_type

        # 检查并设置 option_eth_trunk
        eth_trunk = values.get('eth_trunk')
        values['option_eth_trunk'] = is_valid_eth_trunk(eth_trunk)

        # 检查并转换 lacp_mode
        if not values.get('lacp_mode', '').isalpha():
            values['lacp_mode'] = False
        else:
            values['lacp_mode'] = values['lacp_mode'].lower()

        # 根据接口类型设置 pvid
        if not 'pvid' in values:
            if values['int_type'] == 'access':
                values['pvid'] = values['trunk_vlan']

        # 转换 pvid 和 untag_vlan
        values['pvid'] = int_to_str(values.get('pvid', '1'))
        values['untag_vlan'] = int_to_str(values.get('untag_vlan', '1'))

        mlag_id = values.get('m_lag_id', '-')
        try:
            int(mlag_id)
            values['option_mlag'] = True
        except (ValueError, TypeError):
            values['option_mlag'] = False
        return values


class DeviceL3IntConfig(BaseModel):
    phy: str
    ip: str
    mask: str
    vrf: Optional[str] = None
    option_vrf: Optional[bool] = False
    mac_add: Optional[str] = None
    vid: Optional[int] = None
    option_mac_add: Optional[bool] = False

    @model_validator(mode='before')
    @classmethod
    def type_conversion(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values['vrf'] != '-' and values['vrf'] != 'public':
            values['option_vrf'] = True
        return values


class DeviceGWConfig(BaseModel):
    vlan_id: str
    gw_ip: str
    gw_mask: str
    gw_type: str
    gw_mac: Optional[str] = None
    gw_vrf: Optional[str] = None
    option_vrf: Optional[bool] = False
    gw_local_ip: Optional[str] = None
    description: Optional[str] = None
    gw_mode: Optional[bool] = False
    vrrp_vrid: Optional[int] = None
    option_gw_mac: Optional[bool] = False

    @staticmethod
    def is_valid_mac(mac):
        pattern = r'^([0-9A-Fa-f]{4}-){2}[0-9A-Fa-f]{4}$'
        match = re.match(pattern, mac)
        return bool(match)

    @model_validator(mode='before')
    @classmethod
    def type_conversion(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values['gw_vrf'] != '-' and values['gw_vrf'] != 'public':
            values['option_vrf'] = True
        if values['gw_local_ip'] != '-':
            values['gw_mode'] = True
        if cls.is_valid_mac(values['gw_mac']):
            values['option_gw_mac'] = True
        return values


class DevMLAGConfig(BaseModel):
    dfs_group: str
    priority: str
    peer_Link_phy: str | list[str]
    eth_trunk_id: str
    peer_Link: str
    dad_phy: str
    dad_vrf: str
    dad_ip: str
    dad_mask: str
    v_stp_br_add_mac: str
    dad_vlan: Optional[str] = None
    dad_peer_ip: Optional[str] = None

    @staticmethod
    def is_30_bit_netmask(mask: str):
        net = ipaddress.IPv4Network(f"0.0.0.0/{mask}")
        if not net.prefixlen == 30:
            raise ValueError("Mask must be 30 bit")

    @staticmethod
    def get_peer_ip(ip: str, mask: str):
        ip_with_prefix = f"{ip}/{mask}"
        network = ipaddress.IPv4Network(ip_with_prefix, strict=False)
        hosts = network.hosts()
        for host in hosts:
            if str(host) != ip:
                return str(host)

    @staticmethod
    def peer_phy(peer_phy: str):
        phy = peer_phy.split(',')
        return phy

    @model_validator(mode='before')
    @classmethod
    def type_conversion(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values['dfs_group'] = str(values['dfs_group'])
        values['priority'] = str(values['priority'])
        values['eth_trunk_id'] = str(values['eth_trunk_id'])
        values['peer_Link'] = str(values['peer_Link'])
        local_ip = values['dad_ip']
        local_mask = values['dad_mask']
        cls.is_30_bit_netmask(local_mask)
        values['dad_peer_ip'] = cls.get_peer_ip(local_ip, local_mask)
        values['peer_Link_phy'] = cls.peer_phy(values['peer_Link_phy'])
        return values


class LookbackConfig(BaseModel):
    ip: str
    mask: str
    id: str

    @model_validator(mode='before')
    @classmethod
    def type_conversion(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if is_valid_eth_trunk(values['id']):
            values['id'] = str(values['id'])
        return values


class DevNetConf(BaseModel):
    user: str
    password: str


class DevStaticRouteConfig(BaseModel):
    destination_net: str
    destination_mask: str
    next_hop: str
    priority: Optional[str] = None
    local_vrf: Optional[str] = None
    bfd: Optional[bool | None] = None
    bfd_name: Optional[str] = None


class DevBFDConfig(BaseModel):
    bfd_name: str
    peer_ip: str
    local_vrf: Optional[str] = None
    interface: Optional[str] = None
    source_ip: Optional[str] = None
    discriminator_local: Optional[str] = None


class GlobalVlan(BaseModel):
    vlan_id: str | list
    description: Optional[str] = None
    batch_vlan: Optional[list[str]] = None
