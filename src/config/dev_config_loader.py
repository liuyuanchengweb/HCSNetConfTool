from typing import List

import yaml
from src.utils.ConfigModel import BasicCon, SnmpCon, OptionCon
from src.utils.dev_con_file_path import CONFIG_FILE
from src.utils.exceptions import DevConfLoadDataError


class DevConfigLoader:
    def __init__(self):
        if CONFIG_FILE.exists():
            self.file_content = CONFIG_FILE.read_text(encoding='utf-8')
            self.data = yaml.safe_load(self.file_content)
        else:
            raise DevConfLoadDataError(CONFIG_FILE)

    def get_dev_config(self) -> dict:
        return self.data

    @property
    def get_basic_config(self) -> BasicCon:
        return BasicCon(**self.data['basic_config'])

    @property
    def get_snmp_config(self) -> SnmpCon:
        return SnmpCon(**self.data['snmp_config'])

    @property
    def get_ci_names(self) -> List[str]:
        return self.data['ci_name_list']

    @property
    def get_options(self) -> OptionCon:
        return OptionCon(**self.data['option_config'])


dev_config_loader = DevConfigLoader()
