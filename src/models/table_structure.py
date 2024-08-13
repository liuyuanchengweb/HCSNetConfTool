from dataclasses import dataclass
from typing import Optional, Generic, TypeVar


@dataclass
class TableArg:
    sheet_name: str
    start_id: str | None
    end_id: str | None
    data_path: str
    slice_index: int


@dataclass
class Filter:
    key: str
    value: str


@dataclass
class NetDevSNMPTableHead:
    version: str
    user: str
    authentication_protocol: str
    authentication_pass: str
    encryption_protocol: str
    encryption_pass: str
    port: str
    read_community: str
    write_community: str


@dataclass
class NetDevBasicTableHead:
    device_name: str
    manage_vlan: str
    manage_ip: str
    manage_pro: str
    manage_user: str
    manage_pass: str


TLocal = TypeVar('TLocal')
TRemote = TypeVar('TRemote')


@dataclass
class NetDevLocalBase:
    local_ci_name: str


@dataclass
class NetDevRemoteBase:
    remote_ci_name: str


@dataclass
class NetDevCombinedHead(Generic[TLocal, TRemote]):
    net_dev_local: Optional[TLocal] = None
    net_dev_remote: Optional[TRemote] = None

    @classmethod
    def from_sub_heads(cls, local_head: Optional[TLocal],
                       remote_head: Optional[TRemote]) -> 'NetDevCombinedHead[TLocal, TRemote]':
        instance = cls()
        if local_head is not None:
            for k, v in local_head.__dict__.items():
                instance.__dict__[k] = v
        if remote_head is not None:
            for k, v in remote_head.__dict__.items():
                instance.__dict__[k] = v
        return instance


@dataclass
class NetDevLocalL2IntTableHead(NetDevLocalBase):
    local_phy: str
    local_eth: str
    local_int_type: str
    local_trunk_vlan: str
    local_m_lag_id: str


@dataclass
class NetDevRemoteL2IntTableHead(NetDevRemoteBase):
    remote_phy: str
    remote_eth: str
    remote_int_type: str
    remote_trunk_vlan: str
    remote_m_lag_id: str


@dataclass
class NetDevL2IntTableHead(NetDevCombinedHead[NetDevLocalL2IntTableHead, NetDevRemoteL2IntTableHead]):
    pass


@dataclass
class NetDevLocalL3IntTableHead(NetDevLocalBase):
    local_logical_port: str
    local_vrf: str
    local_ip_address: str


@dataclass
class NetDevRemoteL3IntTableHead(NetDevRemoteBase):
    remote_logical_port: str
    remote_vrf: str
    remote_ip_address: str


@dataclass
class NetDevL3IntTableHead(NetDevCombinedHead[NetDevLocalL3IntTableHead, NetDevRemoteL3IntTableHead]):
    pass


@dataclass
class NetDevDownlinkIntfTableHead:
    local_ci_name: str
    local_phy: str
    int_type: str
    local_logical_port: str
    local_m_lag_id: str
    lacp_mode: str
    lacp_timeout_mode: str
    force_up: str
    trunk_vlan: str
    pvid: str
    untag_vlan: str
    remote_ci_name: str
    remote_phy: str
    description: Optional[str] = None


@dataclass
class NetDevMLAGTableHead:
    dev_group_id: str
    ci_name: str
    dfs_group: str
    priority: str
    peer_Link_phy: str
    eth_trunk_id: str
    peer_Link: str
    dad_phy: str
    dad_vrf: str
    dad_ip: str
    dad_mask: str
    v_stp_br_add_mac: str


@dataclass
class NetDevNetConfProTableHead:
    net_conf_dev_name: str
    net_conf_user: str
    net_conf_pass: str


@dataclass
class NetDevStackTableHead:
    group_id: str
    dev_name: str
    stack_name: str
    member: str
    priority: str
    domain: str
    interface: str


@dataclass
class NetLookBackupTableHead:
    ci_name: str
    ip: str
    mask: str
    id: str


@dataclass
class NetVrfTableHead:
    ci_name: str
    vrf_name: str
    vrf_rd: str
    vrf_v6: Optional[str] = None
    vrf_rt: Optional[str] = None
    vrf_rt_import: Optional[str] = None
    vrf_rt_export: Optional[str] = None


@dataclass
class NetDevGWTableHead:
    net_plane: str
    vlan_id: str
    gw_vrf: str
    gw_ip: str
    gw_mask: str
    gw_type: str
    gw_local_ip: str
    dev_ci_name: str
    gw_mac: str
    ci_name: Optional[str] = None


@dataclass
class NetDevStaticRouteTableHead:
    ci_name: str
    destination_net: str
    next_hop: str
    priority: str
    local_vrf: str
    bfd: str


@dataclass
class NetDevBFDTableHead:
    ci_name: str
    peer_ip: str
    local_vrf: str
    interface: str
    discriminator_local: str


class NetDevGlobalVlanTableHead(NetDevGWTableHead):
    pass
