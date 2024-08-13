from pathlib import Path

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    BASE_DIR: str = Field(default_factory=lambda: str(Path(__file__).parent.parent.parent))
    DATA_DIR: str
    TEMPLATES_DIR: str
    LOGS_DIR: str
    LLD_FILE_NAME: str | None
    SAVE_CONFIG_DIR: str
    LLD_FILE: str | None = None
    SETTINGS_DIR: str = None


class BasicCon(BaseModel):
    manage_vrf_name: str | None = Field(default=None, title="management vrf name")
    option_manage_mode: bool = Field(default=False, title="management mode")
    manage_gw_ip: str | None = Field(default=None, title="management gateway ip")
    sftp: bool = Field(default=False, title="enable sftp")


class SnmpCon(BaseModel):
    target_host: str | None = Field(default=None, title="snmp target host")
    udp_port: int | None = Field(default=10162, title="snmp udp port")
    target_host_host_name: str | None = Field(default=None, title="snmp target host host name")


class OptionCon(BaseModel):
    option_vrf: bool = Field(default=True, title="vrf option")
    option_snmp: bool = Field(default=True, title="snmp option")
    option_mlag: bool = Field(default=True, title="mlag option")
    option_batch_vlan: bool = Field(default=True, title="batch vlan option")
    option_global_vlan: bool = Field(default=True, title="global vlan option")
    option_gw: bool = Field(default=True, title="gw option")
    option_l3_vlan: bool = Field(default=True, title="l3 vlan option")
    option_l3_phy: bool = Field(default=True, title="l3 phy option")
    option_ndi_l2: bool = Field(default=True, title="ndi l2 option")
    option_server_int: bool = Field(default=True, title="server int option")
    option_netconf: bool = Field(default=True, title="netconf option")
    option_look_back: bool = Field(default=True, title="look back option")
    option_static_route: bool = Field(default=True, title="static route option")
    option_bfd: bool = Field(default=True, title="bfd option")
