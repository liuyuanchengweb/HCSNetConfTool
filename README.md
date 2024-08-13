# HCS配置生成工具
## 介绍
 基于HUAWEI CLOUD Stack Designer工具生成的LLD模板进行生成对应的网络设备配置文。
## 支持
 - HCS 830 type1 二层组网架构
 - HCS 831 type1 二层组网架构
## 后续支持
 - HCS 830 type1 三层组网架构
 - HCS 831 type1 三层组网架构
## 使用方法
1. 下载HCS配置生成工具

   - git方式（二次开发推荐）

   git clone https://github.com/liuyuanchengweb/HCSNetConfTool.git

   git clone https://gitee.com/useryc/HCSNetConfTool.git
   - 压缩包下载（有python环境，熟悉环境配置和依赖管理推荐）
   https://gitee.com/useryc/HCSNetConfTool/repository/archive/main.zip

   - 打包文件下载（无python环境推荐）

     https://github.com/liuyuanchengweb/HCSNetConfTool/releases/tag/v0.1.0

     https://gitee.com/useryc/HCSNetConfTool/releases/tag/v0.1.0

2. 安装Python环境

   参考官网：https://docs.python.org/zh-cn/3.11/using/index.html

3. 安装依赖

   poetry方式：

   ```bash
   # 首先安装poetry
   # 安装pipx
   python -m pip install --user pipx -i https://pypi.tuna.tsinghua.edu.cn/simple
   # pipx刷新到系统变量中
   python -m pipx ensurepath
   #
   # 打开新的界面使用pipx安装poetry
   # 安装poetry
   pipx install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple
   # 确认poetry是否正常安装以及版本是否小于1.4.0
   poetry -V
   # 安装依赖
   poetry install
   # 安装完依赖后运行程序，如果.py文件默认是python解释器打开方式，直接使用以下方式
   poetry run run.py
   # 如果.py文件默认打卡方式是其他的方式
   poetry shell
   poetry run python run.py
   ```

   虚拟环境方式：

   ```bash
   # 进入到目录，查看文件，使用dir命令，确认文件夹下存在requirements.txt文件，以及项目的其他文件
   dir
   # 安装虚拟环境，执行命令完成后会在文件夹内生产一个venv的文件夹，如果没有生成查找venv相关文档查看
   python -m venv venv
   # 激活虚拟环境，该命令的意思执行venv文件夹下Scripts文件下的activate文件，激活虚拟环境后目录前方会被括号括住
   venv\Scripts\activate
   # 激活虚拟环境后的状态
   # (venv) C:\Users\10464\Desktop\test\simple_network_inspection_tool>
   # 更新pip库，在虚拟环境下执行
   python -m pip install --upgrade pip
   # 执行依赖安装，在虚拟环境下执行国内会存在下载比较慢的情况，可以在后面加 -i 国内源
   pip install -r requirements.txt
   # 安装完成后即可运行，在运行文件的时候存在两种情况，一种是py文件的默认打开方式为python解释器，可以直接在虚拟环境下运行
   run.py
   # 另外一种是.py文件的默认打开方式为编辑器时，需要使用python解释器执行
   venv\Scripts\python.exe run.py
   #
   ```

4. 指定LLD文件路径

   指定LLD文件路径有两种方式

   - 直接修改配置文件方式

     ```yaml
     # 如果文件在data下，修改LLD_FILE_NAME就可以（推荐）
     # 如果文件没在data下，修改LLD_FILE，填写完整路径
     DATA_DIR: data
     LLD_FILE: null
     LLD_FILE_NAME: "hcs830lld\u6A21\u677F.xlsx"
     LOGS_DIR: logs
     SAVE_CONFIG_DIR: save_config
     SETTINGS_DIR: settings
     TEMPLATES_DIR: templates
     model_mapping:
       CE168: CE168XX
       CE68: CE68XX
       S57: S57XX
     template_name:
       CE168XX: CE68or168.jinja2
       CE68XX: CE68or168.jinja2
       S57XX: S57XX.jinja2
       default: base.jinja2
     ```

   - 命令行指定
     ```bash
     (create-dc-sw-config-py3.11) D:\home\py\HCSNetConfTool>python main.py lld --name hcs830lld模板.xlsx
     2024-08-13 22:22:50,999|INFO|command|update_lld_path_name|33|lld文件名字配置成功hcs830lld模板.xlsx,具体查看配置文件D:\home\py\HCSNetConfTool\settings\settings.yaml
     # 或者指定路径
     (create-dc-sw-config-py3.11) D:\home\py\HCSNetConfTool>python main.py lld --file D:\home\py\HCSNetConfTool\data\hcs830lld模板.xlsx
     2024-08-13 22:23:58,934|INFO|command|update_lld_path|38|lld文件路径配置成功D:\home\py\HCSNetConfTool\data\hcs830lld模板.xlsx,具体查看配置文件D:\home\py\HCSNetConfTool\settings\settings.yaml
     ```

5. 初始化配置，生成设备配置所需要的配置文件，修改配置文件

   初始化配置说明，初始化配置会生成一个yaml配置文件，用于补充LLD表格中没有的一些数据，以及控制生成配置的设备。

   ```bash
   (create-dc-sw-config-py3.11) D:\home\py\HCSNetConfTool>python main.py init
   2024-08-13 22:27:01,904|INFO|net_device_data_extractor|__save_df_slice_as_excel_overwrite_or_create|286|文件 D:\home\py\HCSNetConfTool\data\2、网络&存储设备管理信息.xlsx 已被删除。
   2024-08-13 22:27:01,920|INFO|net_device_data_extractor|__save_df_slice_as_excel_overwrite_or_create|289|文件 D:\home\py\HCSNetConfTool\data\2、网络&存储设备管理信息.xlsx 创建成功。
   2024-08-13 22:27:01,989|INFO|init_config|init|81|初始化完成，请查看修改D:\home\py\HCSNetConfTool\settings\DevConfig.yaml配置文件，修改完成后使用 run执行生成配置文件
   
   ```

   

6. 执行生成配置文件

   ```bash
   python main.py run
   ```

   
