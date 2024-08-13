from pathlib import Path

CON_FILE_NAME = 'DevConfig.yaml'
CONFIG_DIR = Path().cwd() / 'settings'
CONFIG_FILE = CONFIG_DIR / CON_FILE_NAME
SETTINGS_FILE_NAME = 'settings.yaml'
SETTINGS_FILE = Path(__file__).parents[2].joinpath('settings').joinpath(SETTINGS_FILE_NAME)
