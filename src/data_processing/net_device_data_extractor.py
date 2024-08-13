import re
import logging
import numpy as np
import pandas as pd
from src.utils.exceptions import SheetDeletion
from src.models.table_structure import TableArg
from pathlib import Path


class NetDeviceDataExtractor:
    """
    网络设备数据提取器类，用于从特定的文件中提取网络设备数据。

    Attributes:
        __lld_file_path (str): 存储网络设备数据的LLD文件路径。
    """

    def __init__(self, lld_file_path: str):
        """
        初始化网络设备数据提取器类的实例。

        Parameters:
            lld_file_path (str): LLD文件路径，用于提取网络设备数据。
        """
        self.__lld_file_path = lld_file_path

    def __get_excel(self) -> pd.ExcelFile:
        """
        获取Excel文件对象。

        该方法用于创建并返回一个pandas的ExcelFile对象，该对象用于后续读取和处理Excel文件中的数据。

        :return: 返回一个pd.ExcelFile对象，用于操作Excel文件。
        """
        return pd.ExcelFile(self.__lld_file_path)

    def __get_all_sheet(self) -> list:
        """
        获取Excel文件中所有的工作表名称。

        通过调用`__get_excel()`方法获取Excel文件对象，然后返回该对象的`sheet_names`属性，
        其中`sheet_names`是一个包含所有工作表名称的列表。

        :return: 包含所有工作表名称的列表。
        """
        return self.__get_excel().sheet_names

    def __get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """
        根据指定的表单名称，获取Excel中的表单数据并返回为DataFrame对象。

        参数:
        sheet_name (str): 需要获取的表单名称。

        返回:
        pd.DataFrame: 表单数据的DataFrame对象。

        异常:
        SheetDeletion: 如果指定的表单名称不存在于Excel中，抛出SheetDeletion异常。
        """
        # 检查指定的表单名称是否存在于Excel中
        logging.debug(f"尝试获取表单 {sheet_name} 的数据。")
        if sheet_name in self.__get_all_sheet():
            # 如果存在，解析指定的表单并返回其数据
            df = self.__get_excel().parse(sheet_name=sheet_name)
            logging.debug(f"成功获取表单 {sheet_name} 的数据。")
            return df
        else:
            # 如果不存在，抛出SheetDeletion异常
            logging.error(f"表单 {sheet_name} 不存在。")
            raise SheetDeletion(sheet_name)

    @staticmethod
    def __get_max_index(df: pd.DataFrame) -> int:
        """
        获取DataFrame的最大索引值。

        该方法用于确定给定DataFrame的最大索引值，即行数。这对于在操作DataFrame时确定数据的范围很有用。

        参数:
        data_frame (pd.DataFrame): 一个pandas的DataFrame对象，包含待处理的数据。

        返回:
        int: DataFrame的最大索引值（行数）。
        """
        # 计算并返回DataFrame的行数作为最大索引值
        max_index = len(df)
        return max_index

    @staticmethod
    def __get_excel_index(index: str, sheet: pd.DataFrame):
        """
        根据指定索引获取Excel中数据开始的行索引。

        该方法用于在数据表中查找给定索引对应的第一行的位置。这对于处理具有不规则起始行的数据表特别有用，
        例如，当数据表的开头几行可能是标题或空行时。

        参数:
        index: str - 要查找的索引字符串。
        sheet: pd.DataFrame - 包含数据的DataFrame对象。

        返回:
        int - 数据开始的行索引。

        示例:
        假设DataFrame的前两行为标题，第三行包含索引字符串，则调用此方法将返回2。
        """
        logging.debug(f"开始查找索引 {index} 在表单中的位置。")
        # 使用apply方法结合正则表达式在DataFrame的每一行中搜索索引字符串
        start_row = sheet[
            sheet.apply(lambda row: row.astype(str).str.contains(index).any(),
                        axis=1)]
        # 获取包含索引字符串的第一行的索引位置
        try:
            start_row_index = start_row.index.tolist()[0]
            logging.debug(f"找到索引 {index} 对应的位置：{start_row_index}。")
            return start_row_index
        except IndexError:
            logging.error(f"未能找到索引 {index}。")
            raise ValueError(f"索引 {index} 未在表单中找到。")

    def __slice_table(self, start_row: str, end_id: str, sheet: pd.DataFrame):
        """
        根据指定的起始行和结束ID切片表格。

        参数:
        - start_row: str, 切片的起始行标识。
        - end_id: str, 切片的结束ID标识。
        - sheet: pd.DataFrame, 待切片的DataFrame对象。

        返回:
        切片后的DataFrame对象。
        """
        logging.debug(f"开始切片表格，起始行标识为 {start_row}，结束ID标识为 {end_id}。")
        # 如果起始行和结束ID都未指定，直接返回表格的副本
        if start_row is None and end_id is None:
            logging.debug("起始行和结束ID均未指定，直接返回表格副本。")
            return sheet.copy()

        # 获取起始行的索引位置，并将其转换为Excel中的行号（从1开始）
        start_row_index = self.__get_excel_index(index=start_row, sheet=sheet)
        start_row_index += 1
        logging.debug(f"确定起始行索引为 {start_row_index}。")

        # 如果结束ID未指定，根据起始行索引和表格的最大索引进行切片
        if end_id is None:
            end_row = self.__get_max_index(df=sheet)
            logging.debug(f"确定结束行索引为 {end_row}。")
            # 如果起始行索引和结束行索引相同，则创建一个仅含一条记录的DataFrame并返回
            if (start_row_index + 1) == end_row:
                columns = sheet.iloc[start_row_index].dropna()
                df = pd.DataFrame([columns])
                df.loc[0] = '-'
                logging.debug("创建了一个仅含一条记录的DataFrame。")
                return df.copy()
            logging.debug("根据起始行索引和结束行索引进行切片。")
            return sheet[start_row_index:end_row].copy()

        # 获取结束行的索引位置，并进行切片
        end_row_index = self.__get_excel_index(index=end_id, sheet=sheet)
        logging.debug(f"确定结束行索引为 {end_row_index}。")
        slice_data = sheet[start_row_index:end_row_index]
        logging.debug("根据起始行索引和结束行索引进行了切片。")
        return slice_data.copy()

    @staticmethod
    def __set_snmp_v2_config(df: pd.DataFrame):
        """
        设置SNMPv2配置信息到给定的DataFrame中。

        该方法首先检查给定DataFrame的倒数第一列是否为'端口'，如果不是，则不进行任何操作并返回。
        如果是'端口'，则在DataFrame中添加读团体字和写团体字的列。

        参数:
        data_frame (pd.DataFrame): 包含SNMP配置信息的DataFrame。

        返回:
        无返回值。该方法直接在输入的DataFrame上修改。
        """
        # 检查是否达到添加SNMP配置的条件
        if df.iloc[1, -1] != '端口':
            return

        # 计算DataFrame的行数，用于后续生成序列
        num_rows = len(df)

        # 创建读团体字和写团体字的序列
        Read_community = pd.Series(['SNMP信息', '读团体字'] + ['-'] * (num_rows - 2), index=df.index)
        Write_community = pd.Series(['SNMP信息', '写团体字'] + ['-'] * (num_rows - 2), index=df.index)

        # 获取最后一列的列名，用于生成新的列名
        last_column_name = df.columns[-1]
        column_name, last_number = last_column_name.split(": ")

        # 根据现有的列名和数字生成读写团体字的新列名
        Read_community_name = f'{column_name}: {int(last_number) + 1}'
        Write_community_name = f'{column_name}: {int(last_number) + 2}'

        # 将读写团体字的列添加到DataFrame中
        df[Read_community_name] = Read_community
        df[Write_community_name] = Write_community

    @staticmethod
    def __set_df_nan_to_string(df: pd.DataFrame):
        """
        将DataFrame中的NaN值转换为字符串"-"

        该方法首先筛选出DataFrame中的所有数值型列，然后将这些列的数据类型转换为对象类型（字符串），
        最后将所有的NaN值填充为字符串"-"

        参数:
        data_frame: pd.DataFrame - 需要进行处理的DataFrame

        返回:
        无 - 该方法直接修改传入的DataFrame，不返回任何值
        """
        # 筛选DataFrame中的数值型列
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        # 将数值型列的数据类型转换为对象类型（字符串）
        df[numeric_cols] = df[numeric_cols].astype('object')
        # 将所有的NaN值填充为字符串"-"
        df.fillna('-', inplace=True)

    @staticmethod
    def __set_data_drop_all_NaN(df: pd.DataFrame):
        """
        静态方法：删除DataFrame中所有NaN值的列和行。

        参数:
        data_frame (pd.DataFrame): 输入的DataFrame对象。

        返回:
        无直接返回值，该方法直接在传入的DataFrame上进行操作。
        """
        # 删除包含所有NaN值的所有列
        df.dropna(axis='columns', how='all', inplace=True)
        # 删除包含所有NaN值的所有行
        df.dropna(axis='index', how='all', inplace=True)

    @staticmethod
    def __initialize_nulls_with_first_row_values(df: pd.DataFrame):
        """
        使用第一行的值来初始化空值

        当数据框的第二行中存在空值时，此方法使用第一行的相应值来填充这些空值。
        如果数据框少于两行，则不执行任何操作。

        参数:
        data_frame (pd.DataFrame): 需要初始化空值的数据框
        """
        # 获取数据框的起始和结束索引，以确定是否有足够的数据行进行处理
        start_index = df.index.min()
        max_index = df.index.max()
        # 如果数据框只有一行，则无需初始化空值，直接返回
        if max_index == start_index:
            return None

        # 使用前向填充方法用第一行的值初始化第一行的空值
        df.iloc[0] = df.iloc[0].ffill()
        # 识别第二行中的空值列
        second_row_is_null = df.iloc[1].isnull()
        columns_with_null = second_row_is_null[second_row_is_null].index

        # 遍历空值列，并用第一行的值填充空值
        for col in columns_with_null:
            df.loc[:, col] = df[col].fillna(df[col].iloc[0])

    @staticmethod
    def __save_df_slice_as_excel_overwrite_or_create(df: pd.DataFrame, file_name: Path, slice_index: int, header: bool):
        """
        将DataFrame的一部分保存为Excel文件，如果文件已存在，则覆盖或创建新文件。

        参数:
        data_frame: pd.DataFrame - 要保存的DataFrame。
        file_name: Path - 保存文件的路径。
        slice_index: int - 从DataFrame的哪个索引开始切片。
        header: bool - 写入Excel文件时是否包含列名。

        返回:
        无返回值，此函数会打印操作状态。
        """
        # 检查目标文件是否存在
        if file_name.is_file():
            # 如果文件存在，则删除原有文件
            file_name.unlink()
            logging.info(f'文件 {file_name} 已被删除。')
            # 将DataFrame的指定部分保存为Excel文件
            df.iloc[slice_index:].to_excel(str(file_name), header=header, index=False)
            logging.info(f'文件 {file_name} 创建成功。')
        else:
            # 如果文件不存在，检查父目录是否存在
            if file_name.parent.exists():
                # 如果父目录存在，则将DataFrame的指定部分保存为Excel文件
                df.iloc[slice_index:].to_excel(str(file_name), header=header, index=False)
                logging.info(f'文件 {file_name} 创建成功。')
            else:
                # 如果父目录不存在，则抛出文件路径错误的异常
                raise FileNotFoundError(f"传入路径信息有误 '{file_name}'")

    def __prepare_and_save_table_slice_to_excel(self, table_arg: TableArg) -> str:
        """
        根据传入的TableArg对象准备并保存表格切片到Excel文件中。

        :param table_arg: TableArg对象，包含表格切片的参数信息
        :type table_arg: TableArg
        :return: 保存的Excel文件的路径
        :rtype: str
        """
        # 根据表名获取工作表
        sheet = self.__get_sheet(sheet_name=table_arg.sheet_name)
        # 切割表格，获取指定行范围的数据框
        df = self.__slice_table(start_row=table_arg.start_id, sheet=sheet, end_id=table_arg.end_id)

        # 如果起始行和结束行都未指定，则进行特殊处理并保存整个数据框到Excel
        if table_arg.start_id is None and table_arg.end_id is None:
            self.__set_df_nan_to_string(df=df)  # 将数据框中的NaN值转换为字符串
            self.__set_data_drop_all_NaN(df=df)  # 删除数据框中所有NaN值
            # 定义文件名并保存数据框为Excel文件
            file_name = Path(table_arg.data_path).joinpath(f'{table_arg.sheet_name}.xlsx')
            self.__save_df_slice_as_excel_overwrite_or_create(df=df, file_name=file_name,
                                                              slice_index=table_arg.slice_index,
                                                              header=True)
            return str(file_name)

        # 删除数据框中所有NaN值
        self.__set_data_drop_all_NaN(df=df)
        # 用第一行的值初始化空值
        self.__initialize_nulls_with_first_row_values(df=df)
        # 如果指定了起始行且起始行值以"管理信息"结尾，则设置SNMP v2配置
        if table_arg.start_id is not None and re.search(r'.*管理信息$', table_arg.start_id):
            self.__set_snmp_v2_config(df=df)

        # 定义文件名并保存数据框为Excel文件，不包含表头
        file_name = Path(table_arg.data_path).joinpath(f'{table_arg.start_id}.xlsx')
        self.__save_df_slice_as_excel_overwrite_or_create(df=df, file_name=file_name, slice_index=table_arg.slice_index,
                                                          header=False)
        return str(file_name)

    def load_processed_df_from_excel(self, table_arg: TableArg, ):
        """
        从Excel文件中加载处理后的数据框架。

        该方法首先准备并保存一个表格片段到Excel文件中，然后从该文件中读取数据。
        主要用于在需要将数据处理结果保存为Excel文件并重新加载的场景。

        参数:
        - table_arg: TableArg类型，指定需要处理的表格参数。

        返回:
        - 读取Excel文件得到的数据框架。
        """
        # 准备并保存表格片段到Excel文件中，返回文件名
        file_name = self.__prepare_and_save_table_slice_to_excel(table_arg=table_arg)
        # 使用pandas从Excel文件中读取数据
        result = pd.read_excel(file_name)
        # 返回读取的数据框架
        return result


