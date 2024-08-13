from pathlib import Path

import yaml

from src.utils.ConfigModel import AppConfig
from src.utils.dev_con_file_path import SETTINGS_FILE
from src.utils.exceptions import DevConfLoadDataError


class AppConfigLoader:
    def __init__(self):
        if SETTINGS_FILE.exists():
            self.file_content = SETTINGS_FILE.read_text(encoding='utf-8')
            self.data = yaml.safe_load(self.file_content)
            self.config_class = AppConfig(**self.data)
        else:
            raise DevConfLoadDataError(SETTINGS_FILE)

    @property
    def base_dir(self):
        base_dir = self.config_class.BASE_DIR
        return base_dir

    @property
    def data_dir(self):
        data_dir = Path(self.base_dir).joinpath(self.config_class.DATA_DIR)
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
        return str(data_dir)

    @property
    def templates_dir(self):
        templates_dir = str(Path(self.base_dir).joinpath(self.config_class.TEMPLATES_DIR))
        return templates_dir

    @property
    def logs_dir(self):
        # 计算日志目录的完整路径
        logs_dir = Path(self.base_dir).joinpath(self.config_class.LOGS_DIR)

        # 检查目录是否存在，如果不存在则创建
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)

        # 返回目录路径
        return str(logs_dir)

    @property
    def lld_file_name(self):
        lld_file_name = self.config_class.LLD_FILE_NAME
        if lld_file_name:
            return lld_file_name
        else:
            raise DevConfLoadDataError(f"{lld_file_name}请配置LLD文件名，或者配置LLD_FILE路径")

    @property
    def lld_file(self):
        if not self.config_class.LLD_FILE:
            lld_file = str(Path(self.data_dir).joinpath(self.lld_file_name))
            return lld_file
        return self.config_class.LLD_FILE

    @property
    def save_config_dir(self):
        save_config_dir = str(Path(self.data_dir).joinpath(self.config_class.SAVE_CONFIG_DIR))
        return save_config_dir

    @property
    def settings_dir(self):
        settings_dir = str(Path(self.base_dir).joinpath(self.config_class.SETTINGS_DIR))
        return settings_dir

    @property
    def template_name(self):
        template_name = self.data['template_name']
        return template_name

    @property
    def model_mapping(self):
        model_mapping = self.data['model_mapping']
        return model_mapping

    def update_config(self, data):
        self.data.update(data)
        self.file_content = yaml.safe_dump(self.data)
        SETTINGS_FILE.write_text(self.file_content, encoding='utf-8')

    def update_lld_name(self, lld_name):
        self.update_config({'LLD_FILE_NAME': lld_name})
        settings_file = Path(app_config.settings_dir).joinpath('settings.yaml')
        lld_name = self.data['LLD_FILE_NAME']
        return settings_file, lld_name

    def update_lld_file_path(self, lld_file_path):
        self.update_config({'LLD_FILE': lld_file_path})
        settings_file = Path(app_config.settings_dir).joinpath('settings.yaml')
        lld_file_path = self.data['LLD_FILE']
        return settings_file, lld_file_path


app_config = AppConfigLoader()
