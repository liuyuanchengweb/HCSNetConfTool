from src.command import parse_arguments, execute_command
from src.config.app_config_loader import app_config
from src.logs.logger import configure_logging

configure_logging(app_config.logs_dir)
if __name__ == '__main__':
    args = parse_arguments()
    execute_command(args)

