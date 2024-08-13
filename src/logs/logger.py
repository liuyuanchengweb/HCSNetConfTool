import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(log_dir, log_file='app.log', file_log_level=logging.DEBUG, console_log_level=logging.INFO):
    """
    配置日志记录器。

    参数:
        log_dir (str): 日志文件所在的目录路径。
        log_file (str, 可选): 日志文件的名字，默认为 'app.log'。
        file_log_level (int, 可选): 文件日志级别，默认为 logging.DEBUG。
        console_log_level (int, 可选): 控制台日志级别，默认为 logging.INFO。

    此函数会创建一个日志目录（如果不存在），并设置一个滚动文件日志处理器，
    使得日志文件达到一定大小后会被分割保存。同时也会设置日志格式，并将日志
    输出到文件和控制台，确保文件日志级别为 DEBUG，而控制台日志级别为 INFO。

    返回:
        None
    """

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / log_file

    # 创建一个可以滚动的日志文件处理器，并指定编码为UTF-8
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=5, encoding='utf-8')

    # 设置日志格式，包括时间、日志级别、模块名称、方法名称、行号以及消息
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
    file_handler.setFormatter(formatter)

    # 获取或创建基于当前模块名的记录器
    module_logger = logging.getLogger(__name__)
    # 设置记录器的日志级别
    module_logger.setLevel(file_log_level)

    # 添加文件处理器到记录器
    module_logger.addHandler(file_handler)

    # 创建控制台处理器，并设置相同的日志格式
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_log_level)
    module_logger.addHandler(console_handler)  # 同时记录到控制台

    # 将配置应用于 root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(file_log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)  # 确保控制台输出与日志文件中的信息一致




