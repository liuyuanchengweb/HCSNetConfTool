from dataclasses import dataclass, fields
from enum import Enum

from src.models.table_structure import NetDevMLAGTableHead, NetDevL2IntTableHead
from src.models.dev_Config import DevMLAGConfig, DeviceInterfaceConfig


def get_m_lag_alias_map():
    return {
        'dfs_group': 'dfs_group',
        'priority': 'priority',
        'peer_Link_phy': 'peer_Link_phy',
        'eth_trunk_id': 'eth_trunk_id',
        'peer_Link': 'peer_Link',
        'dad_phy': 'dad_phy',
        'dad_vrf': 'dad_vrf',
        'dad_ip': 'dad_ip',
        'dad_mask': 'dad_mask',
        'v_stp_br_add_mac': 'v_stp_br_add_mac',
    }


def get_m_lag_field_group_map():
    return {'ci_name':
                ['dfs_group', 'priority', 'peer_Link_phy', 'eth_trunk_id', 'peer_Link', 'dad_phy', 'dad_vrf', 'dad_ip',
                 'dad_mask', 'v_stp_br_add_mac']
            }


def get_l2_intf_alias_map():
    return {
        'local_phy': 'phy',
        'local_eth': 'eth_trunk',
        'local_int_type': 'int_type',
        'local_trunk_vlan': 'trunk_vlan',
        'local_m_lag_id': 'm_lag_id',
        'local_description': 'description',
        'remote_phy': 'phy',
        'remote_eth': 'eth_trunk',
        'remote_int_type': 'int_type',
        'remote_trunk_vlan': 'trunk_vlan',
        'remote_m_lag_id': 'm_lag_id',
        'remote_description': 'description',

    }


def get_l2_intf_field_group_map():
    return {
        'local_ci_name': ['local_phy', 'local_eth', 'local_int_type', 'local_trunk_vlan', 'local_m_lag_id',
                          'local_description'],
        'remote_ci_name': ['remote_phy', 'remote_eth', 'remote_int_type', 'remote_trunk_vlan', 'remote_m_lag_id',
                           'remote_description']
    }


def get_l3_intf_alias_map():
    return {
        'local_logical_port': 'phy',
        'local_vrf': 'vrf',
        'local_ip_address': 'ip',
        'local_mask': 'mask',
        'remote_logical_port': 'phy',
        'remote_vrf': 'vrf',
        'remote_ip_address': 'ip',
        'remote_mask': 'mask',
        'vid': 'vid'
    }


def get_l3_intf_field_group_map():
    return {
        'local_ci_name': ['local_logical_port', 'local_vrf', 'local_ip_address', 'local_mask', 'vid'],
        'remote_ci_name': ['remote_logical_port', 'remote_vrf', 'remote_ip_address', 'remote_mask', 'vid']
    }


def get_downlink_int_map():
    return {
        'local_phy': 'phy',
        'local_logical_port': 'eth_trunk',
        'local_m_lag_id': 'm_lag_id',
        'int_type': 'int_type',
    }


def get_downlink_int_table_map():
    return {
        'local_ci_name': ['local_phy', 'local_phy', 'int_type', 'local_logical_port', 'local_m_lag_id', 'lacp_mode',
                          'lacp_timeout_mode', 'force_up', 'trunk_vlan', 'pvid', 'untag_vlan', 'description']
    }


def get_netconf_map():
    return {'net_conf_user': 'user',
            'net_conf_pass': 'password'}


def get_netconf_table_map():
    return {'net_conf_dev_name': ['net_conf_user', 'net_conf_pass']}


def get_stack_map():
    return {'priority': 'priority',
            'domain': 'domain',
            'interface': 'interface', }


def get_stack_table_map():
    return {'stack_name': ['priority', 'domain', 'interface', ]}


def get_lookback_alias_map():
    return {
        'ip': 'ip',
        'mask': 'mask',
        'id': 'id',
    }


def get_lookback_field_group_map():
    return {
        'ci_name': ['ip', 'mask', 'id', ]
    }


def get_vrf_alias_map():
    return {
        'vrf_name': 'vrf_name',
        'vrf_rd': 'vrf_rd',
        'vrf_v6': 'vrf_v6',
        'vrf_rt': 'vrf_rt',
    }


def get_vrf_field_group_map():
    return {
        'ci_name': ['vrf_name', 'vrf_rd', 'vrf_v6', 'vrf_rt']
    }


def get_gw_alias_map():
    return {
        'vlan_id': 'vlan_id',
        'gw_vrf': 'gw_vrf',
        'gw_ip': 'gw_ip',
        'gw_mask': 'gw_mask',
        'gw_type': 'gw_type',
        'gw_local_ip': 'gw_local_ip',
        'gw_mac': 'gw_mac',
        'net_plane': 'description',
        'vrrp_vrid': 'vrrp_vrid',

    }


def get_gw_field_group_map():
    return {
        'ci_name': ['vlan_id', 'gw_vrf', 'gw_ip', 'gw_mask', 'gw_type', 'gw_local_ip', 'gw_mac', 'net_plane',
                    'vrrp_vrid']
    }


def get_basic_alias_map():
    return {
        'device_name': 'device_name',
        'manage_vlan': 'manage_vlan',
        'manage_ip': 'manage_ip',
        'manage_pro': 'manage_pro',
        'manage_user': 'manage_user',
        'manage_pass': 'manage_pass',
    }


def get_basic_field_group_map():
    return {
        'ci_name': ['device_name', 'manage_vlan', 'manage_ip', 'manage_pro', 'manage_user', 'manage_pass']
    }


def get_snmp_alias_map():
    return {
        'version': 'version',
        'user': 'user',
        'authentication_protocol': 'authentication_protocol',
        'authentication_pass': 'authentication_pass',
        'encryption_protocol': 'encryption_protocol',
        'encryption_pass': 'encryption_pass',
        'port': 'port',
        'read_community': 'read_community',
        'write_community': 'write_community',
    }


def get_snmp_field_group_map():
    return {
        'ci_name': ['version', 'user', 'authentication_protocol', 'authentication_pass', 'encryption_protocol',
                    'encryption_pass',
                    'port', 'read_community', 'write_community']
    }


def get_static_route_alias_map():
    return {
        'destination_net': 'destination_net',
        'destination_mask': 'destination_mask',
        'next_hop': 'next_hop',
        'priority': 'priority',
        'local_vrf': 'local_vrf',
        'bfd': 'bfd',
        'bfd_name': 'bfd_name',
    }


def get_static_route_field_group_map():
    return {
        'ci_name': ['destination_net', 'destination_mask', 'next_hop', 'priority', 'local_vrf', 'bfd', 'bfd_name']
    }


def get_bfd_alias_map():
    return {
        'bfd_name': 'bfd_name',
        'peer_ip': 'peer_ip',
        'local_vrf': 'local_vrf',
        'interface': 'interface',
        'discriminator_local': 'discriminator_local',
    }


def get_bfd_field_group_map():
    return {
        'ci_name': ['bfd_name', 'peer_ip', 'local_vrf', 'interface',  'discriminator_local', ]
    }


def get_global_alias_map():
    return {
        'vlan_id': 'vlan_id',
        'description': 'description',
    }


def get_global_field_group_map():
    return {
        'dev_ci_name': ['vlan_id', 'description', ]
    }


