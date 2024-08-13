import argparse
import logging
from src.config.dev_config_loader import dev_config_loader
from src.config.app_config_loader import app_config
from src.controller import RenderConfig, CreateJinja2, DeviceConfData
from src.init_pack.init_config import InitConfig


def run():
    basic = dev_config_loader.get_basic_config
    snmp = dev_config_loader.get_snmp_config
    ci_name = dev_config_loader.get_ci_names
    options = dev_config_loader.get_options
    render_config = RenderConfig(jinja2_env=CreateJinja2,
                                 dev_config=DeviceConfData,
                                 ci_name=ci_name,
                                 save_file_path=app_config.save_config_dir,
                                 template_name=app_config.template_name,
                                 model_mapping=app_config.model_mapping,
                                 basic=basic,
                                 snmp=snmp,
                                 options=options, )
    render_config.build_config()


def init():
    init_config = InitConfig()
    init_config.init()


def update_lld_path_name(path_name):
    settings_path, path_name = app_config.update_lld_name(path_name)
    logging.info(f"lld文件名字配置成功{path_name},具体查看配置文件{settings_path}")


def update_lld_path(path):
    settings_path, path = app_config.update_lld_file_path(path)
    logging.info(f"lld文件路径配置成功{path},具体查看配置文件{settings_path}")


def parse_arguments():
    """ 解析命令行参数 """
    parser = argparse.ArgumentParser(
        description='HCS830-Type1-二层组网配置生成工具'
    )

    # 添加子命令解析器
    subparsers = parser.add_subparsers(dest='command')

    # 添加子命令解析器
    subparsers.add_parser('init', help='初始化设备配置文件，初始化完成后根配置文件提修改配置文件')
    subparsers.add_parser('run', help='修改完成配文件后进行生成配置文件')

    # 添加 path 子命令
    parser_path = subparsers.add_parser('lld', help='进行配置LLD相关命令，通过-h查看')
    parser_path.add_argument('--name', type=str,
                             help='指定LLD文件名字，默认采用settings/settings.yaml配文件中的名字，初次使用，配置文件中的名字为None')
    parser_path.add_argument('--file', type=str,
                             help='指定LLD的路径，配置文件中的路径为None，默认通过计算当前工作路径下的data路径+文件名字')

    return parser.parse_args()


def execute_command(args):
    """ 根据命令执行相应的操作 """
    command = args.command

    lld_name = getattr(args, 'name', None)
    lld_file_path = getattr(args, 'file', None)

    if command == 'init':
        init()
    elif command == 'run':
        run()
    elif command == 'lld':
        if lld_name is not None:
            update_lld_path_name(lld_name)
        elif lld_file_path is not None:
            update_lld_path(lld_file_path)
        else:
            print('未指定 参数 使用-h查看需要指定参数。')
    else:
        print("未知命令，请输入 -h查看命令使用方法")
